from datetime import datetime
from typing import Dict, Any, List
from taskiq import TaskiqDepends, Context
from models import get_customer, get_chat, get_message, get_notification_config, get_task
from config.settings import settings
from bson import ObjectId

from worker import broker

@broker.task
async def send_notification_task(
    customer_ids: List[str],
    notification_config_id: str,
    data: Dict[str, Any],
    user_id: str,
    context: Context = TaskiqDepends(),
) -> Dict[str, Any]:
    """
    Background task to send notifications to customers via chat.
    
    Args:
        customer_ids: List of customer IDs or ["all"] for all customers
        notification_config_id: ID of notification config template
        data: Dynamic data for template rendering
        user_id: ID of user who initiated notification
        task: TaskIQ task dependency
    """
    # Get task record
    Task = get_task()
    task_obj = await Task.find_one({"job_id": context.message.task_id})
    if not task_obj:
        raise Exception(f"Task {context.message.task_id} not found")
    
    try:
        # Update task status to running
        task_obj.status = "running"
        task_obj.started_at = datetime.now()
        await task_obj.commit()
        
        # Get notification config
        NotificationConfig = get_notification_config()
        config = await NotificationConfig.find_one({"_id": ObjectId(notification_config_id)})
        if not config:
            raise Exception(f"Notification config {notification_config_id} not found")
        
        # Get customers to notify
        Customer = get_customer()
        if customer_ids == ["all"]:
            customers = await Customer.find({"is_active": True}).to_list()
        else:
            customers = await Customer.find({"_id": {"$in": [ObjectId(customer_id) for customer_id in customer_ids]}}).to_list(length=len(customer_ids))
        
        task_obj.total_items = len(customers)
        await task_obj.commit()
        
        print(f"[TASK] Sending chat notifications to {len(customers)} customers")
        
        # Process each customer
        for index, customer in enumerate(customers):
            try:
                # Get or create chat session
                chat = await get_or_create_chat_session(str(customer.id))
                
                # Render notification content
                notification_content = config.body_template.format(**data, **{
                    "customer_name": customer.full_name,
                    "customer_email": customer.email,
                    "company": customer.company or "FTEL"
                })
                
                # Create system message in chat
                success = await create_chat_notification(
                    chat_id=ObjectId(chat.id),
                    customer_id=str(customer.id),
                    content=notification_content,
                    notification_config_id=notification_config_id,
                    data=data
                )
                
                if success:
                    task_obj.processed_items += 1
                    print(f"[TASK] Sent chat notification to: {customer.email}")
                else:
                    task_obj.failed_items += 1
                    print(f"[TASK] Failed to send chat notification to: {customer.email}")
                
            except Exception as e:
                task_obj.failed_items += 1
                print(f"[TASK] Error sending to {customer.email}: {str(e)}")
            
            # Update progress every 5 customers
            if (index + 1) % 5 == 0:
                task_obj.progress = (index + 1) / len(customers)
                await task_obj.commit()
                print(f"[TASK] Progress: {task_obj.progress:.2%}")
        
        # Final progress update
        task_obj.progress = 1.0
        task_obj.status = "completed"
        task_obj.completed_at = datetime.now()
        await task_obj.commit()
        
        result = {
            "status": "completed",
            "total_customers": len(customers),
            "sent": task_obj.processed_items,
            "failed": task_obj.failed_items,
            "success_rate": f"{(task_obj.processed_items / len(customers)) * 100:.1f}%"
        }
        
        task_obj.result = result
        await task_obj.commit()
        
        print(f"[TASK] Chat notification sending completed: {result}")
        return result
        
    except Exception as e:
        # Update task status to failed
        task_obj.status = "failed"
        task_obj.error_message = str(e)
        task_obj.completed_at = datetime.now()
        await task_obj.commit()
        
        print(f"[TASK] Chat notification sending failed: {str(e)}")
        raise


async def get_or_create_chat_session(customer_id: str):
    """
    Get existing active chat session or create new one for customer.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Chat: Active chat session
    """
    Chat = get_chat()   
    # Try to find existing active session
    chat = await Chat.find_one({
        "customer": customer_id,
        "is_active": True
    })
    
    if chat:
        return chat
    
    # Create new chat session
    import uuid
    Chat = get_chat()
    chat = Chat(
        customer=customer_id,
        session_id=str(uuid.uuid4()),
        is_active=True
    )
    await chat.commit()
    
    print(f"[TASK] Created new chat session for customer: {customer_id}")
    return chat


async def create_chat_notification(
    chat_id: str,
    customer_id: str,
    content: str,
    notification_config_id: str,
    data: Dict[str, Any]
) -> bool:
    """
    Create a system notification message in chat.
    
    Args:
        chat_id: Chat session ID
        customer_id: Customer ID
        content: Notification content
        notification_config_id: Notification config ID
        data: Template data
        
    Returns:
        bool: True if created successfully, False otherwise
    """
    try:
        # Create system message
        Message = get_message()
        message = Message(
            chat=chat_id,
            customer=customer_id,
            content=content,
            role="assistant",  # Show as bot message
            message_type="system",  # System notification
            metadata={
                "notification_config_id": notification_config_id,
                "notification_data": data,
                "is_system_notification": True,
                "created_at": datetime.now().isoformat()
            }
        )
        await message.commit()
        
        print(f"[TASK] Created system notification message: {message.id}")
        return True
        
    except Exception as e:
        print(f"[TASK] Error creating chat notification: {str(e)}")
        return False 
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import get_user, get_customer, get_chat, get_message
from services.auth import get_current_active_user
from services.ai_chatbot import ai_chatbot
from services.memory_manager import memory_manager

from bson import ObjectId


import uuid

router = APIRouter(prefix="/messages", tags=["Messages"])


class MessageRequest(BaseModel):
    customer_id: str
    content: str
    message_type: str = "user"  # user, system


class MessageResponse(BaseModel):
    id: str
    content: str
    role: str
    message_type: str
    created_at: str
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    session_id: str
    customer_id: str
    messages: List[MessageResponse]


@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageRequest,
    current_user = Depends(get_current_active_user)
):
    """Send message to AI chatbot and get response."""
    Customer = get_customer()
    Chat = get_chat()
    Message = get_message()
    
    # Get or create chat session
    customer = await Customer.find_one({"_id": ObjectId(message_data.customer_id)})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get active chat session or create new one
    chat = await Chat.find_one({
        "customer": ObjectId(message_data.customer_id),
        "is_active": True
    })
    
    if not chat:
        chat = Chat(
            customer=ObjectId(message_data.customer_id),
            session_id=str(uuid.uuid4()),
            is_active=True
        )
        await chat.commit()
    
    # Save user message to database
    user_message = Message(
        chat=str(chat.id),
        customer=ObjectId(message_data.customer_id),
        content=message_data.content,
        role="user",
        message_type="user"
    )
    await user_message.commit()
    
    # Get customer info for context
    customer_info = {
        "full_name": customer.full_name,
        "email": customer.email,
        "company": customer.company
    }
    
    # Generate AI response
    ai_response_data = await ai_chatbot.generate_response(
        customer_id=message_data.customer_id,
        message=message_data.content,
        customer_info=customer_info
    )
    
    # Save AI response to database
    ai_message = Message(
        chat=str(chat.id),
        customer=ObjectId(message_data.customer_id),
        content=ai_response_data["content"],
        role="assistant",
        message_type="ai",
        model_used=ai_response_data.get("model_used"),
        response_time=ai_response_data.get("response_time"),
        metadata=ai_response_data.get("metadata", {})
    )
    await ai_message.commit()
    
    # Update memory
    await ai_chatbot.update_memory(
        customer_id=ObjectId(message_data.customer_id),
        user_message=message_data.content,
        ai_response=ai_response_data
    )
    
    return MessageResponse(
        id=str(ai_message.id),
        content=ai_response_data["content"],
        role="assistant",
        message_type="ai",
        created_at=ai_message.created_at.isoformat()
    )


@router.get("/history")
async def get_message_history(
    customer_id: str,
    limit: int = 50,
    message_type: Optional[str] = None,
    current_user = Depends(get_current_active_user)
):
    """Get message history for a customer."""
    Customer = get_customer()
    Message = get_message()
    
    customer = await Customer.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    query = {"customer": ObjectId(customer_id)}
    if message_type:
        query["message_type"] = message_type
    
    messages = await Message.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return [
        MessageResponse(
            id=str(msg.id),
            content=msg.content,
            role=msg.role,
            message_type=msg.message_type,
            created_at=msg.created_at.isoformat(),
            metadata=msg.metadata
        )
        for msg in reversed(messages)  # Oldest first
    ]


@router.get("/memory/stats")
async def get_memory_stats(
    customer_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get memory statistics for a customer."""
    stats = await memory_manager.get_memory_stats(customer_id)
    return stats


@router.get("/notifications/context")
async def get_notification_context(
    customer_id: str,
    limit: int = 10,
    current_user = Depends(get_current_active_user)
):
    """Get recent notification context for a customer."""
    Customer = get_customer()
    Message = get_message()
    
    customer = await Customer.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get recent system notifications
    notifications = await Message.find({
        "customer": ObjectId(customer_id),
        "message_type": "system"
    }).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(notif.id),
            "content": notif.content,
            "created_at": notif.created_at.isoformat(),
            "metadata": notif.metadata
        }
        for notif in notifications
    ] 
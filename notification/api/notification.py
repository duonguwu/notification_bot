from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
import uuid
import os
from datetime import datetime

from models import get_user, get_customer, get_notification_config, get_message, get_task
from services.auth import get_current_active_user
from tasks.send_notification import send_notification_task
from config.settings import settings

from bson import ObjectId


router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationConfigCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject: str
    body_template: str
    email_template: str
    notification_type: str = "email"


class NotificationConfigResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    subject: str
    body_template: str
    email_template: str
    notification_type: str
    is_active: bool
    created_at: str
    updated_at: str


class NotificationSendRequest(BaseModel):
    customer_ids: Union[List[str], str]  # List of IDs or "all"
    notification_config_id: str
    data: dict = {}  # Dynamic data for template
    notification_type: str = "chat"  # chat, email, or both


class NotificationResponse(BaseModel):
    id: str
    customer_id: str
    config_id: str
    content: str
    message_type: str
    role: str
    created_at: str
    metadata: Optional[dict] = None


@router.post("/config", response_model=NotificationConfigResponse)
async def create_notification_config(
    config_data: NotificationConfigCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new notification configuration template."""
    NotificationConfig = get_notification_config()
    # Check if config with same name exists
    existing = await NotificationConfig.find_one({"name": config_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification config with this name already exists"
        )
    
    config = NotificationConfig(
        name=config_data.name,
        description=config_data.description,
        subject=config_data.subject,
        body_template=config_data.body_template,
        email_template=config_data.email_template,
        notification_type=config_data.notification_type,
        created_by=str(current_user.id)
    )
    await config.commit()
    
    return NotificationConfigResponse(
        id=str(config.id),
        name=config.name,
        description=config.description,
        subject=config.subject,
        body_template=config.body_template,
        email_template=config.email_template,
        notification_type=config.notification_type,
        is_active=config.is_active,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )


@router.get("/config", response_model=List[NotificationConfigResponse])
async def list_notification_configs(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user = Depends(get_current_active_user)
):
    """List notification configurations."""
    NotificationConfig = get_notification_config()
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    
    configs = await NotificationConfig.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        NotificationConfigResponse(
            id=str(config.id),
            name=config.name,
            description=config.description,
            subject=config.subject,
            body_template=config.body_template,
            email_template=config.email_template,
            notification_type=config.notification_type,
            is_active=config.is_active,
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat()
        )
        for config in configs
    ]


@router.get("/config/{config_id}", response_model=NotificationConfigResponse)
async def get_notification_config_by_id(
    config_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get notification configuration by ID."""
    NotificationConfig = get_notification_config()
    config = await NotificationConfig.find_one({"_id": ObjectId(config_id)})
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification config not found"
        )
    
    return NotificationConfigResponse(
        id=str(config.id),
        name=config.name,
        description=config.description,
        subject=config.subject,
        body_template=config.body_template,
        email_template=config.email_template,
        notification_type=config.notification_type,
        is_active=config.is_active,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )


@router.post("/send")
async def send_notification(
    request: NotificationSendRequest,
    current_user = Depends(get_current_active_user)
):
    """Send notification to customers using TaskIQ."""
    NotificationConfig = get_notification_config()
    # Validate notification config
    config = await NotificationConfig.find_one({"_id": ObjectId(request.notification_config_id)})
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification config not found"
        )
    
    if not config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification config is not active"
        )
    
    # Prepare customer IDs
    if request.customer_ids == "all":
        customer_ids = ["all"]
    else:
        # Validate customer IDs
        Customer = get_customer()
        customers = await Customer.find({"_id": {"$in": [ObjectId(customer_id) for customer_id in request.customer_ids]}}).to_list(length=len(request.customer_ids))
        if len(customers) != len(request.customer_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some customer IDs are invalid"
            )
        customer_ids = request.customer_ids
    
    result = await send_notification_task.kiq(
        customer_ids=customer_ids,
        notification_config_id=request.notification_config_id,
        data=request.data,
        user_id=str(current_user.id)
    )
    job_id = result.task_id
    # Create task record
    Task = get_task()
    task = Task(
        job_id=job_id,
        task_name="send_notification",
        status="pending",
        user_id=str(current_user.id),
        parameters={
            "customer_ids": customer_ids,
            "notification_config_id": request.notification_config_id,
            "data": request.data
        }
    )
    await task.commit()
    
    return {
        "message": "Chat notification sending started",
        "job_id": task.job_id,
        "task_id": str(task.id),
        "total_customers": len(customer_ids) if customer_ids != ["all"] else "all",
        "notification_config": config.name,
        "notification_type": "chat"
    }


@router.get("/history", response_model=List[NotificationResponse])
async def get_notification_history(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[str] = None,
    current_user = Depends(get_current_active_user)
):
    """Get chat notification history."""
    Message = get_message()
    query = {"message_type": "system"}
    if customer_id:
        query["customer"] = ObjectId(customer_id)
    
    messages = await Message.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        NotificationResponse(
            id=str(msg.id),
            customer_id=str(msg.customer),
            config_id=msg.metadata.get("notification_config_id", "") if msg.metadata else "",
            content=msg.content,
            message_type=msg.message_type,
            role=msg.role,
            created_at=msg.created_at.isoformat(),
            metadata=msg.metadata
        )
        for msg in messages
    ]


@router.get("/stats")
async def get_notification_stats(
    current_user = Depends(get_current_active_user)
):
    Message = get_message()
    """Get chat notification statistics."""
    total_notifications = await Message.count_documents({"message_type": "system"})
    
    # Get notifications from last 30 days
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_notifications = await Message.count_documents({
        "message_type": "system",
        "created_at": {"$gte": thirty_days_ago}
    })
    
    return {
        "total_notifications": total_notifications,
        "recent_notifications": recent_notifications,
        "notification_type": "chat"
    } 
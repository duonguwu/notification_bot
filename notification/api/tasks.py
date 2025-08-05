from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from models import get_task
from services.auth import get_current_active_user
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskResponse(BaseModel):
    id: str
    job_id: str
    task_name: str
    status: str
    progress: float
    total_items: int
    processed_items: int
    failed_items: int
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    result: Optional[dict]


class TaskStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    cancelled_tasks: int


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    task_name: Optional[str] = Query(None),
    current_user = Depends(get_current_active_user)
):
    """List all tasks with filtering and pagination."""
    Task = get_task()
    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter
    if task_name:
        query["task_name"] = {"$regex": task_name, "$options": "i"}
    
    tasks = await Task.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        TaskResponse(
            id=str(task.id),
            job_id=task.job_id,
            task_name=task.task_name,
            status=task.status,
            progress=task.progress,
            total_items=task.total_items,
            processed_items=task.processed_items,
            failed_items=task.failed_items,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            error_message=task.error_message,
            result=task.result
        )
        for task in tasks
    ]


@router.get("/{job_id}", response_model=TaskResponse)
async def get_task_by_job_id(
    job_id: str,
    current_user = Depends(get_current_active_user)
):
    Task = get_task()
    """Get task details by job ID."""
    task = await Task.find_one({"job_id": job_id})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=str(task.id),
        job_id=task.job_id,
        task_name=task.task_name,
        status=task.status,
        progress=task.progress,
        total_items=task.total_items,
        processed_items=task.processed_items,
        failed_items=task.failed_items,
        created_at=task.created_at.isoformat(),
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        error_message=task.error_message,
        result=task.result
    )


@router.post("/{job_id}/cancel")
async def cancel_task(
    job_id: str,
    current_user = Depends(get_current_active_user)
):
    Task = get_task()
    """Cancel a running or pending task."""
    task = await Task.find_one({"job_id": job_id})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task with status: {task.status}"
        )
    
    # Update task status
    task.status = "cancelled"
    task.completed_at = datetime.now()
    await task.commit()
    
    return {"message": "Task cancelled successfully", "job_id": job_id}


@router.get("/stats/overview", response_model=TaskStats)
async def get_task_stats(
    current_user = Depends(get_current_active_user)
):
    Task = get_task()
    """Get task statistics overview."""
    # Count tasks by status
    total_tasks = await Task.count_documents({})
    pending_tasks = await Task.count_documents({"status": "pending"})
    running_tasks = await Task.count_documents({"status": "running"})
    completed_tasks = await Task.count_documents({"status": "completed"})
    failed_tasks = await Task.count_documents({"status": "failed"})
    cancelled_tasks = await Task.count_documents({"status": "cancelled"})
    
    return TaskStats(
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        running_tasks=running_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        cancelled_tasks=cancelled_tasks
    )


@router.get("/stats/recent")
async def get_recent_task_stats(
    days: int = Query(7, ge=1, le=30),
    current_user = Depends(get_current_active_user)
):
    Task = get_task()
    """Get recent task statistics."""
    from datetime import timedelta
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get tasks in date range
    recent_tasks = await Task.find({
        "created_at": {"$gte": start_date, "$lte": end_date}
    }).to_list()
    
    # Calculate statistics
    total_recent = len(recent_tasks)
    completed_recent = len([t for t in recent_tasks if t.status == "completed"])
    failed_recent = len([t for t in recent_tasks if t.status == "failed"])
    
    success_rate = (completed_recent / total_recent * 100) if total_recent > 0 else 0
    
    return {
        "period_days": days,
        "total_tasks": total_recent,
        "completed_tasks": completed_recent,
        "failed_tasks": failed_recent,
        "success_rate": f"{success_rate:.1f}%",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    } 
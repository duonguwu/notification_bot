from umongo import Document, fields
from datetime import datetime, UTC
from config.database import get_umongo_instance


class Task(Document):
    """Task/Job tracking for TaskIQ jobs."""
    
    job_id = fields.StrField(required=True, unique=True)
    task_name = fields.StrField(required=True)
    status = fields.StrField(
        required=True
    )  # pending, running, completed, failed, cancelled
    progress = fields.FloatField(default=0.0)  # 0.0 to 1.0
    total_items = fields.IntField(default=0)
    processed_items = fields.IntField(default=0)
    failed_items = fields.IntField(default=0)
    
    # Task metadata
    user_id = fields.ReferenceField("User")
    parameters = fields.DictField(default=dict)
    result = fields.DictField(default=dict)
    error_message = fields.StrField()
    
    # Timing
    created_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    started_at = fields.DateTimeField()
    completed_at = fields.DateTimeField()
    updated_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    
    # Retry info
    retry_count = fields.IntField(default=0)
    max_retries = fields.IntField(default=3)
    
    class Meta:
        collection_name = "tasks"
        indexes = [
            "job_id",
            "task_name",
            "status",
            "user_id",
            "created_at"
        ]
    
    def __str__(self):
        return f"Task({self.task_name} - {self.status})"


# Lazy registration
def get_task_model():
    """Get Task model with database registration."""
    return get_umongo_instance().register(Task) 
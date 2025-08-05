from umongo import Document, fields
from datetime import datetime, UTC
from config.database import get_umongo_instance


class NotificationConfig(Document):
    """Notification configuration template."""
    
    name = fields.StrField(required=True, unique=True)
    description = fields.StrField()
    subject = fields.StrField(required=True)
    body_template = fields.StrField(required=True)
    email_template = fields.StrField(required=True)
    notification_type = fields.StrField(
        required=True
    )  # email, sms, push
    is_active = fields.BoolField(default=True)
    created_by = fields.ReferenceField("User")
    created_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    
    class Meta:
        collection_name = "notification_configs"
        indexes = [
            "name",
            "notification_type",
            "is_active"
        ]
    
    def __str__(self):
        return f"NotificationConfig({self.name})"


class Notification(Document):
    """Notification instance for tracking sent notifications."""
    
    customer = fields.ReferenceField("Customer", required=True)
    config = fields.ReferenceField("NotificationConfig", required=True)
    subject = fields.StrField(required=True)
    body = fields.StrField(required=True)
    status = fields.StrField(
        required=True
    )  # pending, sent, failed
    sent_at = fields.DateTimeField()
    error_message = fields.StrField()
    retry_count = fields.IntField(default=0)
    max_retries = fields.IntField(default=3)
    metadata = fields.DictField(default=dict)
    created_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    
    class Meta:
        collection_name = "notifications"
        indexes = [
            "customer",
            "config", 
            "status",
            "sent_at"
        ]
    
    def __str__(self):
        return f"Notification({self.customer.email} - {self.status})"


# Lazy registration
def get_notification_config_model():
    """Get NotificationConfig model with database registration."""
    return get_umongo_instance().register(NotificationConfig)


def get_notification_model():
    """Get Notification model with database registration."""
    return get_umongo_instance().register(Notification) 
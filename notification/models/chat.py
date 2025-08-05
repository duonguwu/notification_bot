from umongo import Document, fields
from datetime import datetime, UTC
from config.database import get_umongo_instance


class Chat(Document):
    """Chat session between customer and AI."""
    
    customer = fields.ReferenceField("Customer", required=True)
    session_id = fields.StrField(required=True, unique=True)
    is_active = fields.BoolField(default=True)
    started_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    ended_at = fields.DateTimeField()
    metadata = fields.DictField(default=dict)
    
    class Meta:
        collection_name = "chats"
        indexes = [
            "customer",
            "session_id",
            "is_active"
        ]
    
    def __str__(self):
        return f"Chat({self.session_id})"


class Message(Document):
    """Individual message in a chat session."""
    
    chat = fields.ReferenceField("Chat", required=True)
    customer = fields.ReferenceField("Customer", required=True)
    content = fields.StrField(required=True)
    message_type = fields.StrField(
        required=True
    )  # user, ai, system
    role = fields.StrField(required=True)  # user, assistant, system
    tokens_used = fields.IntField()
    model_used = fields.StrField()
    response_time = fields.FloatField()  # in seconds
    metadata = fields.DictField(default=dict)
    created_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    
    class Meta:
        collection_name = "messages"
        indexes = [
            "chat",
            "customer",
            "message_type",
            "created_at"
        ]
    
    def __str__(self):
        return f"Message({self.message_type} - {self.content[:50]}...)"


# Lazy registration
def get_chat_model():
    """Get Chat model with database registration."""
    return get_umongo_instance().register(Chat)


def get_message_model():
    """Get Message model with database registration."""
    return get_umongo_instance().register(Message) 
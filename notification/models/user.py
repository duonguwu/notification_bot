from umongo import Document, fields
from datetime import datetime, UTC
from config.database import get_umongo_instance


class User(Document):
    username = fields.StrField(required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    hashed_password = fields.StrField(required=True)
    full_name = fields.StrField(default="")
    is_active = fields.BoolField(default=True)
    is_superuser = fields.BoolField(default=False)
    created_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    
    class Meta:
        collection_name = "users"
        indexes = [
            "username",
            "email"
        ]
    
    def __str__(self):
        return f"User({self.username})"


# Lazy registration
def get_user_model():
    """Get User model with database registration."""
    return get_umongo_instance().register(User) 
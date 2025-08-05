from umongo import Document, fields
from datetime import datetime, UTC
from config.database import get_umongo_instance


class Customer(Document):
    """Customer model for storing customer information."""
    
    email = fields.EmailField(required=True, unique=True)
    phone = fields.StrField(unique=True)
    full_name = fields.StrField(required=True)
    company = fields.StrField()
    position = fields.StrField()
    address = fields.StrField()
    city = fields.StrField()
    country = fields.StrField()
    language = fields.StrField(default="vi")
    is_active = fields.BoolField(default=True)
    tags = fields.ListField(fields.StrField(), default=list)
    metadata = fields.DictField(default=dict)
    created_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = fields.DateTimeField(default=lambda: datetime.now(UTC))
    
    class Meta:
        collection_name = "customers"
        indexes = [
            "email",
            "phone",
            "company",
            "tags"
        ]
    
    def __str__(self):
        return f"Customer({self.email})"


# Lazy registration
def get_customer_model():
    """Get Customer model with database registration."""
    return get_umongo_instance().register(Customer) 
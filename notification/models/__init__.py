"""
Model registry for lazy loading and database registration.
"""

from .user import User, get_user_model
from .customer import Customer, get_customer_model
from .notification import (
    NotificationConfig, 
    Notification, 
    get_notification_config_model,
    get_notification_model
)
from .chat import Chat, Message, get_chat_model, get_message_model
from .task import Task, get_task_model


class ModelRegistry:
    """Registry for all models with lazy registration."""
    
    def __init__(self):
        self._models = {}
        self._registered = False
    
    def register_all(self):
        """Register all models with database."""
        if self._registered:
            return
        
        # Register models in dependency order
        self._models['User'] = get_user_model()
        self._models['Customer'] = get_customer_model()
        self._models['NotificationConfig'] = get_notification_config_model()
        self._models['Notification'] = get_notification_model()
        self._models['Chat'] = get_chat_model()
        self._models['Message'] = get_message_model()
        self._models['Task'] = get_task_model()
        
        self._registered = True
        print("All models registered successfully!")
    
    def get_model(self, name: str):
        """Get registered model by name."""
        if not self._registered:
            self.register_all()
        return self._models.get(name)
    
    def get_all_models(self):
        """Get all registered models."""
        if not self._registered:
            self.register_all()
        return self._models


# Global registry instance
registry = ModelRegistry()


# Convenience functions
def get_user():
    """Get User model."""
    return registry.get_model('User')


def get_customer():
    """Get Customer model."""
    return registry.get_model('Customer')


def get_notification_config():
    """Get NotificationConfig model."""
    return registry.get_model('NotificationConfig')


def get_notification():
    """Get Notification model."""
    return registry.get_model('Notification')


def get_chat():
    """Get Chat model."""
    return registry.get_model('Chat')


def get_message():
    """Get Message model."""
    return registry.get_model('Message')


def get_task():
    """Get Task model."""
    return registry.get_model('Task')


def register_all_models():
    """Register all models with database."""
    registry.register_all() 
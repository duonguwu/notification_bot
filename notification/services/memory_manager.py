import json
from typing import List, Dict, Any
from config.database import get_redis
from config.settings import settings
from models import get_message
from bson import ObjectId


class MemoryManager:
    """Manage short-term (Redis) and long-term (MongoDB) memory."""
    
    def __init__(self):
        self._redis = None
        self.short_term_ttl = settings.short_term_memory_ttl
    
    @property
    def redis(self):
        """Lazy initialization of Redis connection."""
        if self._redis is None:
            self._redis = get_redis()
        return self._redis
    
    async def get_short_term_memory(
        self, customer_id: str
    ) -> List[Dict[str, Any]]:
        """Get short-term memory from Redis."""
        try:
            key = f"memory:short:{customer_id}"
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return []
        except Exception:
            return []
    
    async def set_short_term_memory(
        self, customer_id: str, messages: List[Dict[str, Any]]
    ):
        """Set short-term memory in Redis."""
        try:
            key = f"memory:short:{customer_id}"
            # Keep only recent messages
            recent_messages = messages[-settings.max_conversation_history:]
            await self.redis.setex(
                key, self.short_term_ttl, json.dumps(recent_messages)
            )
        except Exception:
            pass
    
    async def add_to_short_term_memory(
        self, customer_id: str, message: Dict[str, Any]
    ):
        """Add message to short-term memory."""
        try:
            current_memory = await self.get_short_term_memory(customer_id)
            current_memory.append(message)
            await self.set_short_term_memory(customer_id, current_memory)
        except Exception:
            pass
    
    async def get_long_term_memory(
        self, customer_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get long-term memory from MongoDB."""
        try:
            Message = get_message()
            # Get recent messages from database
            messages = await Message.find(
                {"customer": ObjectId(customer_id)}
            ).sort("created_at", -1).limit(limit).to_list(length=limit)
            
            # Convert to dict format
            memory = []
            for msg in reversed(messages):  # Oldest first
                memory.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "message_type": msg.message_type
                })
            
            return memory
        except Exception:
            return []
    
    async def add_to_long_term_memory(
        self, customer_id: str, chat_id: str, message: Dict[str, Any]
    ):
        """Add message to long-term memory (MongoDB)."""
        try:
            # Create message record
            Message = get_message()
            msg = Message(
                chat=chat_id,
                customer=customer_id,
                content=message["content"],
                role=message["role"],
                message_type=message.get("message_type", "user"),
                tokens_used=message.get("tokens_used"),
                model_used=message.get("model_used"),
                response_time=message.get("response_time"),
                metadata=message.get("metadata", {})
            )
            await msg.commit()
        except Exception:
            pass

    async def get_recent_notifications(
        self, customer_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent 'system' messages (notification) for a customer from MongoDB."""
        try:
            Message = get_message()
            messages = await Message.find(
                {"customer": ObjectId(customer_id), "message_type": "system"}
            ).sort("created_at", -1).limit(limit).to_list(length=limit)
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "message_type": msg.message_type
                }
                for msg in reversed(messages)
            ]
        except Exception:
            return []

    async def get_combined_memory(
        self, customer_id: str, short_term_limit: int = 10, conversation_limit: int = 30, notification_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Lấy short-term (chat gần nhất), long-term (history hội thoại), VÀ notification (system message gần nhất)
        """
        # Short-term chứa cả user và ai
        short_term = await self.get_short_term_memory(customer_id)
        
        # Long-term chỉ lấy message user/ai (không lấy system)
        long_term = await self.get_long_term_memory(customer_id, limit=conversation_limit)
        
        # Notification là 10 cái system gần nhất
        notifications = await self.get_recent_notifications(customer_id, limit=notification_limit)
        # Gộp lại, loại trùng (dựa trên content + type + timestamp)
        combined = short_term[-short_term_limit:] + notifications + long_term

        seen = set()
        unique_memory = []
        for msg in combined:
            key = f"{msg['content']}_{msg.get('timestamp')}_{msg.get('message_type')}"
            if key not in seen:
                seen.add(key)
                unique_memory.append(msg)
        return unique_memory

    
    async def clear_short_term_memory(self, customer_id: str):
        """Clear short-term memory for a customer."""
        try:
            key = f"memory:short:{customer_id}"
            await self.redis.delete(key)
        except Exception:
            pass
    
    async def get_memory_stats(self, customer_id: str) -> Dict[str, Any]:
        """Get memory statistics for a customer."""
        try:
            short_term = await self.get_short_term_memory(customer_id)
            long_term_count = await Message.count_documents(
                {"customer": customer_id}
            )
            
            return {
                "short_term_count": len(short_term),
                "long_term_count": long_term_count,
                "total_memory": len(short_term) + long_term_count
            }
        except Exception:
            return {
                "short_term_count": 0,
                "long_term_count": 0,
                "total_memory": 0
            }


# Global memory manager instance
memory_manager = MemoryManager() 
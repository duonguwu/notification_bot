import time
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
from services.memory_manager import memory_manager
from prompts.system_prompt import build_system_prompt 

class AIChatbot:
    """AI Chatbot service using Google Gemini and Langchain."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.1,
                max_output_tokens=1024
            )
        return self._model

    async def generate_response(
        self,
        customer_id: str,
        message: str,
        customer_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()

        try:
            memory = await memory_manager.get_combined_memory(customer_id)
            context, recent_notifications = self._build_context_and_notifs(memory, customer_info)
            messages = self._create_messages(context, message, recent_notifications)
            response = await self.model.ainvoke(messages)
            ai_response = response.content if hasattr(response, "content") else str(response)
            response_time = time.time() - start_time
            response_data = {
                "content": ai_response,
                "role": "assistant",
                "message_type": "ai",
                "response_time": response_time,
                "model_used": settings.gemini_model,
                "metadata": {
                    "memory_count": len(memory),
                    "customer_info": customer_info
                }
            }
            return response_data
        except Exception as e:
            print("[AIChatbot Exception]:", e)
            return {
                "content": "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
                "role": "assistant",
                "message_type": "ai",
                "response_time": time.time() - start_time,
                "model_used": settings.gemini_model,
                "error": str(e)
            }

    def _build_context_and_notifs(
        self,
        memory: List[Dict[str, Any]],
        customer_info: Optional[Dict[str, Any]] = None
    ) -> (str, list):
        context_parts = []
        # Add customer info if available
        if customer_info:
            customer_context = f"Khách hàng: {customer_info.get('full_name', 'Unknown')}"
            if customer_info.get('company'):
                customer_context += f" từ {customer_info['company']}"
            context_parts.append(customer_context)
        # Add recent notifications context
        recent_notifications = [msg['content'] for msg in memory if msg.get("message_type") == "system"]
        print("recent_notifications: ", recent_notifications)
        if recent_notifications:
            context_parts.append("Thông báo gần đây:")
            for notif in recent_notifications[-3:]:
                context_parts.append(f"{notif}")
        # Add conversation history
        regular_messages = [msg for msg in memory if msg.get("message_type") != "system"]
        if regular_messages:
            context_parts.append("Lịch sử hội thoại gần đây:")
            for msg in regular_messages[-10:]:
                role = "Khách hàng" if msg["role"] == "user" else "Bot"
                context_parts.append(f"{role}: {msg['content']}")
        # Trả về context (text), đồng thời trả về 3 thông báo gần nhất để truyền vào system prompt
        return "\n".join(context_parts), recent_notifications[-3:] if recent_notifications else []

    def _create_messages(self, context: str, user_message: str, notifications: list) -> List:
        # Truyền thông báo vào system prompt (inject thông báo vào đầu cho LLM)
        system_prompt = build_system_prompt(notifications)
        print("system_prompt: ", system_prompt)
        return [
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Context: {context}"),
            HumanMessage(content=user_message)
        ]

    async def update_memory(
        self,
        customer_id: str,
        user_message: str,
        ai_response: Dict[str, Any]
    ):
        user_msg = {
            "role": "user",
            "content": user_message,
            "message_type": "user",
            "timestamp": time.time()
        }
        await memory_manager.add_to_short_term_memory(customer_id, user_msg)
        ai_msg = {
            "role": "assistant",
            "content": ai_response["content"],
            "message_type": "ai",
            "timestamp": time.time(),
            "model_used": ai_response.get("model_used"),
            "response_time": ai_response.get("response_time")
        }
        await memory_manager.add_to_short_term_memory(customer_id, ai_msg)

# Global AI chatbot instance
ai_chatbot = AIChatbot()

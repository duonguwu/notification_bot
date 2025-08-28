# 🚀 AI CHATBOT DEPLOYMENT GUIDE

## 📋 **REQUIREMENTS**

### **Python Dependencies**
```bash
pip install langgraph langchain-google-genai langchain-community
```

### **Environment Variables**
```bash
# Add to your .env or settings
GOOGLE_API_KEY=your_gemini_api_key_here
```

### **Database Requirements**
- ✅ MongoDB (đã có - dùng existing collections)
- ✅ Redis (đã có - dùng existing connection)
- 🚧 Qdrant (optional - cho RAG features)

## 🔧 **DEPLOYMENT STEPS**

### **1. Verify Code Integration**

Check rằng tất cả files đã được tạo:
```bash
# AI module structure
ls -la src/core_service/fptchat/ai/
ls -la src/core_service/fptchat/ai/nodes/
ls -la src/core_service/fptchat/ai/tools/

# Task handler
ls -la src/core_service/fptchat/tasks/handler_message/handler_message_ai_chat.py

# Utils
ls -la src/core_service/fptchat/utils/ai_context_builder.py
```

### **2. Update Dependencies**

Add to `requirements.txt`:
```txt
langgraph>=0.0.40
langchain-google-genai>=1.0.0
langchain-community>=0.0.30
```

### **3. Environment Setup**

Add Gemini API key to your settings:
```python
# In configs/settings.py
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
```

### **4. TaskIQ Registration**

Ensure AI task được registered trong TaskIQ broker:
```python
# In src/core_service/fptchat/chatbot.py - should auto-discover
# The @noti_fpt.task decorator will automatically register the task
```

### **5. Test Dependencies**

```bash
python -c "import langgraph; import langchain_google_genai; print('Dependencies OK')"
```

## 🧪 **TESTING GUIDE**

### **1. Basic Webhook Test**

Send simple text message:
```bash
curl -X POST "http://localhost:8000/v1/webhook/webhook_fptchat" \
--header 'Content-Type: application/json' \
--data-raw '{
  "object": "page",
  "entry": [{
    "messaging": [{
      "sender": {"id": "test_user_123"},
      "recipient": {"id": "bot_456"},
      "message": {
        "text": "Xin chào",
        "mid": "test_msg_001"
      },
      "timestamp": 1640995200000
    }]
  }]
}'
```

### **2. Admin Query Test**

Test admin function calling:
```bash
curl -X POST "http://localhost:8000/v1/webhook/webhook_fptchat" \
--header 'Content-Type: application/json' \
--data-raw '{
  "object": "page",
  "entry": [{
    "messaging": [{
      "sender": {"id": "admin_user_456"},
      "recipient": {"id": "bot_456"},
      "message": {
        "text": "Cho tôi danh sách campaigns",
        "mid": "admin_msg_001"
      }
    }]
  }]
}'
```

### **3. Campaign Query Test**

Test campaign memory:
```bash
curl -X POST "http://localhost:8000/v1/webhook/webhook_fptchat" \
--header 'Content-Type: application/json' \
--data-raw '{
  "object": "page",
  "entry": [{
    "messaging": [{
      "sender": {"id": "user_with_campaigns"},
      "recipient": {"id": "bot_456"},
      "message": {
        "text": "Cho tôi xem lại thông báo về khuyến mãi",
        "mid": "campaign_msg_001"
      }
    }]
  }]
}'
```

### **4. RAG Query Test**

Test knowledge base:
```bash
curl -X POST "http://localhost:8000/v1/webhook/webhook_fptchat" \
--header 'Content-Type: application/json' \
--data-raw '{
  "object": "page",
  "entry": [{
    "messaging": [{
      "sender": {"id": "user_789"},
      "recipient": {"id": "bot_456"},
      "message": {
        "text": "FTEL cung cấp dịch vụ gì?",
        "mid": "rag_msg_001"
      }
    }]
  }]
}'
```

## 📊 **MONITORING & LOGS**

### **Expected Log Flow**

1. **Webhook Receipt:**
```
INFO: Text message - Sender: user_123, Message: Xin chào
```

2. **AI Processing:**
```
INFO: [job_id] Processing AI chat from user user_123
INFO: Starting workflow for user user_123
INFO: Classifying intent for user user: Xin chào
INFO: Classified intent: greeting for user user_123
INFO: Processing general chat for user user_123
INFO: Generated general chat response for user user_123
INFO: Successfully sent AI response to user user_123
```

3. **Success Response:**
```
INFO: [job_id] Successfully processed AI chat in 2.34s
```

### **Common Issues & Solutions**

1. **"No AI response found"**
   - Check if LLM processing succeeded
   - Verify Gemini API key
   - Check network connectivity

2. **"Intent classification error"**
   - Check LLM availability
   - Verify prompt templates
   - Check token limits

3. **"Admin function error"**
   - Verify user permissions
   - Check database connections
   - Verify campaign tools

4. **"Campaign memory error"**
   - Check NotificationHistory collection
   - Verify user has received campaigns
   - Check MongoDB connection

## 🔧 **TROUBLESHOOTING**

### **Debug Mode**

Enable detailed logging:
```python
# In logging config
logging.getLogger("src.core_service.fptchat.ai").setLevel(logging.DEBUG)
```

### **Test Individual Components**

```python
# Test intent classification
from src.core_service.fptchat.ai.nodes.classifier import IntentClassifier
classifier = IntentClassifier()

# Test memory building
from src.core_service.fptchat.utils.ai_context_builder import AIContextBuilder
context_builder = AIContextBuilder()
context = await context_builder.build_context("test_user")
```

### **Check Dependencies**

```python
# Test Gemini connection
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key="your_key"
)
response = await llm.ainvoke([{"role": "user", "content": "test"}])
```

## 📈 **PERFORMANCE MONITORING**

### **Key Metrics to Track**

1. **Response Times:**
   - Intent classification: <500ms
   - Function calling: <2s
   - Memory retrieval: <300ms
   - Total response: <3s

2. **Success Rates:**
   - Intent classification accuracy: >90%
   - Admin query success: >95%
   - Memory retrieval success: >98%

3. **Resource Usage:**
   - Memory per request: <50MB
   - Redis cache hit rate: >80%
   - MongoDB query time: <100ms

### **Alerting Setup**

Monitor for:
- High error rates (>5%)
- Slow response times (>5s)
- API key quota exhaustion
- Database connection failures

## 🔒 **SECURITY CHECKLIST**

- ✅ Admin permission validation
- ✅ Tenant data isolation
- ✅ Input sanitization
- ✅ Error message filtering
- ✅ Audit logging for admin queries
- ✅ Rate limiting ready (implement if needed)

## 🚀 **PRODUCTION DEPLOYMENT**

### **Environment-Specific Settings**

```python
# Production settings
AI_CHATBOT_SETTINGS = {
    "max_response_time": 5.0,
    "max_memory_usage": 100,  # MB
    "enable_debug_logs": False,
    "fallback_enabled": True
}
```

### **Health Checks**

Add health check endpoint:
```python
@app.get("/health/ai-chatbot")
async def ai_chatbot_health():
    # Test basic AI functionality
    # Return health status
```

---

**🎉 AI CHATBOT IS READY FOR DEPLOYMENT!**

Hệ thống đã sẵn sàng để handle real user interactions. Test thoroughly và monitor trong production environment.

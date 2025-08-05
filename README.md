# 🤖 Notification Bot - AI Chatbot API Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

## 📋 Tổng quan

Notification Bot là một hệ thống chatbot API backend hoàn chỉnh, có thể import và thêm khách hàng, tạo sự kiện thông báo gửi đến user, sau đó nếu user trả lời qua kênh chat, AI sẽ trả lời user theo context và memory long-short term

### ✨ Tính năng chính

- 👥 **Quản lý khách hàng** - CRUD operations + CSV import tự động
- 📧 **Hệ thống thông báo** - Chat notifications với template system
- ⚡ **Background Tasks** - TaskIQ cho xử lý bất đồng bộ
- 🔐 **JWT Authentication** - Bảo mật API endpoints
- 📊 **Task Monitoring** - Dashboard theo dõi tasks real-time
- 🌐 **RESTful API** - Swagger/OpenAPI documentation
- 🤖 **AI Chatbot thông minh** - Sử dụng Google Gemini với Langchain
- 🧠 **Memory Management** - Redis (short-term) + MongoDB (long-term)


## 🏗️ Kiến trúc hệ thống

```mermaid
graph TB
    A[FastAPI Server] --> B[JWT Auth]
    A --> C[Customer API]
    A --> D[Message API]
    A --> E[Notification API]
    A --> F[Task API]
    
    C --> G[MongoDB]
    D --> H[Google Gemini AI]
    D --> I[Redis Cache]
    D --> G
    
    E --> J[TaskIQ Worker]
    F --> J
    J --> K[Chat Service]
    J --> L[CSV Processing]
    
    H --> M[Langchain]
    I --> N[Short-term Memory]
    G --> O[Long-term Memory]
```

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework cho Python
- **Uvicorn** - ASGI server với performance cao
- **Pydantic** - Data validation và settings management

### Database & Cache
- **MongoDB** - NoSQL database với umongo ODM
- **Redis** - In-memory cache và message broker
- **Motor** - Async MongoDB driver

### GenAI
- **Google Gemini** - Large Language Model
- **Langchain** - AI framework cho chat applications
- **Google GenerativeAI** - Python SDK cho Gemini

### Task Queue & Background Processing
- **TaskIQ** - Modern task queue cho Python
- **TaskIQ-Redis** - Redis broker cho TaskIQ

### Authentication & Security
- **Python-JOSE** - JWT token handling
- **Passlib** - Password hashing với bcrypt
- **CORS Middleware** - Cross-origin resource sharing

### Data Processing & Chat
- **Pandas** - CSV processing và data manipulation
- **aiosmtplib** - Async SMTP client
- **FastAPI-Mail** - Chat template system
- **Jinja2** - Template engine

## 📦 Cài đặt và Setup (Docker)

Cách nhanh nhất và được khuyến khích để chạy dự án này là sử dụng Docker và Docker Compose. Toàn bộ hệ thống (API, Worker, Database, Cache) sẽ được khởi động chỉ với một vài lệnh đơn giản.

### 1. Yêu cầu hệ thống
- Docker
- Docker Compose
- `make` (tùy chọn, để sử dụng các lệnh tắt)

### 2. Clone repository
```bash
git clone <repository-url>
cd notification_bot
```

### 3. Cấu hình môi trường
Cần tạo một file `.env` trong thư mục `notification/` để cấu hình các biến môi trường.

```bash
# Từ thư mục gốc của project (notification_bot)
cp notification/env.example notification/.env
```

Sau đó, mở file `notification/.env` và điền `GOOGLE_API_KEY` của . Các biến khác đã được cấu hình sẵn để hoạt động với Docker Compose.

```env
# notification/.env

# Google Gemini API (BẮT BUỘC)
GOOGLE_API_KEY=your-google-api-key-here

# Các biến khác có thể giữ nguyên khi chạy với Docker
# ...
```

### 4. Khởi động hệ thống
Sử dụng `make` để khởi động tất cả các service. Lệnh này sẽ tự động build image và chạy các container ở chế độ nền.

```bash
make up
```

Nếu không có `make`,  có thể dùng lệnh `docker-compose` trực tiếp:
```bash
docker-compose up -d --build
```

### 5. Kiểm tra trạng thái
Sau khi khởi động, có thể kiểm tra trạng thái của các container:
```bash
docker-compose ps
```

Các service `mongo`, `redis`, `app`, và `worker` sẽ chạy.

### 6. Truy cập ứng dụng
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Các lệnh `make` hữu ích khác
- `make logs`: Xem log từ tất cả các service.
- `make logs-app`: Chỉ xem log của API server.
- `make logs-worker`: Chỉ xem log của TaskIQ worker.
- `make down`: Dừng tất cả các service.
- `make clean`: Dừng và xóa toàn bộ container, network và volume.
- `make shell`: Truy cập vào shell của container `app` để gỡ lỗi hoặc chạy lệnh.

## 🚀 API Documentation

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | Đăng nhập user | ❌ |
| GET | `/auth/me` | Thông tin user hiện tại | ✅ |
| POST | `/auth/register` | Đăng ký user mới | ❌ |

### Customer Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/customers` | Danh sách khách hàng (có pagination) | ✅ |
| POST | `/customers` | Tạo khách hàng mới | ✅ |
| GET | `/customers/{id}` | Chi tiết khách hàng | ✅ |
| PUT | `/customers/{id}` | Cập nhật khách hàng | ✅ |
| DELETE | `/customers/{id}` | Xóa khách hàng | ✅ |
| POST | `/customers/import` | Import CSV với TaskIQ | ✅ |

### AI Chatbot
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/messages/send` | Gửi tin nhắn cho AI | ✅ |
| GET | `/messages/history` | Lịch sử chat theo session | ✅ |
| DELETE | `/messages/history/{session_id}` | Xóa lịch sử chat | ✅ |
| GET | `/messages/memory/stats` | Thống kê memory usage | ✅ |

### Notification System
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/notifications/config` | Tạo notification template | ✅ |
| GET | `/notifications/config` | Danh sách templates | ✅ |
| PUT | `/notifications/config/{id}` | Cập nhật template | ✅ |
| DELETE | `/notifications/config/{id}` | Xóa template | ✅ |
| POST | `/notifications/send` | Gửi notification với TaskIQ | ✅ |
| GET | `/notifications/history` | Lịch sử notifications | ✅ |
| GET | `/notifications/stats` | Thống kê notifications | ✅ |

### Task Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks` | Danh sách tasks (có filter) | ✅ |
| GET | `/tasks/{job_id}` | Chi tiết task | ✅ |
| POST | `/tasks/{job_id}/cancel` | Hủy task đang chạy | ✅ |
| DELETE | `/tasks/{job_id}` | Xóa task record | ✅ |
| GET | `/tasks/stats/overview` | Thống kê tổng quan | ✅ |
| GET | `/tasks/stats/recent` | Thống kê tasks gần đây | ✅ |

## 🤖 AI Chatbot System

### Tính năng AI
- **Context Awareness**: Bot nhớ thông tin khách hàng và lịch sử hội thoại
- **Vietnamese Support**: Được tối ưu cho tiếng Việt
- **Professional Tone**: Giọng điệu chuyên nghiệp
- **Notification Integration**: Tự động reference notifications trong chat
- **Memory Management**: Kết hợp short-term (Redis) và long-term (MongoDB)

### System Prompt
Bot được cấu hình với personality chuyên nghiệp trong `prompts/system_prompt.py`:
- Trợ lý khách hàng thân thiện
- Trả lời bằng tiếng Việt
- Hỗ trợ đặt hàng, thanh toán, chính sách
- Tích hợp thông báo vào cuộc hội thoại

### Memory Architecture
```python
# Short-term Memory (Redis) - 30 phút
- Conversation context
- Recent customer interactions
- Temporary session data

# Long-term Memory (MongoDB) - Vĩnh viễn
- Customer profiles
- Chat history
- Notification records
- Learning patterns
```

## 📧 Notification System

### Template System
- **Dynamic Variables**: `{customer_name}`, `{customer_email}`, `{company}`
- **Jinja2 Templates**: Advanced templating với logic
- **Multi-channel**: Chat
- **Batch Processing**: Gửi hàng loạt với TaskIQ

### Notification Flow
```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant TaskIQ
    participant AI Bot
    participant Customer
    
    Admin->>API: POST /notifications/send
    API->>TaskIQ: Queue notification task
    TaskIQ->>TaskIQ: Process template
    TaskIQ->>Customer: Send Chat
    TaskIQ->>AI Bot: Inject into chat context
    Customer->>AI Bot: Ask about notification
    AI Bot->>Customer: Reference notification content
```

## ⚡ TaskIQ Background Processing

### Task Types
1. **CSV Import Processing** (`import_customers.py`)
   - Parse và validate CSV files
   - Batch insert customers
   - Progress tracking
   - Error reporting

2. **Chat Notification Sending** (`send_notification.py`)
   - Template processing
   - Batch Chat sending
   - Delivery tracking
   - Retry mechanism

### Task Monitoring
- **Real-time Progress**: WebSocket updates
- **Status Tracking**: pending → running → completed/failed
- **Error Handling**: Detailed error logs
- **Performance Metrics**: Execution time, success rate
- **Task Cancellation**: Stop running tasks

## 📁 Cấu trúc Project

```
notification/
├── 📁 api/                     # API route handlers
│   ├── 🔐 auth.py             # JWT authentication
│   ├── 👥 customer.py         # Customer CRUD + CSV import
│   ├── 💬 message.py          # AI chatbot messaging
│   ├── 📧 notification.py     # Notification management
│   └── ⚡ tasks.py            # Task monitoring
├── 📁 config/                  # Configuration modules
│   ├── ⚙️ settings.py         # Pydantic settings
│   └── 🗄️ database.py         # DB connection setup
├── 📁 models/                  # Database models (umongo)
│   ├── 👤 user.py             # User authentication
│   ├── 👥 customer.py         # Customer data model
│   ├── 💬 chat.py             # Chat sessions & messages
│   ├── 📧 notification.py     # Notification templates
│   └── ⚡ task.py             # TaskIQ job tracking
├── 📁 services/                # Business logic layer
│   ├── 🔐 auth.py             # JWT + password hashing
│   ├── 🤖 ai_chatbot.py       # Google Gemini integration
│   └── 🧠 memory_manager.py   # Redis + MongoDB memory
├── 📁 tasks/                   # TaskIQ background tasks
│   ├── 📊 import_customers.py # CSV processing
│   └── 📧 send_notification.py# Chat sending
├── 📁 utils/                   # Utility functions
│   └── ✅ validators.py       # Data validation helpers
├── 📁 prompts/                 # AI prompt templates
│   └── 🤖 system_prompt.py    # FTEL chatbot personality
├── 📁 uploads/                 # File upload directory
├── 🚀 main.py                 # FastAPI application
├── ⚡ worker.py               # TaskIQ worker process
├── 📋 requirements.txt        # Python dependencies
├── 🔧 env.example             # Environment template
└── 📚 README.md               # Documentation
```

## 🔧 Development

### Local Development
```bash
# Hot reload development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run TaskIQ worker với debug
python worker.py

# Run tests
pytest tests/ -v

# Code formatting
black .
isort .
```

### Environment Variables
```env
# App Configuration
DEBUG=true
APP_NAME="Chatbot API Backend"
APP_VERSION="1.0.0"
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
MONGODB_URL=mongodb://admin:password123@localhost:27017
MONGODB_DATABASE=chatbot_db

# Redis & TaskIQ
REDIS_URL=redis://localhost:6379
REDIS_DB=0
TASKIQ_BROKER_URL=redis://localhost:6379/1
TASKIQ_RESULT_BACKEND_URL=redis://localhost:6379/2

# AI Configuration
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=gemini-1.5-flash

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Memory Settings
SHORT_TERM_MEMORY_TTL=1800  # 30 minutes
MAX_CONVERSATION_HISTORY=50
```

## 📊 Monitoring & Analytics

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db

# Redis connectivity
curl http://localhost:8000/health/redis
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Performance Monitoring
- Task execution metrics
- Memory usage statistics
- API response times
- Error rate tracking
- Database query performance

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt với salt
- **CORS Protection**: Configurable origins
- **Input Validation**: Pydantic models
- **File Upload Security**: Type và size validation
- **Rate Limiting**: API endpoint protection
- **SQL Injection Prevention**: NoSQL với umongo

## 🐳 Docker Deployment (Coming Soon)

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mongo
      - redis
    environment:
      - MONGODB_URL=mongodb://admin:password123@mongo:27017
      - REDIS_URL=redis://redis:6379
      # ... other env vars

  worker:
    build: .
    command: python worker.py
    depends_on:
      - redis
    environment:
      - TASKIQ_BROKER_URL=redis://redis:6379/1
      # ... other env vars

  mongo:
    image: mongo:latest
    # ... config

  redis:
    image: redis:7-alpine
    # ... config
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
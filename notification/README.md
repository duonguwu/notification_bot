# 🚀 Chatbot API Backend

Backend API cho hệ thống chatbot với AI, TaskIQ, MongoDB và Redis.

## 🏗️ Kiến trúc

```
FastAPI (JWT Auth) 
    ├── Customer Management (CRUD + CSV Import with TaskIQ)
    ├── AI Chatbot (Google Gemini + Langchain)
    ├── Memory Management (Redis + MongoDB)
    ├── Notification System (Email + TaskIQ)
    └── Task Management (TaskIQ Monitoring)
```

## 🛠️ Công nghệ sử dụng

- **FastAPI** - Web framework
- **MongoDB + umongo** - Database
- **Redis** - Cache & short-term memory
- **TaskIQ** - Background task processing ✅
- **Google Gemini** - AI model
- **Langchain** - AI framework
- **JWT** - Authentication
- **Pandas** - CSV processing ✅
- **aiosmtplib** - Email sending ✅

## 📦 Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd notification
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
```bash
cp env.example .env
# Chỉnh sửa file .env với thông tin của bạn
```

### 5. Khởi động services
```bash
# Start MongoDB và Redis
docker-compose up -d mongo redis

# Hoặc chạy riêng lẻ:
docker run -d -p 27017:27017 --name mongo-container mongo:latest
docker run -d -p 6379:6379 --name redis-container redis:7-alpine
```

### 6. Setup environment
```bash
# Copy environment file
cp env.example .env

# Edit .env file với configuration của bạn
# Đặc biệt là GOOGLE_API_KEY
```

### 7. Chạy ứng dụng
```bash
# Terminal 1: FastAPI app
python main.py

# Terminal 2: TaskIQ worker
python worker.py

# Hoặc dùng Makefile:
make run      # Run FastAPI
make worker   # Run TaskIQ worker
make dev      # Run với auto-reload
```

## 🔧 Cấu hình

### Biến môi trường quan trọng:

- `GOOGLE_API_KEY` - API key cho Google Gemini (bắt buộc)
- `SECRET_KEY` - JWT secret key
- `MONGODB_URL` - MongoDB connection string (với auth)
- `REDIS_URL` - Redis connection string
- `TASKIQ_BROKER_URL` - TaskIQ Redis broker URL

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - Đăng nhập
- `GET /auth/me` - Thông tin user hiện tại
- `POST /auth/register` - Đăng ký (dev only)

### Customers
- `GET /customers` - Danh sách khách hàng
- `POST /customers` - Tạo khách hàng mới
- `GET /customers/{id}` - Chi tiết khách hàng
- `POST /customers/import` - Import CSV với TaskIQ ✅

### Messages
- `POST /messages/send` - Gửi tin nhắn cho AI
- `GET /messages/history` - Lịch sử chat
- `GET /messages/memory/stats` - Thống kê memory

### Notifications ✅
- `POST /notifications/config` - Tạo notification template
- `GET /notifications/config` - Danh sách templates
- `POST /notifications/send` - Gửi notification với TaskIQ
- `GET /notifications/history` - Lịch sử notifications
- `GET /notifications/stats` - Thống kê notifications

### Tasks ✅
- `GET /tasks` - Danh sách tasks
- `GET /tasks/{job_id}` - Chi tiết task
- `POST /tasks/{job_id}/cancel` - Hủy task
- `GET /tasks/stats/overview` - Thống kê tổng quan
- `GET /tasks/stats/recent` - Thống kê gần đây

## 🤖 AI Chatbot

### Features:
- **Memory Management**: Short-term (Redis) + Long-term (MongoDB)
- **Context Awareness**: Nhớ thông tin khách hàng và lịch sử chat
- **Vietnamese Support**: Trả lời bằng tiếng Việt
- **Professional Tone**: Giọng điệu chuyên nghiệp, thân thiện

### System Prompt:
Được cấu hình trong `prompts/system_prompt.txt`

## 🔄 TaskIQ Integration ✅

### Task Types:
- **CSV Import Processing**: Import khách hàng từ file CSV
- **Email Notification Sending**: Gửi email hàng loạt
- **Background Processing**: Xử lý tác vụ nặng

### Features:
- **Progress Tracking**: Theo dõi tiến độ real-time
- **Error Handling**: Xử lý lỗi và retry
- **Task Monitoring**: Dashboard quản lý tasks
- **File Management**: Tự động cleanup files

### Task Management:
- **Task Status**: pending, running, completed, failed, cancelled
- **Progress Updates**: Real-time progress tracking
- **Task Cancellation**: Hủy task đang chạy
- **Statistics**: Performance metrics và analytics

## 📧 Notification System ✅

### Features:
- **Template Management**: Tạo và quản lý notification templates
- **Dynamic Content**: Template variables (customer_name, company, etc.)
- **Chat Integration**: Gửi notifications vào chat sessions
- **Batch Sending**: Gửi cho nhiều customers cùng lúc
- **Interactive Notifications**: Users có thể respond to notifications
- **AI Context Awareness**: Bot nhớ và reference notifications

### Template Variables:
- `{customer_name}` - Tên khách hàng
- `{customer_email}` - Email khách hàng
- `{company}` - Tên công ty
- Custom variables từ request data

### Notification Flow:
- **Admin sends notification** → **Creates system message in chat** → **User sees in chat interface** → **User can respond** → **AI provides context**

## 📁 Cấu trúc Project

```
notification/
├── api/                    # API endpoints
│   ├── auth.py            # JWT Authentication
│   ├── customer.py        # Customer CRUD + Import
│   ├── message.py         # AI Chatbot messaging
│   ├── tasks.py           # Task management ✅
│   └── notification.py    # Notification system ✅
├── config/                 # Configuration
│   ├── settings.py        # Pydantic Settings
│   └── database.py        # DB connections
├── models/                 # Database models
│   ├── user.py            # User authentication
│   ├── customer.py        # Customer data
│   ├── notification.py    # Notification system
│   ├── chat.py           # Chat sessions & messages
│   └── task.py           # TaskIQ job tracking ✅
├── services/               # Business logic
│   ├── auth.py           # JWT + password hashing
│   ├── ai_chatbot.py     # Google Gemini + Langchain
│   └── memory_manager.py # Redis + MongoDB memory
├── tasks/                  # TaskIQ tasks ✅
│   ├── import_customers.py # CSV import processing
│   └── send_notification.py # Email sending
├── utils/                  # Utilities ✅
│   └── validators.py      # Data validation
├── prompts/                # AI prompts
│   └── system_prompt.txt  # FTEL chatbot personality
├── main.py                # FastAPI application
├── worker.py              # TaskIQ worker ✅
├── requirements.txt       # Dependencies
└── env.example            # Environment template
```

## 🚀 Development

### Chạy với hot reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Chạy TaskIQ worker:
```bash
python worker.py
```

### API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Check:
```bash
curl http://localhost:8000/health
```

## 📊 TaskIQ Monitoring

### Task Dashboard:
- **Overview**: Tổng quan tất cả tasks
- **Real-time Progress**: Theo dõi tiến độ live
- **Error Logs**: Chi tiết lỗi và debugging
- **Performance Metrics**: Thời gian xử lý, success rate

### Task Status:
- **Pending**: Task đang chờ xử lý
- **Running**: Task đang chạy
- **Completed**: Task hoàn thành thành công
- **Failed**: Task thất bại
- **Cancelled**: Task bị hủy

## 🔒 Security

- JWT Authentication cho tất cả protected endpoints
- Password hashing với bcrypt
- CORS configuration
- Input validation với Pydantic
- File upload security

## 📈 Monitoring & Analytics

- Health check endpoint
- Task status tracking
- Memory statistics
- Notification delivery tracking
- Error logging và debugging

## 🐳 Docker (Coming Soon)

```bash
docker-compose up -d
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License 
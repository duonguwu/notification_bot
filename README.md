# 🚀 **CHATBOT API BACKEND**

---

## **1. TỔNG QUAN KIẾN TRÚC**

```
Client <--> FastAPI (JWT Auth, RESTful API)
                |
                |-- CSV Import API ----> TaskIQ (Xử lý nền với pandas) ---> MongoDB (umongo)
                |
                |-- Notification API --(TaskIQ email sender)--> SMTP/Email
                |
                |-- Message API (chatbot logic) --(Langchain/AI)--> 
                |         |                            |            
                |         |----> Redis (short-term memory)         
                |         |----> MongoDB (long-term memory)        
```

---

## **2. CÁC CHỨC NĂNG & LUỒNG XỬ LÝ CHÍNH**

### **A. Đăng nhập/Xác thực JWT**

* **API**: `POST /auth/login`
* Nhận username/password, trả về JWT Token.
* Dùng JWT để xác thực các endpoint khác.

**Công nghệ:**

* FastAPI
* `fastapi.security` (OAuth2PasswordBearer/JWT)
* PyJWT hoặc jose

---

### **B. Import khách hàng từ CSV (Xử lý bất đồng bộ với TaskIQ)**

* **API**: `POST /customers/import`

  * Nhận file CSV upload từ user.
  * Trả về job\_id để check trạng thái xử lý.

* **Luồng xử lý:**

  1. File lưu tạm (hoặc buffer in-memory).
  2. Đẩy task vào TaskIQ queue (task xử lý file nền).
  3. TaskIQ worker dùng pandas đọc file, lọc row trùng (theo email/phone/ID).
  4. Lưu từng khách hàng vào MongoDB (qua umongo).
  5. Ghi log trạng thái (số dòng thành công, lỗi, v.v.)

* **API**: `GET /customers/import/{job_id}/status`

  * Trả về trạng thái xử lý, tổng số dòng thành công, bị lỗi, v.v.

**Công nghệ:**

* FastAPI (upload file)
* TaskIQ (background processing)
* pandas (read/clean csv)
* MongoDB + umongo (lưu customer)
* Redis (job status cache, tuỳ chọn)

---

### **C. Quản lý khách hàng**

* **API**: `GET /customers` (paging, filter)
* **API**: `GET /customers/{id}`
* **API**: `PUT /customers/{id}` (update info)
* **API**: `DELETE /customers/{id}`

**Công nghệ:**

* FastAPI
* MongoDB + umongo

---

### **D. Cấu hình và gửi thông báo (Notification) cho khách hàng**

#### **1. Tạo cấu hình thông báo**

* **API**: `POST /notifications/config`

  * Định nghĩa template, loại thông báo, kênh gửi (email).
  * VD: Chọn nội dung email, subject, vv.
* **API**: `GET /notifications/configs`

  * Xem các config hiện có.

**Công nghệ:**

* FastAPI
* MongoDB + umongo

#### **2. Gửi thông báo**

* **API**: `POST /notifications/send`

  * Truyền vào: customer\_id hoặc “all”, notification\_config\_id, data động (cho template).
  * Gọi task gửi nền bằng TaskIQ (có thể batch khi gửi nhiều).

**Luồng xử lý:**

* TaskIQ lấy thông tin khách hàng, render template, gửi email.
* Cập nhật trạng thái gửi thành công/thất bại.
* Nếu gửi cho nhiều user: chunk thành các batch nhỏ.

**Công nghệ:**

* FastAPI (API)
* TaskIQ (task gửi email, retry nếu lỗi)
* Email (SMTP, dùng thư viện như aiosmtplib hoặc fastapi-mail)
* MongoDB (lưu log gửi/noti)

---

### **E. Chatbot Message API – Trả lời user bằng AI**

* **API**: `POST /messages/send`

  * Nhận vào: customer\_id, message.
  * Lưu message user vào memory (ngắn và dài).
  * Gọi Langchain để generate response.
  * Lưu response vào memory và trả về API.

#### **Memory ngắn/dài:**

* **Short-term (ngắn):** Redis (tồn tại 10-30 phút, các message gần nhất)
* **Long-term (dài):** MongoDB (toàn bộ lịch sử hội thoại)
* Khi cần sinh response, sẽ lấy cả memory ngắn & dài truyền cho Langchain.

**Công nghệ:**

* FastAPI
* Redis (short-term message buffer)
* MongoDB + umongo (long-term chat history)
* Langchain (AI chatbot pipeline, tích hợp Google Gemini API)
* Google Gemini Pro (AI model chính)
* TaskIQ (nếu muốn trả lời async hoặc có delay xử lý lớn)

---

### **F. API query lịch sử hội thoại**

* **API**: `GET /messages/history?customer_id=...`

**Công nghệ:**

* FastAPI
* MongoDB

---

### **G. Task Management & Monitoring APIs**

#### **1. Quản lý Tasks**

* **API**: `GET /tasks` 
  * List tất cả tasks với filter theo status, type, user_id
  * Phân trang và sort theo thời gian
* **API**: `GET /tasks/{job_id}`
  * Chi tiết task cụ thể (progress, logs, error messages)
* **API**: `POST /tasks/{job_id}/cancel`
  * Hủy task đang pending hoặc running
* **API**: `GET /tasks/stats`
  * Dashboard stats: số task pending/running/completed/failed

#### **2. Task Types được hỗ trợ:**

* `csv_import` - Import khách hàng từ CSV
* `email_batch_send` - Gửi email hàng loạt
* `ai_chat_process` - Xử lý AI response phức tạp (nếu cần async)

**Công nghệ:**

* FastAPI
* TaskIQ (task execution)
* Redis (task status cache + results)
* MongoDB (task logs + history)

---

### **H. AI Prompt Management**

#### **1. Dynamic Prompts**

* **API**: `GET /prompts/templates`
  * List các template prompt có sẵn
* **API**: `POST /prompts/templates`
  * Tạo/cập nhật prompt template
* **API**: `GET /prompts/render`
  * Test render prompt với data mẫu

#### **2. Prompt Features:**

* **System prompts**: Định nghĩa personality của bot
* **Context templates**: Template để inject customer info, history
* **Dynamic variables**: `{customer_name}`, `{company}`, `{recent_history}`
* **Multilingual support**: Prompt theo ngôn ngữ khách hàng

**Công nghệ:**

* Jinja2 (template rendering)
* Google Gemini Pro (AI model)
* Langchain (prompt management)

---

## **3. ĐỀ XUẤT CẤU TRÚC PROJECT**

```
/app
├── api/
│   ├── auth.py
│   ├── customer.py
│   ├── notification.py
│   ├── message.py
│   └── tasks.py (Task management APIs)
├── tasks/
│   ├── import_customers.py
│   ├── send_email.py
│   └── ai_chat_processor.py (Async AI processing)
├── models/
│   ├── user.py
│   ├── customer.py
│   ├── notification.py
│   ├── chat.py
│   └── task.py (Job status tracking)
├── services/
│   ├── email_sender.py
│   ├── ai_chatbot.py
│   ├── memory_manager.py
│   ├── auth.py
│   └── task_manager.py
├── prompts/
│   ├── system_prompt.txt
│   ├── customer_service.txt
│   └── templates/ (Dynamic prompt templates)
├── utils/
│   ├── csv_cleaner.py
│   └── validators.py
├── config/
│   ├── settings.py
│   └── database.py
├── main.py (FastAPI entry)
├── worker.py (TaskIQ worker)
└── requirements.txt
```

---

## **4. TÓM TẮT CÔNG NGHỆ TƯƠNG ỨNG**

| Thành phần        | Công nghệ                     |
| ----------------- | ----------------------------- |
| API server        | FastAPI                       |
| Auth              | JWT (PyJWT, fastapi.security) |
| Database          | MongoDB + umongo              |
| Task Queue        | TaskIQ + RabbitMQ/Redis       |
| CSV processing    | pandas                        |
| Email             | aiosmtplib, fastapi-mail      |
| AI chatbot        | Langchain, Google Gemini      |
| Prompt templates  | Jinja2                        |
| Short-term memory | Redis                         |
| Long-term memory  | MongoDB                       |
| Task monitoring   | Redis + MongoDB               |
| Async/Queue       | TaskIQ                        |

---

## **5. API ENDPOINTS**

| Phân hệ      | Endpoint                                | Ý nghĩa                      |
| ------------ | --------------------------------------- | ---------------------------- |
| Auth         | POST `/auth/login`                      | Đăng nhập, trả JWT           |
| Customer     | POST `/customers/import`                | Import csv, đẩy task         |
|              | GET `/customers/import/{job_id}/status` | Tra trạng thái import        |
|              | GET `/customers`                        | List, filter, paging         |
|              | GET `/customers/{id}`                   | Lấy info                     |
|              | PUT `/customers/{id}`                   | Update                       |
|              | DELETE `/customers/{id}`                | Xoá                          |
| Notification | POST `/notifications/config`            | Tạo config noti              |
|              | GET `/notifications/configs`            | List config                  |
|              | POST `/notifications/send`              | Gửi noti (1 user / all)      |
| Message      | POST `/messages/send`                   | User gửi message, AI trả lời |
|              | GET `/messages/history`                 | Query hội thoại              |
| Tasks        | GET `/tasks`                            | List tất cả tasks/jobs       |
|              | GET `/tasks/{job_id}`                   | Chi tiết task cụ thể         |
|              | POST `/tasks/{job_id}/cancel`           | Hủy task đang chạy           |
|              | GET `/tasks/stats`                      | Thống kê task (pending/running/completed/failed) |

---

## **6. VỀ KỸ THUẬT**

* **Sử dụng TaskIQ** để giải phóng tải cho API server, xử lý các công việc nặng như import csv hoặc gửi nhiều email đồng loạt.
* **pandas** giúp xử lý dữ liệu lớn, lọc trùng, chuẩn hoá khách hàng hiệu quả.
* **umongo** chuẩn hoá schema khách hàng, log gửi, chat history.
* **AI chatbot** quản lý ngữ cảnh hội thoại chuyên nghiệp nhờ hệ thống memory ngắn/dài (redis/mongodb), có thể dễ dàng mở rộng dùng nhiều loại AI khác nhau.
* **Bảo mật** tốt với JWT, validate từng request.
* **Dễ scale**: Task worker có thể mở rộng theo số lượng request lớn.
* **Task Monitoring**: Full visibility vào task status, logs, và performance metrics.
* **Dynamic Prompts**: Quản lý prompts linh hoạt, test và A/B test các prompt khác nhau.
* **Google Gemini Integration**: Sử dụng model AI mạnh mẽ với cost-effective.
* **Memory Architecture**: Hybrid memory (Redis + MongoDB) cho performance và persistence tối ưu.
* **Xử lý realtime**: Có thể bổ sung WebSocket nếu cần gửi notification/chat live về client.

---

## **7. LƯU Ý VÀ GỢI Ý PHÁT TRIỂN THÊM**

### **A. Production Ready Features:**
* **Rate Limiting**: Implement rate limiting cho các API endpoints
* **Caching Strategy**: Cache frequent queries (customer info, prompt templates)
* **Health Checks**: `/health` endpoint cho load balancer
* **Metrics & Logging**: Prometheus metrics, structured logging
* **Error Handling**: Comprehensive error responses với error codes

### **B. Advanced Features:**
* **Webhook Support**: Cho external integrations
* **Batch Operations**: Bulk customer operations
* **File Storage**: S3/MinIO cho CSV files và attachments  
* **API Versioning**: `/v1/`, `/v2/` cho backward compatibility
* **OpenAPI Documentation**: Auto-generated với examples

### **C. Cấu trúc API modules:**
  * **Auth**: JWT, refresh tokens, user management
  * **Customer**: CRUD, import, export, segmentation
  * **Notification**: Templates, campaigns, delivery tracking
  * **Message**: AI chat, history, context management  
  * **Tasks**: Job monitoring, cancellation, retry logic
  * **Prompts**: Template management, A/B testing

### **D. TaskIQ Advanced Usage:**
* **Task Priorities**: High/Normal/Low priority queues
* **Task Scheduling**: Cron-like scheduled tasks
* **Task Chaining**: Pipeline of dependent tasks
* **Error Recovery**: Automatic retry với exponential backoff
* **Task Metrics**: Execution time, success rate tracking

---

Bạn thấy plan này đã “giải nghĩa” đủ kỹ ý tưởng chưa?
Bạn cần **mock code khởi đầu**, hoặc vẽ sơ đồ kiến trúc, hay cần chi tiết hơn từng phần nào không?
Tui có thể gợi ý kỹ hơn về xử lý AI memory hoặc cách build TaskIQ worker cho file import nếu bạn muốn!

# SRS - SCC NOTIFICATION BOT
## Tài liệu Đặc tả Yêu cầu Phần mềm (Software Requirements Specification)

---

## MỤC LỤC

### A. GIỚI THIỆU
I. [Mục đích tài liệu](#i-mục-đích-tài-liệu)  
II. [Thông tin chung](#ii-thông-tin-chung)  
III. [Tài liệu tham khảo](#iii-tài-liệu-tham-khảo)  
IV. [Thuật ngữ, từ ngữ viết tắt](#iv-thuật-ngữ-từ-ngữ-viết-tắt)  

### B. [ERD (Entity Relationship Diagram)](#b-erd-entity-relationship-diagram)

### C. TỔNG QUAN
I. [Sơ đồ tổng quan](#i-sơ-đồ-tổng-quan)  
II. [Use-case diagram](#ii-use-case-diagram)  
III. [Danh sách các chức năng và Phân quyền](#iii-danh-sách-các-chức-năng-và-phân-quyền)  
IV. [Các yêu cầu phi chức năng](#iv-các-yêu-cầu-phi-chức-năng)  

### D. [ĐẶC TẢ CÁC CHỨC NĂNG](#d-đặc-tả-các-chức-năng)

---

## A. GIỚI THIỆU

### I. Mục đích tài liệu
Tài liệu này mô tả các yêu cầu chức năng và phi chức năng của hệ thống **SCC Notification Bot** - một hệ thống quản lý và gửi thông báo tự động đa kênh (FPT Chat, Email, Telegram). Tài liệu này được xây dựng để:

- Cung cấp cái nhìn tổng quan về hệ thống cho các bên liên quan
- Định nghĩa rõ ràng các chức năng và luồng xử lý
- Làm cơ sở cho việc kiểm thử bảo mật (penetration testing)
- Hỗ trợ việc phát triển và bảo trì hệ thống

### II. Thông tin chung

**Tên dự án:** SCC Notification Bot  
**Phiên bản:** 1.0  
**Ngày tạo:** [Ngày hiện tại]  
**Người tạo:** Development Team  

**Mô tả hệ thống:**
SCC Notification Bot là một hệ thống notification automation được thiết kế theo kiến trúc microservices với các worker xử lý bất đồng bộ. Hệ thống hỗ trợ:

- Quản lý campaign marketing tự động
- Gửi tin nhắn đa kênh (FPT Chat, Email, Telegram)
- Xử lý luồng conversation tương tác
- Lập lịch và trigger campaign theo thời gian
- Quản lý dữ liệu khách hàng và phân quyền

**Công nghệ sử dụng:**
- **Backend:** FastAPI, Python 3.8+
- **Database:** MongoDB (Motor driver)
- **Cache:** Redis
- **Message Queue:** RabbitMQ với TaskIQ
- **Authentication:** Microsoft Azure AD SSO + JWT
- **Deployment:** Docker, Gunicorn

### III. Tài liệu tham khảo
- [README copy.md](./zmarkdown/README%20copy.md)
- [summary.md](./zmarkdown/summary.md)
- FastAPI Documentation
- TaskIQ Documentation
- MongoDB Documentation

### IV. Thuật ngữ, từ ngữ viết tắt

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **Campaign** | Chiến dịch gửi tin nhắn có kèm lịch trình và script content |
| **Script Content** | Nội dung tin nhắn và luồng conversation (nodes/edges) |
| **Customer Data** | Dữ liệu khách hàng được import để gửi tin nhắn |
| **TaskIQ** | Distributed task queue system thay thế Celery |
| **Worker** | Process xử lý task bất đồng bộ |
| **Tenant** | Đơn vị tổ chức có dữ liệu riêng biệt (multi-tenancy) |
| **FPT Chat** | Nền tảng chat của FPT để gửi tin nhắn |
| **SSO** | Single Sign-On với Microsoft Azure AD |

---

## B. ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    UserInfo {
        ObjectId _id PK
        string email
        string name
        string password
        boolean is_active
        array role_id FK
        datetime created_at
        string created_by
        datetime updated_at
        string updated_by
        string tenant_id
    }

    Roles {
        ObjectId _id PK
        string role_name
        string role_description
        array permissions
        boolean is_active
        datetime created_at
        string created_by
        datetime updated_at
        string updated_by
        string tenant_id
    }

    CampaignManagement {
        ObjectId _id PK
        string campaign_name
        array campaign_type
        string config_noti_id FK
        string campaign_status
        datetime start_time
        datetime end_time
        string customer_data_id FK
        object script_content
        object schedule_info
        datetime created_at
        string created_by
        datetime updated_at
        string updated_by
        string tenant_id
    }

    CustomerDataInfo {
        ObjectId _id PK
        string data_name
        string share_id
        object data_type
        array customer_fields
        datetime created_at
        string created_by
        datetime updated_at
        string updated_by
        string tenant_id
    }

    CustomerDataShared {
        ObjectId _id PK
        string share_id FK
        array customer_data
        string data_name
        object data_type
        datetime created_at
        string created_by
        datetime updated_at
        string updated_by
        string tenant_id
    }

    ConfigNotificationInfo {
        ObjectId _id PK
        string config_name
        object config_info
        string channel
        datetime created_at
        string created_by
        datetime updated_at
        string updated_by
        string tenant_id
    }

    %% Relationships
    UserInfo ||--o{ Roles : "has roles"
    CampaignManagement ||--|| ConfigNotificationInfo : "uses config"
    CampaignManagement ||--|| CustomerDataInfo : "targets customers"
    CustomerDataInfo ||--|| CustomerDataShared : "shares data"
```

---

## C. TỔNG QUAN

### I. Sơ đồ tổng quan

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web UI/Admin Dashboard]
        API_CLIENT[API Clients]
    end

    subgraph "API Gateway Layer"
        LB[Load Balancer]
        AUTH[Authentication/SSO]
    end

    subgraph "Application Layer"
        API[FastAPI Application]
        ADMIN[Admin Site]
    end

    subgraph "Core Services"
        CAMPAIGN[Campaign Management]
        CUSTOMER[Customer Data Service]
        SCHEDULE[Schedule Service]
    end

    subgraph "Worker Layer"
        FPTCHAT_WORKER[FPT Chat Worker]
        SENDER_WORKER[Sender Worker]
        SCHEDULE_WORKER[Schedule Worker]
    end

    subgraph "Message Queue"
        RABBITMQ[RabbitMQ]
        REDIS[Redis Cache/Result Backend]
    end

    subgraph "External Services"
        FPTCHAT_API[FPT Chat API]
        EMAIL_API[Email Service]
        TELEGRAM_API[Telegram Bot API]
        AZURE_AD[Microsoft Azure AD]
    end

    subgraph "Data Layer"
        MONGODB[MongoDB]
    end

    %% Connections
    UI --> LB
    API_CLIENT --> LB
    LB --> AUTH
    AUTH --> API
    AUTH --> ADMIN
    API --> CAMPAIGN
    API --> CUSTOMER
    CAMPAIGN --> MONGODB
    CUSTOMER --> MONGODB
    SCHEDULE --> RABBITMQ
    RABBITMQ --> FPTCHAT_WORKER
    RABBITMQ --> SENDER_WORKER
    FPTCHAT_WORKER --> SENDER_WORKER
    SENDER_WORKER --> FPTCHAT_API
    SENDER_WORKER --> EMAIL_API
    SENDER_WORKER --> TELEGRAM_API
    AUTH --> AZURE_AD
    FPTCHAT_WORKER --> REDIS
    SENDER_WORKER --> REDIS
    SCHEDULE_WORKER --> REDIS
```

### II. Use-case diagram

```mermaid
graph LR
    subgraph "Actors"
        ADMIN[System Admin]
        TENANT_ADMIN[Tenant Admin]
        USER[End User]
        SYSTEM[System/Scheduler]
        FPTCHAT[FPT Chat Platform]
    end

    subgraph "Authentication & Authorization"
        UC1[Login with SSO]
        UC2[Manage Roles & Permissions]
        UC3[Manage Users]
    end

    subgraph "Campaign Management"
        UC4[Create Campaign]
        UC5[Update Campaign]
        UC6[Delete Campaign]
        UC7[View Campaign List]
        UC8[View Campaign Details]
    end

    subgraph "Customer Data Management"
        UC9[Import Customer Data]
        UC10[View Customer Data]
        UC11[Export Customer Data]
        UC12[Delete Customer Data]
    end

    subgraph "Notification Config"
        UC13[Create Bot Config]
        UC14[Update Bot Config]
        UC15[View Bot Config]
        UC16[Delete Bot Config]
    end

    subgraph "Message Sending"
        UC17[Send Manual Message]
        UC18[Send Manual Image]
        UC19[Process Webhook]
    end

    subgraph "Automated Processes"
        UC20[Schedule Campaign Trigger]
        UC21[Process Campaign]
        UC22[Send Automated Messages]
        UC23[Handle Conversation Flow]
        UC24[Update Campaign Status]
    end

    %% Admin use cases
    ADMIN --> UC1
    ADMIN --> UC2
    ADMIN --> UC3
    ADMIN --> UC4
    ADMIN --> UC5
    ADMIN --> UC6
    ADMIN --> UC7
    ADMIN --> UC8
    ADMIN --> UC9
    ADMIN --> UC10
    ADMIN --> UC11
    ADMIN --> UC12
    ADMIN --> UC13
    ADMIN --> UC14
    ADMIN --> UC15
    ADMIN --> UC16
    ADMIN --> UC17
    ADMIN --> UC18

    %% Tenant Admin use cases
    TENANT_ADMIN --> UC1
    TENANT_ADMIN --> UC4
    TENANT_ADMIN --> UC5
    TENANT_ADMIN --> UC7
    TENANT_ADMIN --> UC8
    TENANT_ADMIN --> UC9
    TENANT_ADMIN --> UC10
    TENANT_ADMIN --> UC11
    TENANT_ADMIN --> UC17
    TENANT_ADMIN --> UC18

    %% System automated processes
    SYSTEM --> UC20
    SYSTEM --> UC21
    SYSTEM --> UC22
    SYSTEM --> UC24

    %% FPT Chat webhook
    FPTCHAT --> UC19
    FPTCHAT --> UC23
```

### III. Danh sách các chức năng và Phân quyền

#### 3.1 Modules và Permissions

| Module | Actions | Description |
|--------|---------|-------------|
| **USER** | VIEW, EDIT, DELETE | Quản lý thông tin user |
| **ROLE_PERMISSION** | VIEW, EDIT, CREATE, DELETE | Quản lý role và permission |
| **CUSTOMER_DATA** | VIEW, EDIT, CREATE, DELETE, EXPORT | Quản lý dữ liệu khách hàng |
| **CAMPAIGN** | VIEW, EDIT, CREATE, DELETE | Quản lý campaign |
| **NOTIFICATION** | VIEW, EDIT, CREATE, DELETE, SEND | Quản lý cấu hình thông báo |
| **REPORT** | VIEW, EXPORT | Xem báo cáo |
| **CONFIG** | VIEW, EDIT, CREATE, DELETE | Quản lý cấu hình hệ thống |
| **TENANT** | VIEW, EDIT, CREATE, DELETE | Quản lý tenant (Super Admin only) |

#### 3.2 Roles mặc định

| Role | Permissions | Description |
|------|-------------|-------------|
| **Super Admin** | `__all__` | Quyền truy cập toàn bộ hệ thống |
| **Admin** | `__all__` | Quyền admin trong tenant |
| **Guest** | `user:view`, `user:edit` | Quyền hạn chế |

### IV. Các yêu cầu phi chức năng

#### 4.1 Performance Requirements
- **Response Time:** API response < 2 seconds
- **Throughput:** Hỗ trợ 1000+ concurrent users
- **Message Processing:** 10,000+ messages/minute

#### 4.2 Security Requirements
- **Authentication:** SSO với Microsoft Azure AD
- **Authorization:** Role-based access control (RBAC)
- **Data Protection:** Encryption in transit và at rest
- **Input Validation:** Pydantic schema validation

#### 4.3 Reliability Requirements
- **Availability:** 99.9% uptime
- **Data Consistency:** ACID transactions với MongoDB
- **Error Handling:** Comprehensive error logging và recovery

#### 4.4 Scalability Requirements
- **Horizontal Scaling:** Stateless workers
- **Load Balancing:** Support multiple API instances
- **Database Scaling:** MongoDB sharding support

---

## D. ĐẶC TẢ CÁC CHỨC NĂNG

### 1. Campaign Management

#### 1.1 Create Campaign (UC4)

**Business Rules (BR):**
- BR-001: Campaign name phải unique trong tenant
- BR-002: Start time phải < End time
- BR-003: Customer data phải tồn tại và thuộc cùng tenant
- BR-004: Script content phải có ít nhất 1 node start

**Technical Requirements (TR):**
- TR-001: API endpoint: `POST /v1/campaign/create_campaign`
- TR-002: Permission required: `campaign:create`
- TR-003: Input validation bằng Pydantic schema
- TR-004: Auto-generate campaign ID (ObjectId)

**Activity Diagram:**

```mermaid
graph TD
    A[Start: User tạo campaign] --> B[Validate input data]
    B --> C{Input valid?}
    C -->|No| D[Return validation error]
    C -->|Yes| E[Check permissions]
    E --> F{Has permission?}
    F -->|No| G[Return 403 Forbidden]
    F -->|Yes| H[Validate customer data exists]
    H --> I{Customer data valid?}
    I -->|No| J[Return customer data error]
    I -->|Yes| K[Create campaign in DB]
    K --> L[Set status = NEW]
    L --> M[Return success response]
    D --> N[End]
    G --> N
    J --> N
    M --> N
```

#### 1.2 Campaign Processing Workflow

**Activity Diagram - Campaign Lifecycle:**

```mermaid
graph TD
    A[Campaign Status: NEW] --> B[Schedule Worker checks time]
    B --> C{Time to run?}
    C -->|No| B
    C -->|Yes| D[Trigger NEW state handler]
    D --> E[Load customer data]
    E --> F[Set status = RUNNING]
    F --> G[Process first batch]
    G --> H[Build messages from script]
    H --> I[Send to Sender Worker]
    I --> J[Update status = WAITING]
    J --> K[Schedule Worker checks interval]
    K --> L{More customers?}
    L -->|Yes| M[Trigger WAITING state handler]
    M --> N[Process next batch]
    N --> H
    L -->|No| O[Set status = COMPLETED]
    O --> P[End]
```

### 2. Message Sending Flow

#### 2.1 Send Message to FPT Chat

**Activity Diagram:**

```mermaid
graph TD
    A[Start: Message ready to send] --> B[Get bot token from config]
    B --> C[Build message content]
    C --> D{Message type?}
    D -->|Text| E[Prepare text message]
    D -->|Image| F[Upload image first]
    D -->|Interactive| G[Prepare button options]
    E --> H[Call FPT Chat API]
    F --> I[Get image URL]
    I --> J[Prepare image message]
    J --> H
    G --> H
    H --> K{API call success?}
    K -->|Yes| L[Log success]
    K -->|No| M[Retry with backoff]
    M --> N{Retry count < max?}
    N -->|Yes| H
    N -->|No| O[Log failure]
    L --> P[Trigger done customer data]
    O --> Q[Mark customer as error]
    P --> R[End]
    Q --> R
```

### 3. Webhook Processing

#### 3.1 Handle FPT Chat Webhook

**Business Rules:**
- BR-005: Webhook phải có valid signature
- BR-006: User interaction phải trong thời gian campaign active
- BR-007: Answer phải match với available options

**Activity Diagram:**

```mermaid
graph TD
    A[Webhook received] --> B[Validate webhook signature]
    B --> C{Signature valid?}
    C -->|No| D[Return 401 Unauthorized]
    C -->|Yes| E[Extract user interaction data]
    E --> F[Validate campaign status]
    F --> G{Campaign active?}
    G -->|No| H[Send error to user]
    G -->|Yes| I[Get conversation state]
    I --> J[Validate user selection]
    J --> K{Selection valid?}
    K -->|No| L[Send invalid option message]
    K -->|Yes| M[Update interaction history]
    M --> N[Get next node from script]
    N --> O[Build next message]
    O --> P[Send next message]
    P --> Q[End]
    D --> Q
    H --> Q
    L --> Q
```

### 4. Schedule System

#### 4.1 Campaign Scheduling

**Technical Requirements:**
- TR-005: Schedule worker chạy mỗi 1 giây
- TR-006: Hỗ trợ 2 loại schedule: AT_TIME và INTERVAL
- TR-007: Timezone mặc định: Asia/Bangkok

**Activity Diagram:**

```mermaid
graph TD
    A[Schedule Worker starts] --> B[Every 1 second]
    B --> C[Get campaigns with status NEW]
    C --> D{Any campaigns?}
    D -->|No| B
    D -->|Yes| E[Check each campaign time]
    E --> F{Time to run?}
    F -->|No| G[Next campaign]
    F -->|Yes| H[Trigger campaign handler]
    H --> I[Update campaign status]
    I --> G
    G --> J{More campaigns?}
    J -->|Yes| E
    J -->|No| K[Get campaigns with status WAITING]
    K --> L{Any waiting campaigns?}
    L -->|No| B
    L -->|Yes| M[Check interval timing]
    M --> N{Time for next run?}
    N -->|No| O[Next waiting campaign]
    N -->|Yes| P[Trigger waiting handler]
    P --> O
    O --> Q{More waiting campaigns?}
    Q -->|Yes| M
    Q -->|No| B
```

### 5. Error Handling và Recovery

#### 5.1 Campaign Error Recovery

**Business Rules:**
- BR-008: Lỗi campaign phải được log và notify admin
- BR-009: Customer data lỗi không ảnh hưởng campaign khác
- BR-010: Retry mechanism với exponential backoff

**Activity Diagram:**

```mermaid
graph TD
    A[Error occurred] --> B{Error type?}
    B -->|Campaign config error| C[Set campaign status = ERROR]
    B -->|Customer data error| D[Mark customer as failed]
    B -->|API call error| E[Retry with backoff]
    C --> F[Log error details]
    D --> G[Continue with next customer]
    E --> H{Retry count < max?}
    H -->|Yes| I[Wait exponential backoff]
    I --> J[Retry operation]
    J --> K{Success?}
    K -->|Yes| L[Continue normal flow]
    K -->|No| E
    H -->|No| M[Mark as permanent failure]
    F --> N[Notify admin]
    G --> O[Check if more customers]
    M --> P[Log permanent failure]
    L --> Q[End]
    N --> Q
    O --> Q
    P --> Q
```

---

## Ghi chú cho việc triển khai

### Sơ đồ Mermaid có thể render
Các sơ đồ trên sử dụng Mermaid syntax và có thể được render trong:
- GitHub/GitLab markdown
- VS Code với Mermaid extension
- Online tools như mermaid.live
- Documentation platforms như GitBook, Notion

### Khuyến nghị phát triển tiếp
1. **Sequence Diagrams:** Thêm sequence diagrams cho API interactions
2. **State Diagrams:** Mô tả chi tiết state transitions của Campaign
3. **Component Diagrams:** Detailed architecture components
4. **Security Analysis:** Threat modeling và security requirements chi tiết
5. **Performance Testing:** Load testing scenarios và benchmarks

### Công cụ hỗ trợ vẽ sơ đồ
- **Mermaid:** Embedded trong markdown
- **Draw.io/Diagrams.net:** Export sang nhiều format
- **PlantUML:** Text-based diagrams
- **Lucidchart:** Professional diagramming tool 

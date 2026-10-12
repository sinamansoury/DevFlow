# DevFlow

[![CI](https://github.com/sinamansoury/devflow/actions/workflows/ci.yml/badge.svg)](https://github.com/sinamansoury/devflow/actions/workflows/ci.yml)

DevFlow یک سیستم مدیریت Workspace، Project و Task است. بک‌اند با Django و Django REST Framework و فرانت‌اند با React (Vite) نوشته شده است.

## Features

- ثبت‌نام و ورود با JWT (ایمیل به‌عنوان نام کاربری) و Throttle برای login و register
- مدیریت Workspace و اعضای آن
- مدیریت Project و Task
- سطح دسترسی بر اساس نقش Owner و Member
- تعیین Task به اعضای Workspace و مدیریت وضعیت (`TODO`, `IN_PROGRESS`, `DONE`)
- ثبت خودکار `finished_date` هنگام تکمیل Task
- Audit Log برای عملیات مهم (شامل حذف‌ها)
- نوتیفیکیشن اختصاص Task به کاربر؛ ساخت آن با Celery و Redis و بعد از commit تراکنش انجام می‌شود
- Filtering، Searching، Ordering و Pagination
- مستندات Swagger / OpenAPI
- تست‌های خودکار با pytest و CI با GitHub Actions (روی PostgreSQL)
- اجرای کامل پروژه با Docker Compose (PostgreSQL، Redis، Celery worker و Flower)
- تست بار با Locust

## Technologies

- Backend: Python, Django, Django REST Framework, Simple JWT, django-filter, drf-spectacular
- Database / Queue: PostgreSQL, Redis, Celery, Flower
- Frontend: React, Vite, React Router, Axios
- Tooling: pytest, pytest-django, ruff, Docker Compose, Locust, GitHub Actions

## Project Structure

```text
DevFlow/
├── backend/
│   ├── audit/
│   ├── config/
│   │   ├── celery.py
│   │   └── settings/
│   │       ├── base.py
│   │       ├── development.py
│   │       └── production.py
│   ├── notifications/
│   ├── project/
│   ├── task/
│   ├── users/
│   ├── workspace/
│   ├── .env.example
│   ├── Dockerfile
│   ├── conftest.py
│   ├── manage.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
├── compose.yaml
├── locustfile.py
└── .github/workflows/ci.yml
```

## Getting Started

```bash
git clone https://github.com/sinamansoury/devflow.git
cd devflow
```

### روش اول: Docker Compose (پیشنهادی)

```bash
cp backend/.env.example backend/.env   # SECRET_KEY و DB_PASSWORD را تغییر بده
docker compose up --build
```

سرویس‌ها:

| Service | Address | Description |
| --- | --- | --- |
| web | `http://127.0.0.1:8000` | Django API (با اجرای خودکار `migrate`) |
| db | `127.0.0.1:5433` | PostgreSQL 16 |
| redis | داخلی | Broker و result backend برای Celery |
| worker | داخلی | Celery worker برای ساخت نوتیفیکیشن‌ها |
| flower | `http://127.0.0.1:5555` | مانیتورینگ Celery |

این تنظیمات برای توسعه است و سرور `runserver` استفاده می‌شود؛ برای production باید از Gunicorn و تنظیمات `production.py` استفاده شود.

### روش دوم: اجرای محلی

برای اجرای محلی به یک PostgreSQL در دسترس و (برای نوتیفیکیشن‌ها) یک Redis نیاز است.

```bash
cd backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
cp .env.example .env             # مقدارهای SECRET_KEY و DB_* را تنظیم کن

python manage.py migrate
python manage.py runserver

# در ترمینال دیگر، برای نوتیفیکیشن‌ها:
celery -A config worker --loglevel=info
```

API در آدرس `http://127.0.0.1:8000/` در دسترس است. فایل `.env` باید داخل پوشه‌ی `backend/` باشد؛ نمونه‌ی آن در `backend/.env.example` است. برای اجرای محلی بدون Docker مقدار `DB_HOST` را `localhost` بگذار.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

فرانت‌اند درخواست‌های `/api` را از طریق proxy ی Vite به `http://127.0.0.1:8000` می‌فرستد، پس بک‌اند باید در حال اجرا باشد.

## API Documentation

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

## Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/register/` | ساخت حساب کاربری |
| POST | `/api/auth/login/` | دریافت Access Token و Refresh Token |
| POST | `/api/auth/refresh/` | دریافت Access Token جدید |
| GET | `/api/auth/me/` | اطلاعات کاربر فعلی |

سایر endpointها نیاز به هدر `Authorization: Bearer <access_token>` دارند.
Access Token ۳۰ دقیقه و Refresh Token ۷ روز اعتبار دارد.

## Resources and Permissions

| Resource | Prefix | Owner | Member |
| --- | --- | --- | --- |
| Workspace | `/api/workspaces/` | ایجاد، ویرایش، حذف، مدیریت اعضا | مشاهده |
| Project | `/api/projects/` | ایجاد، ویرایش، حذف | مشاهده |
| Task | `/api/tasks/` | ایجاد، ویرایش، حذف، تعیین مسئول | مشاهده و تغییر `status` |
| Audit Log | `/api/audits/` | مشاهده‌ی تاریخچه‌ی Workspaceهای خود | — |
| Notification | `/api/notifications/` | مشاهده و علامت‌گذاری نوتیفیکیشن‌های خود به‌عنوان خوانده‌شده | مشاهده و علامت‌گذاری نوتیفیکیشن‌های خود به‌عنوان خوانده‌شده |

نکات:

- Project با `POST /api/projects/workspace/<workspace_id>/` ساخته می‌شود و Task با `POST /api/tasks/projects/<project_id>/` ساخته می‌شود.
- با تغییر وضعیت Task به `DONE` مقدار `finished_date` خودکار ثبت می‌شود و با خروج از `DONE` پاک می‌شود.
- با حذف یک عضو از Workspace، Taskهای او به Owner منتقل می‌شوند.

## Filtering, Search and Ordering

```text
/api/tasks/?status=TODO
/api/tasks/?project=1&assigned_to=2
/api/tasks/?search=login
/api/tasks/?ordering=-created_at
/api/tasks/?page=2
/api/audits/?entity_type=TASK&action=DELETE
```

## Audit Log

عملیات مهم زیر ثبت می‌شوند: ایجاد، ویرایش و حذف Workspace، Project و Task، افزودن و حذف عضو، و تغییر وضعیت Task.

هر رکورد شامل `user`، `entity_type`، `entity_id`، `entity_name`، `action`، `old_value`، `new_value` و `created_at` است. شناسه‌ی Workspace هم روی خود لاگ ذخیره می‌شود، بنابراین تاریخچه‌ی موجودیت‌های حذف‌شده برای Owner قابل مشاهده می‌ماند.

## Testing

```bash
cd backend
pytest
ruff check .
```

تست‌ها روی PostgreSQL اجرا می‌شوند و CI هم روی هر push و pull request همین کار را با یک سرویس PostgreSQL انجام می‌دهد.

## Load Testing

```bash
pip install locust
DEVFLOW_EMAIL=you@example.com DEVFLOW_PASSWORD=your-password \
  locust -f locustfile.py --host http://127.0.0.1:8000
```

## License

This project is developed for educational and portfolio purposes.

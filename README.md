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
- Filtering، Searching، Ordering و Pagination
- مستندات Swagger / OpenAPI
- تست‌های خودکار با pytest و CI با GitHub Actions

## Technologies

- Backend: Python, Django, Django REST Framework, Simple JWT, django-filter, drf-spectacular, SQLite
- Frontend: React, Vite, React Router, Axios
- Tooling: pytest, pytest-django, ruff, GitHub Actions

## Project Structure

```text
DevFlow/
├── backend/
│   ├── audit/
│   ├── config/
│   │   └── settings/
│   │       ├── base.py
│   │       ├── development.py
│   │       └── production.py
│   ├── project/
│   ├── task/
│   ├── users/
│   ├── workspace/
│   ├── conftest.py
│   ├── manage.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
└── .github/workflows/ci.yml
```

## Getting Started

### Backend

```bash
git clone https://github.com/sinamansoury/devflow.git
cd devflow/backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
cp .env.example .env             # then set a real SECRET_KEY

python manage.py migrate
python manage.py runserver
```

API در آدرس `http://127.0.0.1:8000/` در دسترس است.

فایل `.env` باید داخل پوشه‌ی `backend/` باشد:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

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

## License

This project is developed for educational and portfolio purposes.

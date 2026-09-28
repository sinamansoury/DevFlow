\# DevFlow



DevFlow یک REST API برای مدیریت Workspace، Project و Task است که با Django و Django REST Framework توسعه داده شده است.



این پروژه شامل احراز هویت JWT، سیستم سطح دسترسی، مدیریت اعضای Workspace، فیلتر و جستجو، Pagination، مرتب‌سازی و ثبت Audit Log برای فعالیت‌های مهم است.



\## Features



\* ثبت‌نام و ورود کاربران

\* احراز هویت با JWT

\* مدیریت Workspace

\* مدیریت اعضای Workspace

\* مدیریت Project

\* مدیریت Task

\* سیستم Permission بر اساس Owner و Member

\* تعیین Task به اعضای Workspace

\* مدیریت وضعیت Task

\* ثبت خودکار `finished\_date` هنگام تکمیل Task

\* Audit Log برای عملیات مهم

\* Filtering

\* Searching

\* Ordering

\* Pagination

\* Swagger / OpenAPI documentation



\## Technologies



\* Python

\* Django

\* Django REST Framework

\* Simple JWT

\* Django Filter

\* drf-spectacular

\* SQLite



\## Project Structure



```text

DevFlow/

├── audit/

├── config/

│   └── settings/

│       ├── base.py

│       ├── development.py

│       └── production.py

├── project/

├── task/

├── users/

├── workspace/

├── manage.py

├── requirements.txt

├── .env

└── .env.example

```



\## Installation



\### 1. Clone the repository



```bash

git clone <repository-url>

cd DevFlow

```



\### 2. Create a virtual environment



Windows:



```bash

python -m venv .venv

```



Activate it:



```bash

.venv\\Scripts\\activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file in the project root:



```env

SECRET\_KEY=your-secret-key

DEBUG=True

```



برای محیط واقعی، مقدار `SECRET\_KEY` باید یک مقدار امن و غیرقابل حدس باشد.



\### 5. Run migrations



```bash

python manage.py migrate

```



\### 6. Run the development server



```bash

python manage.py runserver

```



API در آدرس زیر در دسترس خواهد بود:



```text

http://127.0.0.1:8000/

```



\## API Documentation



مستندات API با Swagger و OpenAPI در دسترس است:



```text

http://127.0.0.1:8000/api/docs/

```



Schema:



```text

http://127.0.0.1:8000/api/schema/

```



در Swagger می‌توان Endpointها را مشاهده و مستقیماً تست کرد.



\## Authentication



احراز هویت API با JWT انجام می‌شود.



\### Register



```text

POST /api/auth/register/

```



برای ساخت حساب کاربری جدید.



\### Login



```text

POST /api/auth/login/

```



برای دریافت:



\* Access Token

\* Refresh Token



\### Refresh Token



```text

POST /api/auth/refresh/

```



برای دریافت Access Token جدید.



\### Current User



```text

GET /api/auth/me/

```



برای دریافت اطلاعات کاربر فعلی.



Endpointهای محافظت‌شده نیاز به JWT Access Token دارند.



\## Workspace



Workspace محیط اصلی سازماندهی Projectها و Taskها است.



Owner می‌تواند:



\* Workspace را ایجاد کند.

\* Workspace را ویرایش کند.

\* Workspace را حذف کند.

\* اعضا را اضافه کند.

\* اعضا را حذف کند.

\* اعضای Workspace را مشاهده کند.



Member می‌تواند Workspaceهایی را که به آن دسترسی دارد مشاهده کند.



\## Project



هر Project متعلق به یک Workspace است.



Owner Workspace می‌تواند:



\* Project ایجاد کند.

\* Project را ویرایش کند.

\* Project را حذف کند.



اعضای Workspace می‌توانند Projectها را مشاهده کنند.



Projectها از امکانات زیر پشتیبانی می‌کنند:



\* Filtering بر اساس Workspace

\* Search بر اساس نام و توضیحات

\* Ordering

\* Pagination



\## Task



Taskها به Project متصل هستند.



Owner Workspace می‌تواند:



\* Task ایجاد کند.

\* Task را ویرایش کند.

\* Task را حذف کند.

\* Task را به اعضای Workspace یا Owner اختصاص دهد.



Member می‌تواند Taskها را مشاهده کند و وضعیت Task را تغییر دهد.



Taskها از امکانات زیر پشتیبانی می‌کنند:



\* Filtering بر اساس Status

\* Filtering بر اساس Project

\* Filtering بر اساس Assigned User

\* Search بر اساس Title و Description

\* Ordering

\* Pagination



هنگام تغییر Status به `DONE`، مقدار `finished\_date` به صورت خودکار ثبت می‌شود.



در صورت خارج شدن Task از وضعیت `DONE`، مقدار `finished\_date` حذف می‌شود.



\## Audit Log



فعالیت‌های مهم سیستم در Audit Log ثبت می‌شوند.



از جمله:



\* ایجاد Workspace

\* ویرایش Workspace

\* حذف Workspace

\* اضافه کردن Member

\* حذف Member

\* ایجاد Project

\* ویرایش Project

\* حذف Project

\* ایجاد Task

\* ویرایش Task

\* تغییر وضعیت Task

\* حذف Task



Audit Log شامل اطلاعاتی مانند:



\* User

\* Entity Type

\* Entity ID

\* Entity Name

\* Action

\* Old Value

\* New Value

\* Created At



است.



\## Filtering, Search and Ordering



API از Filtering، Search و Ordering پشتیبانی می‌کند.



مثال:



```text

/api/tasks/?status=TODO

```



Search:



```text

/api/tasks/?search=login

```



Ordering:



```text

/api/tasks/?ordering=-created\_at

```



Pagination:



```text

/api/tasks/?page=2

```



\## Permissions



سطح دسترسی‌ها بر اساس نقش کاربر در Workspace کنترل می‌شود.



\### Workspace Owner



Owner می‌تواند Workspace و منابع مربوط به آن را مدیریت کند.



\### Workspace Member



Member می‌تواند منابع Workspace را مشاهده کند و بر اساس قوانین هر resource عملیات مجاز را انجام دهد.



برای مثال، در Task، Member فقط مجاز به تغییر Status است.



تمام Endpointهای محافظت‌شده نیاز به احراز هویت دارند.



\## Development



برای اجرای پروژه در محیط توسعه:



```bash

python manage.py runserver

```



برای ساخت migration در صورت تغییر مدل‌ها:



```bash

python manage.py makemigrations

```



و سپس:



```bash

python manage.py migrate

```



\## Testing



برای اجرای تست‌ها:



```bash

python manage.py test

```



\## License



This project is developed for educational and portfolio purposes.




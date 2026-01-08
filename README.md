# Django REST API Project

A scalable REST API built with **Django 5**, **Django REST Framework**, and **MySQL**, featuring JWT authentication, CORS support, auto-generated API documentation (Swagger), and static file serving with Whitenoise.

---

## 🚀 Features

- Django 5.x + DRF 3.16.x
- JWT authentication (`djangorestframework-simplejwt`)
- Swagger / ReDoc API docs (`drf-yasg`)
- MySQL database integration
- CORS support for cross-origin requests
- Production-ready with Gunicorn + Whitenoise
- Image handling with Pillow

---

## 🛠️ Tech Stack

| Category | Tool |
|-----------|------|
| Framework | Django 5.2.1 |
| API Layer | Django REST Framework |
| Auth | SimpleJWT |
| DB | MySQL (via `mysqlclient`) |
| Docs | drf-yasg (Swagger / ReDoc) |
| Static Files | Whitenoise |
| Deployment | Gunicorn |
| Misc | PyYAML, inflection, pillow |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject

2️⃣ Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  
3️⃣ Install dependencies
pip install -r requirements.txt
🗄️ Database Setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

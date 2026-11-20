# Smart Lost & Found Platform - Backend API

AI-Powered Django REST Framework Backend with Pretrained CLIP Vision Transformers, MySQL 8.4, Simple JWT Authentication, and Haversine Proximity Search.

## Features
- **JWT Authentication & RBAC:** General User, Item Finder, and Administrator roles.
- **AI Matching Engine:** Pretrained CLIP (`openai/clip-vit-base-patch32`) generating 512-dimensional visual embeddings, cosine similarity, and multi-factor weighted scoring.
- **Geospatial Proximity:** OpenStreetMap coordinates and Haversine distance calculations.
- **Confidential Claims:** Secure ownership verification workflow with private identifying answers redacted from public viewing.
- **Automated Notifications:** In-app notification center and email notification dispatchers.
- **Admin Dashboard:** Platform metrics, user privilege management, and audit logging.

## Tech Stack
- Python 3.10+ (tested on Python 3.14)
- Django 6.1.1
- Django REST Framework 3.18.1
- Simple JWT 5.5.1
- MySQL 8.4 Server
- PyTorch 2.15.0 & Hugging Face Transformers 5.22.2
- drf-spectacular 0.30.0 (Swagger/OpenAPI 3.0)

## Quick Start Guide

### 1. Configure Environment
Copy `.env.example` to `.env` and set your MySQL credentials:
```powershell
cp .env.example .env
```

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=smart_loss_database
DB_USER=root
DB_PASSWORD=2008
DB_HOST=localhost
DB_PORT=3306

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Database Migrations
```powershell
python manage.py migrate
```

### 4. Seed Database with Demonstration Records
```powershell
python manage.py seed_data
```

### 5. Start Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```
- API Base URL: `http://127.0.0.1:8000/api/`
- Interactive Swagger UI: `http://127.0.0.1:8000/api/docs/`
- Redoc Documentation: `http://127.0.0.1:8000/api/redoc/`
- Admin Panel: `http://127.0.0.1:8000/admin/`

## Testing
Run automated unit and integration tests:
```powershell
python manage.py test accounts lost_items found_items ai_matching claims dashboard
```

# Kanban Backend (Django + DRF)

Simple backend API for a Kanban board application built with Django and Django REST Framework.

## Features
- User registration & login (token authentication)
- Board management (owner + members)
- Task management (status, priority, assignment, review)
- Comment system
- Permission system (board members, owners, task creators)

## Tech Stack
- Python >=3.12
- Django == 6.0.3
- Django REST Framework == 3.17.1

## Setup
1. Clone project
```bash
git clone https://github.com/lucas-hmchr/kanmind
cd kanmind
```

2. Create virtual environment
```bash
python -m venv venv
```

Activate:
Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser (optional)
```bash
python manage.py createsuperuser
```

6. Start server
```bash
python manage.py runserver
```

API:
http://127.0.0.1:8000/api/

Admin:
http://127.0.0.1:8000/admin/

## Authentication
After registration or login you receive a token.

Use it like this:
Authorization: Token <your_token>

## API Endpoints

Auth
POST /api/registration
POST /api/login

Boards
GET /api/boards/
POST /api/boards/
GET /api/boards/{id}/
PATCH /api/boards/{id}/
DELETE /api/boards/{id}/

Tasks
GET /api/tasks/assigned-to-me/
GET /api/tasks/reviewing/
POST /api/tasks/
GET /api/tasks/{id}/
PATCH /api/tasks/{id}/
DELETE /api/tasks/{id}/

Comments
GET /api/tasks/{task_id}/comments/
POST /api/tasks/{task_id}/comments/
DELETE /api/tasks/{task_id}/comments/{comment_id}/

## Notes
- Only authenticated users can access most endpoints
- Users only see boards where they are owner or member
- Only board owners can delete boards
- Only task creators or board owners can delete tasks
- Only comment authors can delete comments

Backend learning project with Django & DRF 🚀
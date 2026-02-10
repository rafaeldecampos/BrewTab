# BrewTab - Brewery Management & Quality Control System

A Django-based web application for managing brewery production processes, quality control, HACCP compliance, and non-conformity tracking.

## Stage 1: Base Project Architecture ✅

This is **Stage 1** of the BrewTab project, covering:
- ✅ Django 4.2 project setup
- ✅ Application organization (brewery, processes apps)
- ✅ User authentication system
- ✅ Brewery model with user ownership
- ✅ Complete navigation interface
- ✅ HTML templates with consistent styling

## Project Structure

```
BrewTab/
├── brewtab_config/          # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── views.py
├── brewery/                 # Brewery management app
│   ├── models.py            # Brewery model
│   ├── views.py             # Brewery views (FBV)
│   ├── urls.py              # Brewery URL routes
│   ├── admin.py             # Brewery admin configuration
│   └── migrations/
├── processes/               # Processes app (reserved for Stage 2)
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Homepage
│   ├── auth/                # Authentication templates
│   │   ├── login.html
│   │   └── signup.html
│   └── brewery/             # Brewery templates
│       ├── brewery_list.html
│       ├── brewery_detail.html
│       ├── brewery_form.html
│       └── brewery_confirm_delete.html
├── manage.py
├── requirements.txt
└── db.sqlite3               # Database file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Windows, macOS, or Linux

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser (Optional, for admin access)
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Default Admin Credentials (for testing)
- **Username**: admin
- **Password**: admin123
- **Admin URL**: http://127.0.0.1:8000/admin/

## Features in Stage 1

### User Registration & Authentication
- Sign up new users
- Login/Logout functionality
- Protected views (login required)
- User-specific brewery isolation

### Brewery Management
- **Create**: Add new breweries (name required, unique)
- **Read**: List all user's breweries with details
- **Update**: Edit brewery information
- **Delete**: Remove breweries with confirmation
- View details: See full brewery information
- Permission control: Users can only see/edit their own breweries

### Navigation Flow
```
Home (/)
├── Login (/login)
├── Sign Up (/signup)
└── Breweries (/brewery/)
    ├── List all breweries
    ├── Create new brewery
    ├── View brewery details
    ├── Edit brewery
    └── Delete brewery
```

## Database Schema - Stage 1

### User Model (Django built-in)
- id
- username
- email
- password
- first_name
- last_name

### Brewery Model
```python
class Brewery:
    - id (PK)
    - name (CharField, unique)
    - owner (ForeignKey → User)
    - created_at (DateTimeField, auto_now_add)
    - updated_at (DateTimeField, auto_now)
```

## Key Design Decisions

1. **Function-Based Views (FBV)**: Chosen for simplicity and clarity at this stage
2. **Simple HTML Templates**: No JavaScript framework; pure HTML + CSS for rapid development
3. **SQLite Database**: Perfect for development; easily upgradeable to PostgreSQL for production
4. **User Isolation**: Each user sees only their own breweries (enforced by `owner=request.user` queries)
5. **Responsive CSS**: Mobile-friendly styling with gradient background
6. **REST-like URLs**: Clear URL patterns (`/brewery/`, `/brewery/<id>/`, `/brewery/<id>/edit/`)

## Coming in Future Stages

- **Stage 2**: Process (SOP) management and process steps
- **Stage 3**: Process execution and automated checklists
- **Stage 4**: Step execution tracking
- **Stage 5**: HACCP Point definitions and critical control points
- **Stage 6**: Non-Conformity (NC) management
- **Stage 7**: Corrective Actions (CAPA) workflow
- **Stage 8**: Dashboard and reporting
- **Advanced Features**: PDF reports, email notifications, trend analysis

## Code Quality Standards

- Clean, readable code with meaningful variable names
- DRY principle applied throughout
- Database queries optimized with `select_related`/`prefetch_related`
- Comments only where logic complexity warrants
- Consistent template architecture
- Permission checks on all user-specific views

## Testing the Application

### User Registration Flow
1. Go to http://127.0.0.1:8000/signup/
2. Create a new user account
3. You'll be redirected to brewery list (empty initially)

### Brewery Creation Flow
1. Click "Create New Brewery" button
2. Enter brewery name and submit
3. View details, edit, or delete the brewery

### Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Manage brewery records directly from admin interface

## Notes

- Messages system is integrated for user feedback on all actions
- Permission checks prevent unauthorized access to other users' breweries
- All HTML forms use Django CSRF protection
- Database queries are logged during development (DEBUG=True)

---

**Author**: Built according to senior software architecture principles for industrial brewery operations.  
**Framework**: Django 4.2 | **Database**: SQLite | **Python**: 3.10+ | **Status**: Stage 1 Complete ✅

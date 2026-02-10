# BrewTab Architecture Documentation - Stage 1

## Technical Overview

### Technology Stack
- **Framework**: Django 4.2.0
- **Database**: SQLite (development) - easily upgradeable to PostgreSQL
- **Frontend**: Pure HTML5 + CSS3 (no JavaScript framework)
- **View Pattern**: Function-Based Views (FBV)
- **Authentication**: Django's built-in authentication system

### Project Organization

```
brewtab_config/     → Main Django project configuration
brewery/            → Brewery management application
processes/          → Processes & SOP management (reserved)
templates/          → All HTML templates
  ├── base.html     → Master template (styling + navigation)
  ├── home.html     → Public homepage
  ├── auth/         → Login/Signup pages
  └── brewery/      → Brewery CRUD pages
```

## Core Models - Stage 1

### Brewery Model
```python
class Brewery(models.Model):
    name = CharField(max_length=255, unique=True)
    owner = ForeignKey(User, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Why this structure?**
- `name`: Unique identifier for brewery, prevents duplicates
- `owner`: FK to User ensures each brewery has one owner
- `on_delete=CASCADE`: If user deleted, breweries deleted too
- `created_at/updated_at`: Audit trail for compliance

## View Patterns - Stage 1

All views follow this pattern:
1. **Authentication Check**: `@login_required` decorator
2. **Permission Check**: Verify `brewery.owner == request.user`
3. **Action**: Create/Read/Update/Delete operation
4. **Feedback**: Messages system for user feedback
5. **Redirect**: To appropriate next page or list

### View List
- `brewery_list()` → GET all user breweries
- `brewery_detail()` → GET single brewery
- `brewery_create()` → GET form + POST create
- `brewery_edit()` → GET form + POST update
- `brewery_delete()` → GET confirmation + POST delete
- `signup_view()` → GET form + POST new user

## URL Structure - REST-like

```
/                       → Home page
/login/                → Django login view
/logout/               → Django logout view
/signup/               → Custom signup view
/brewery/              → List all user's breweries
/brewery/create/       → Create new brewery form
/brewery/<id>/         → View brewery details
/brewery/<id>/edit/    → Edit brewery form
/brewery/<id>/delete/  → Delete confirmation
/admin/                → Django admin panel
```

## Template Architecture

### Template Inheritance
```
base.html (master template)
├── header with navigation
├── messages display
├── main content block
├── footer
└── consistent styling (CSS in <head>)
```

**CSS Strategy:**
- All CSS in base.html `<style>` tag
- Responsive grid layout (mobile-first)
- Gradient background with card-based content
- Color scheme: Purple (#667eea, #764ba2), clean white content areas

### Template Reuse
- `brewery_form.html`: Used for both create AND edit (via `action` context variable)
- `base.html`: Inherited by all application templates
- Consistent button styles, form layouts, and messaging

## Authentication Flow

### Registration (Sign Up)
1. User submits form with username, email, password
2. Validation checks for:
   - Username uniqueness
   - Email uniqueness
   - Password requirements (min 8 chars)
   - Password confirmation match
3. User created with hashed password
4. Auto-login after registration
5. Redirect to brewery list

### Login
1. Django's built-in LoginView
2. Authenticates against User model
3. Session created
4. Redirect to `LOGIN_REDIRECT_URL` = `/brewery/`

### Access Control
- `@login_required` on all brewery views
- Permission check: `if brewery.owner != request.user: return HttpResponseForbidden`
- Database queries filtered by `owner=request.user`

## Database Schema Notes

### Foreign Key Relationships
- `Brewery.owner` → `User` (many breweries per user, each brewery owned by one user)
- Future: `Process.brewery` → `Brewery` (one brewery, many processes)

### Indexes (implicit)
- User ID (PK in auth_user)
- Brewery ID (PK)
- Brewery.owner (FK, auto-indexed)
- Brewery.name (unique field, auto-indexed)

## Key Design Decisions

### Why FBV instead of CBV?
- **Simplicity**: Easier to understand for developers starting on project
- **Flexibility**: More control over exact behavior
- **Explicit**: No "magic" happening in class inheritance chains
- **Incremental**: Easy to add logic step-by-step

### Why pure HTML instead of React/Vue?
- **Server-side rendering**: Django templates handle all rendering
- **No API complexity**: Simple form submissions, no JSON APIs yet
- **Fast development**: No build process, no Node.js dependencies
- **Accessibility**: HTML first, all data in DOM
- **Future-proof**: Can add JS/HTMX later without refactoring templates

### Why SQLite for development?
- **Zero setup**: Included with Python
- **Database as single file**: Easy to backup, reset, version control
- **Perfect for development**: Can handle any query pattern we'll use
- **Production upgrade path**: Simple migration to PostgreSQL in Stage 8

### Why `owner` field in Brewery?
- **Isolation**: Each user sees only their data
- **Compliance**: Audit trail of who owns what
- **Multi-tenancy**: Simple multi-tenancy without third-party tools
- **Future**: Can be extended to `team_owner` later

## Permission Model

```
User ─┬→ owns multiple Breweries
      ├→ queries filtered by: Brewery.objects.filter(owner=request.user)
      └→ can only view/edit/delete own breweries

Superuser (admin)
      ├→ can see all breweries via admin panel
      └→ can manage users and permissions
```

## Code Quality Practices

### Query Optimization (for future stages)
- Use `select_related()` for FK relationships
- Use `prefetch_related()` for reverse FK relationships
- Example (not yet needed): `Brewery.objects.select_related('owner').all()`

### Error Handling
- 404 errors: `get_object_or_404()` (raises 404 if not found)
- 403 errors: `HttpResponseForbidden()` (for permission denied)
- Validation errors: Stored in context, displayed in template

### Messages Framework
- Success: "Brewery created successfully" → green alert
- Error: "Brewery with this name already exists" → red alert
- Messages auto-removed after display

## Scalability Considerations for Future Stages

### Database Growth
- Brewery table: Can handle millions (indexed on owner, name)
- Queue query optimization when we add many related objects

### Process Model (Stage 2)
```python
class Process(models.Model):
    brewery = ForeignKey(Brewery)
    name = CharField()
    category = CharField(choices=[...])
```

### Process Execution (Stage 4)
```python
class ProcessExecution(models.Model):
    process = ForeignKey(Process)
    started_at = DateTimeField()
```

These models will follow the same ownership pattern:
- User owns Brewery
- Brewery has Processes
- User can only see/execute Processes they have access to (via brewery)

## Testing Checklist - Stage 1

To verify Stage 1 is complete:

- [ ] User can sign up with valid credentials
- [ ] User can login with correct password
- [ ] Login with wrong password fails
- [ ] Logged-in user sees their breweries (empty initially)
- [ ] User can create brewery with unique name
- [ ] Duplicate brewery name shows error
- [ ] User can view brewery details
- [ ] User can edit brewery name
- [ ] User can delete brewery (with confirmation)
- [ ] User A cannot see User B's breweries
- [ ] User A cannot edit User B's brewery (404)
- [ ] Logout works correctly
- [ ] Navigation bar shows appropriate links (auth status)
- [ ] Admin panel works with credentials
- [ ] All forms have CSRF protection
- [ ] Messages display correctly (success/error)

## Next Steps - Stage 2

After Stage 1 is validated:

1. **Create Process Model**
   ```python
   class Process(models.Model):
       brewery = ForeignKey(Brewery)
       name = CharField()
       category = CharField(choices=['produção', 'limpeza', 'envase', 'qualidade'])
   ```

2. **Create Views**
   - `process_list(brewery_id)` - show processes for a brewery
   - `process_create(brewery_id)` - create process in brewery
   - `process_detail(brewery_id, process_id)` - view process

3. **Create Templates**
   - `process_list.html` - list processes
   - `process_form.html` - create/edit process
   - `process_detail.html` - process details

4. **Update Navigation**
   - Brewery detail should link to "View Processes"
   - Get all processes for a brewery

5. **Database Migration**
   - `makemigrations` and `migrate`

## Monitoring & Debugging

### Django Debug Mode
- `DEBUG = True` in settings.py (development only)
- Shows detailed error pages with traceback
- SQL queries logged using `django.db.connection.queries`

### Admin Panel
- Access at `/admin/` with superuser credentials
- Create test users
- View/edit breweries directly
- User permissions management

### Django Shell for Testing
```bash
python manage.py shell
>>> from brewery.models import Brewery
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.breweries.all()
```

---

**Stage 1 Complete**: Base project, authentication, and basic CRUD operations are fully functional and navigable.

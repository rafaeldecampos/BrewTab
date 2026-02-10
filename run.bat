@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting BrewTab Django development server...
echo Access the application at: http://127.0.0.1:8000/
echo.
echo Admin panel: http://127.0.0.1:8000/admin/
echo Admin username: admin
echo Admin password: (create with: python manage.py createsuperuser)
echo.

python manage.py runserver

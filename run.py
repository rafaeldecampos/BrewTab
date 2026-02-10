#!/usr/bin/env python
"""
BrewTab Development Server Launcher
Launch the Django development server with helpful information.
"""
import os
import sys
import subprocess

def main():
    # Add current directory to path
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "="*60)
    print("BrewTab - Brewery Management System".center(60))
    print("="*60 + "\n")
    
    print("Starting Django development server...")
    print("\nAccess the application at:")
    print("  → http://127.0.0.1:8000/")
    print("\nAdmin panel:")
    print("  → http://127.0.0.1:8000/admin/")
    print("  Username: admin (if created)")
    print("  Password: (create with: python manage.py createsuperuser)")
    print("\nPress Ctrl+C to stop the server.\n")
    print("="*60 + "\n")
    
    # Run the Django development server
    subprocess.run([
        sys.executable, 
        'manage.py', 
        'runserver'
    ])

if __name__ == '__main__':
    main()

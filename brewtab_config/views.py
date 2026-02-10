from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages


def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        errors = {}
        
        if not username:
            errors['username'] = 'Username is required.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
        
        if not email:
            errors['email'] = 'Email is required.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists.'
        
        if not password:
            errors['password'] = 'Password is required.'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        
        if password != password_confirm:
            errors['password_confirm'] = 'Passwords do not match.'
        
        if errors:
            return render(request, 'auth/signup.html', {'errors': errors, 'username': username, 'email': email})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('home')
    
    return render(request, 'auth/signup.html')


def custom_404(request, exception):
    """Custom 404 error handler."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error handler."""
    return render(request, '500.html', status=500)


def custom_403(request, exception=None):
    """Custom 403 error handler."""
    return render(request, '403.html', status=403)

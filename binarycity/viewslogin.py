from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('client_list')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('client_list')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    return render(request, 'binarycity/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

from django.shortcuts import redirect, render
from .forms import UserRegistrationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

def register(request):
    # We don't want authenticated users to access registration page
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            messages.success(request, f'Account created for: {username}')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def log_in(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # attempt to authenticate the user
        user = authenticate(request, username=username, password=password)

        # if authentication was successful, redirect to the dashboard
        if user is not None:
            login(request, user)
            return redirect('list_website_reports')
        else:
            messages.info(request, 'Username or password is incorrect.')
    return render(request, 'accounts/login.html')

def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('home')
    logout(request)
    return redirect('home')



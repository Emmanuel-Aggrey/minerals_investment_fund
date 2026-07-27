from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def login_view(request):
    if request.user.is_authenticated:
        return redirect('visitor:dashboard')
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', 'visitor:dashboard'))
        error = 'Invalid email or password.'
    return render(request, 'login.html', {'error': error})


def logout_view(request):

    if request.method == 'POST':

        logout(request)
        return redirect('accounts:login')
    return redirect('visitor:dashboard')

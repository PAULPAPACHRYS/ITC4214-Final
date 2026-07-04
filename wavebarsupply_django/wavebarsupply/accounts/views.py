from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def auth_view(request):
    """Single page hosting both the login and register forms (tabbed UI).

    Uses Django's built-in auth: login() sets up the session, and request.user
    is available in templates.
    """
    login_form = LoginForm(request)
    register_form = RegisterForm()
    active_panel = 'login'

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            active_panel = 'login'
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('catalogue:browse')

        elif 'register_submit' in request.POST:
            register_form = RegisterForm(request.POST)
            active_panel = 'register'
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('catalogue:browse')

    return render(request, 'accounts/login.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_panel': active_panel,
    })


def logout_view(request):
    logout(request)
    return redirect('home:index')

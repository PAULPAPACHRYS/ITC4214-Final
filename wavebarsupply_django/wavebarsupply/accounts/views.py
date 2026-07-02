from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def auth_view(request):
    """Single page that hosts both the login and register forms (tabbed UI)."""
    login_form = LoginForm(request)
    register_form = RegisterForm()
    active_panel = 'login'

    if request.method == 'POST':
        # The two submit buttons are named so we know which form was sent.
        if 'login_submit' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('catalogue:browse')
            active_panel = 'login'

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

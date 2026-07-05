from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import AccountEditForm, LoginForm, RegisterForm


def auth_view(request):
    """Login + register page (for guests). Logged-in users are sent to Account."""
    if request.user.is_authenticated:
        return redirect('accounts:account')

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


@login_required
def account(request):
    """Shows the logged-in user's details and lets them edit them."""
    show_edit = False
    if request.method == 'POST':
        form = AccountEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:account')
        show_edit = True          # keep the edit form open to show errors
    else:
        form = AccountEditForm(instance=request.user)

    return render(request, 'accounts/account.html', {
        'form': form,
        'show_edit': show_edit,
    })


def logout_view(request):
    logout(request)
    return redirect('home:index')

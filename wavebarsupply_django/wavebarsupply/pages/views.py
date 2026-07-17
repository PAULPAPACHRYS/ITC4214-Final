from django.shortcuts import render
from .forms import ContactForm


def about(request):
    return render(request, 'pages/about.html')


def not_found(request, exception=None):
    """
    the 'page does not exist' page
    for anything that raises Http404 and for an address that matches no page at all
    """
    return render(request, 'pages/404.html', status=404)


def contact(request):
    submitted = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form = ContactForm()
            submitted = True
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form, 'submitted': submitted})

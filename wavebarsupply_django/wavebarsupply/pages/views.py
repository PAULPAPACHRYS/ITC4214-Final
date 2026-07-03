from django.shortcuts import render
from .forms import ContactForm


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    submitted = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # A real site would email or store this; here we just confirm receipt
            # and hand back a fresh, empty form.
            form = ContactForm()
            submitted = True
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form, 'submitted': submitted})

from django.shortcuts import render
from .forms import ContactForm


def about(request):
    return render(request, 'pages/about.html')


def not_found(request, exception=None):
    """The 'page does not exist' page.

    Used in two ways (see wavebarsupply/urls.py):
      * as Django's handler404, for anything that raises Http404;
      * as the catch-all at the end of the URL list, for an address that matches
        no page at all - which is the case when someone types a wrong address by
        hand instead of clicking a link.

    `exception` is passed in by Django when it is used as handler404, and is not
    passed by the catch-all, so it has a default.

    status=404 matters: the page must actually TELL the browser it was not found.
    Rendering it with a normal 200 would claim the page was found, which would
    mislead browsers and search engines.
    """
    return render(request, 'pages/404.html', status=404)


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

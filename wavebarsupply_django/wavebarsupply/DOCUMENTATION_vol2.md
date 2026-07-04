# WaveBar Supply — Django Transition Documentation (Vol. 2)

This document covers **only the new additions and changes** made in this round:
the **About** page, the **Contact** page (with a Django form), the navbar links
for both, and the CSS clean-up. Nothing from the first documentation is repeated
here.

---

## 1. What was added

- A new **About** page with information about WaveBar Supply.
- A new **Contact** page with a form (email, bar name, message) built using
  Django's forms framework.
- **About** and **Contact** links in the header navbar only (not the footer).
- Removed the empty `font-family:` declaration from `general_style.css`.

---

## 2. New / changed files at a glance

| File | New or changed | Purpose |
|---|---|---|
| `pages/` | new app | Holds the About and Contact pages |
| `pages/forms.py` | new | `ContactForm` (Django `forms.Form`) |
| `pages/views.py` | new | `about` and `contact` views |
| `pages/urls.py` | new | Namespaced routes `pages:about`, `pages:contact` |
| `templates/pages/about.html` | new | About page template |
| `templates/pages/contact.html` | new | Contact page template |
| `static/css/pages_style.css` | new | Styling for both new pages |
| `templates/base.html` | changed | Added About + Contact links to the header nav |
| `wavebarsupply/settings.py` | changed | Registered the `pages` app |
| `wavebarsupply/urls.py` | changed | Included `pages.urls` |
| `static/css/general_style.css` | changed | Removed empty `font-family:` |

---

## 3. Step-by-step process

### Step 1 — Created a single `pages` app for both new pages

```bash
python manage.py startapp pages
```

About and Contact are small, closely related "static-ish" pages, so rather than
create two separate apps they share one **`pages`** app. This keeps the project
tidy while still following the rule that every app carries its own name:
`pages/urls.py` sets `app_name = 'pages'`, giving the namespaced routes
`pages:about` and `pages:contact`, which can never collide with the other apps'
route names.

The app's auto-generated `models.py`, `admin.py` and `tests.py` were removed
because these pages need no database tables — the app only serves views. (Django
does not require these files to exist.)

### Step 2 — Registered the app and its URLs

`pages` was added to `INSTALLED_APPS` in `settings.py`, and the root
`wavebarsupply/urls.py` now includes the app:

```python
path('', include('pages.urls')),
```

`pages/urls.py` defines the two named routes:

```python
app_name = 'pages'
urlpatterns = [
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
```

This produces `/about/` and `/contact/`. Mounting at `''` is safe because these
sub-paths (`about/`, `contact/`) are distinct from the home app's empty path, so
there is no clash. Everything links to these pages by their **nickname**
(`{% url 'pages:about' %}`, `{% url 'pages:contact' %}`), never by a raw path.

### Step 3 — Built the Contact form with Django's forms framework

The requirement was to use Django's built-in forms rather than hand-writing a
form. Django ships ready-made form classes for authentication (used earlier for
login/register), but there is no ready-made "contact" form — so the correct
Django way is to declare a form with the **forms framework** (`forms.Form`),
which is what does the validation for us. The alternative — writing raw
`<input>` tags and validating them by hand in JavaScript — is exactly what we
are avoiding.

`pages/forms.py`:

```python
class ContactForm(forms.Form):
    email    = forms.EmailField(max_length=100, ...)
    bar_name = forms.CharField(max_length=100, ...)
    message  = forms.CharField(max_length=500, widget=forms.Textarea, ...)
```

Notes on the fields:

- `email` uses `EmailField`, so Django checks it is a valid email **and** at most
  100 characters.
- `bar_name` is a `CharField` capped at 100 characters.
- `message` is a `CharField` capped at 500 characters, rendered as a
  **textarea** (via `widget=forms.Textarea`) so there is room to type.
- Each widget also gets a `maxlength` attribute, so the browser stops input past
  the limit as well — but the real enforcement is Django's server-side
  validation.

### Step 4 — Wrote the views

`pages/views.py` has two simple views:

- `about` just renders the template.
- `contact` handles both GET and POST. On GET it shows an empty form. On POST it
  validates the submitted data with `ContactForm(request.POST)`; if valid, it
  sets a `submitted` flag and hands back a fresh empty form so the page can show
  a success message. If invalid, the same bound form is re-rendered and Django
  automatically displays the error messages next to each field.

The contact messages are not stored anywhere — the task only asked for the form
and a submit button, so on success we simply confirm receipt. (Storing them in a
model, or emailing them, would be a natural next step.)

### Step 5 — Created the templates

Both templates use `{% extends 'base.html' %}` so they inherit the shared
navbar and footer, and both load the new `pages_style.css` through their
`{% block extra_css %}`.

- **`about.html`** — a navy hero band with the page title, a short intro about
  WaveBar Supply, and three small "value" cards (Wholesale Pricing, 24h
  Delivery, Curated Range).
- **`contact.html`** — a centered card containing the form. The form is a
  standard `<form method="post">` with `{% csrf_token %}`; each field is rendered
  with its label, the field itself, and `{{ field.errors }}`. A success banner
  appears above the form when `submitted` is true. The submit button is a plain
  `<button type="submit">`, and there is **no `onclick`** anywhere — the form
  posts itself the normal way.

### Step 6 — Added the navbar links (header only)

`base.html` now has two extra links in the header's `.nav_links` list:

```django
<li><a href="{% url 'pages:about' %}" class="nav_link">About</a></li>
<li><a href="{% url 'pages:contact' %}" class="nav_link">Contact</a></li>
```

They were added **only** to the header navigation, as requested — the footer
navigation was left unchanged (still Home / Browse / Login). Because the existing
`general_script.js` already highlights whichever nav link matches the current
path, the new About and Contact links get the active-state styling automatically
with no extra JavaScript.

### Step 7 — Removed the empty `font-family` from `general_style.css`

The `html` selector previously had a leftover empty declaration:

```css
html { scroll-behavior: smooth; font-family:  }   /* before */
html { scroll-behavior: smooth; }                 /* after  */
```

The empty `font-family:` was invalid and did nothing (the browser ignored it),
but it has now been removed for cleanliness. The `remember me` checkbox and
`forgot password` link on the login page were intentionally left as they are.

---

## 4. Rules followed in this round

- Only **vanilla HTML, CSS and JavaScript** were used; no libraries added.
- **No new JavaScript was needed** — the contact form submits via a normal HTML
  form POST, and the navbar highlighting already exists. So there was no
  `getElementById`/`querySelector` decision to make and no `onclick` anywhere.
- The contact form uses **Django's forms framework** (`forms.Form`) rather than a
  hand-built form.
- All page navigation uses **named URLs** (`{% url 'pages:about' %}`,
  `{% url 'pages:contact' %}`); no page is linked by a raw path.
- The new **`pages` app has its own app name** (`pages`) to avoid route-name
  collisions.
- New code was kept simple: one small app, one form, two views, two templates.

---

## 5. How to run (unchanged)

No new setup steps are required. The same commands as before still apply
(`migrate`, `loaddata products`, `runserver`); there are no new migrations
because the `pages` app has no models. The new pages are then available at
`/about/` and `/contact/`.

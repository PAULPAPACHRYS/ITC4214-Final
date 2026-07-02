# WaveBar Supply — Django Transition Documentation

This document explains how the original static site (plain HTML, CSS and
JavaScript for the **Home**, **Browse** and **Login/Register** pages) was
converted into a Django project, every change that was made, and the reasoning
behind each decision.

---

## 1. How to run the project

From the project root (the folder containing `manage.py`):

```bash
# 1. (optional) create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. create the database tables
python manage.py migrate

# 4. load the 52 products into the database
python manage.py loaddata products

# 5. (optional) create an admin account to use /admin/
python manage.py createsuperuser

# 6. run the development server
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

---

## 2. Final project structure

```
wavebarsupply/
├── manage.py
├── requirements.txt
├── wavebarsupply/              ← project package (settings, root URLs)
│   ├── settings.py
│   └── urls.py
├── home/                       ← app: landing page          (app_name = "home")
│   ├── urls.py
│   └── views.py
├── catalogue/                  ← app: browse page + data     (app_name = "catalogue")
│   ├── models.py               ← Product model
│   ├── admin.py
│   ├── urls.py
│   ├── views.py
│   └── fixtures/products.json  ← the 52 products from data.js
├── accounts/                   ← app: login / register       (app_name = "accounts")
│   ├── models.py               ← Profile model
│   ├── forms.py                ← LoginForm + RegisterForm (built-in forms)
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html               ← shared nav + footer (template inheritance)
│   ├── home/index.html
│   ├── catalogue/browse.html
│   └── accounts/login.html
└── static/
    ├── css/   general_style.css, home_style.css, browse_style.css, login_style.css
    └── js/    general_script.js, home.js, browse.js, login.js
```

---

## 3. Step-by-step process

### Step 1 — Created the project and three apps

The site has three distinct areas, so it was split into three apps. Keeping
each page concern in its own app keeps the code organised and lets each app own
its own URLs.

```bash
django-admin startproject wavebarsupply .
python manage.py startapp home
python manage.py startapp catalogue
python manage.py startapp accounts
```

Each app is given a **URL namespace** (an "app name") in its `urls.py`, e.g.
`app_name = 'home'`. This was a specific requirement: it prevents URL-name
collisions between apps (so `home:index` and `catalogue:browse` can never clash
even if two apps used the same name internally).

### Step 2 — Configured `settings.py`

Four changes were made:

1. Registered the three apps at the top of `INSTALLED_APPS` (`home`,
   `catalogue`, `accounts`).
2. Told the template engine where the shared templates live:
   `'DIRS': [BASE_DIR / 'templates']`.
3. Pointed the static-file finder at the project static folder:
   `STATICFILES_DIRS = [BASE_DIR / 'static']`.
4. Added authentication redirect settings, written as **named URLs** rather than
   hard-coded paths:

   ```python
   LOGIN_URL = 'accounts:login'
   LOGIN_REDIRECT_URL = 'catalogue:browse'
   LOGOUT_REDIRECT_URL = 'home:index'
   ```

### Step 3 — Wired up the URLs (with nicknames, no hard-coded page links)

The original site linked pages with raw file names like `href="browse.html"`.
That does not work in Django, where URLs are routed by the dispatcher. The
requirement was to **avoid navigating by URL string and instead give every URL a
nickname (name)** and reference it by that name.

The root `wavebarsupply/urls.py` includes each app:

```python
path('', include('home.urls')),
path('browse/', include('catalogue.urls')),
path('accounts/', include('accounts.urls')),
```

And every route is named inside its app, for example:

```python
# catalogue/urls.py
app_name = 'catalogue'
urlpatterns = [ path('', views.browse, name='browse') ]
```

Templates then link with `{% url 'catalogue:browse' %}` instead of
`browse.html`. The named routes created are: `home:index`,
`catalogue:browse`, `accounts:login`, `accounts:logout`.

### Step 4 — Turned the HTML pages into templates

The three `.html` files were moved into the `templates/` folder and converted to
Django templates:

- All `href` and `src` references to local files now use the `{% static %}` and
  `{% url %}` tags so Django resolves the correct paths.
- Each page now **extends a shared `base.html`** via `{% extends 'base.html' %}`
  and fills in a `{% block content %}`.

**Why a `base.html`?** In the original site the navigation bar and footer were
not in the HTML at all — `general_script.js` injected them into empty
`<header>`/`<footer>` elements with `innerHTML`. That approach has two problems
in Django: the nav links were hard-coded `.html` paths (which won't route), and
building markup in JavaScript can't use `{% url %}` names. Moving the nav and
footer into `base.html` solves both: the markup is server-rendered, the links
use named URLs, and every page automatically shares the same chrome. The nav
also now shows **Logout** when a user is logged in and **Login / Register**
otherwise, using `{% if user.is_authenticated %}`.

### Step 5 — Moved the product data into a real database model

The original `data.js` held a 52-item `PRODUCTS` array. For a genuine Django
project this data belongs in the database, so:

- A `Product` model was created in `catalogue/models.py` with the same fields
  the JavaScript used (`name`, `brand`, `category`, `subcategory`, `price`,
  `volume`, `abv`, `emoji`, `tags`). `tags` is a `JSONField` because it is a
  list; `price` is a `DecimalField` because it represents money.
- The whole array was converted into a Django **fixture**
  (`catalogue/fixtures/products.json`) and loaded with
  `python manage.py loaddata products`.
- The model is registered in the **Django admin** so products can be managed
  through `/admin/` without touching code.

**Keeping the front-end filtering exactly as it was.** The Browse page does all
of its searching, filtering and sorting in the browser with JavaScript, and that
logic is good. Rewriting it server-side would have been a large change for no
benefit, so instead the views read the products from the database and pass them
to the page using Django's `json_script` filter:

```django
{{ products|json_script:"products_data" }}
```

This renders a `<script type="application/json">` block. The JavaScript then
reads it instead of relying on the old global variable:

```javascript
const PRODUCTS = JSON.parse(document.querySelector('#products_data').textContent);
```

That single line is the **only** change to `browse.js` — every filter, the
price sliders, the search and the sorting work exactly as before. `data.js` is
therefore no longer needed and was removed; the database is now the single
source of truth.

One small but important detail: in the view, `price` is converted with
`float(p['price'])`. Django serialises `Decimal` values as strings, which would
have broken `product.price.toFixed(2)` in the JavaScript, so casting to a number
keeps the front-end working.

The **featured products** on the home page used to be picked inside `home.js`
(`featured_ids = [22, 39, …]`). That selection was moved into `home/views.py`
(a data concern belongs in the view) and the chosen products are passed to the
page the same `json_script` way. `home.js` is now simpler: it just renders
whatever the view gives it, in the order the view provides.

### Step 6 — Replaced the JavaScript form validation with Django's built-in forms

This was the biggest functional change, and the requirement was explicit: **use
Django's built-in forms, do not hand-build custom forms.**

The original `login.js` did all validation in the browser (checking empty
fields, email format, password length, matching passwords, etc.) and then faked
a success message. In Django that work is done by form classes on the server:

- **Login** uses `LoginForm`, a thin subclass of Django's
  `AuthenticationForm`. It only relabels the username field to "Email Address"
  and adds the shared CSS classes so it matches the existing styling.
- **Register** uses `RegisterForm`, a subclass of Django's `UserCreationForm`.
  `UserCreationForm` already handles the password rules and the
  password-confirmation match. It was *extended* (not replaced) with the extra
  business fields the original form collected: first name, last name, business
  name, email, phone, region and the terms checkbox.

Because the original site logs in **by email** (there was no username field),
the form stores the user's email as the Django `username` as well. That way the
built-in `AuthenticationForm` — which authenticates on `username` — accepts the
email, and no custom authentication backend is needed.

The trade-only fields that don't belong on the built-in `User` model
(`bar_name`, `phone`, `location`) are saved to a small **`Profile` model** in the
`accounts` app, linked one-to-one to the user. `Profile` is also registered in
the admin.

`accounts/views.py` serves both forms from a single view. The two submit buttons
are named (`login_submit` and `register_submit`) so the view knows which form
was posted. On success the user is logged in and redirected to the catalogue; on
failure the same page is re-rendered with the form's error messages, and the
`active_panel` variable makes sure the tab that was submitted stays open.

`login.js` was trimmed accordingly: all the validation functions were deleted
(Django does that now) and the file keeps only the genuine UI behaviour — the
Login/Register tab switching and the show/hide-password toggle.

### Step 7 — Moved the static assets

The four CSS files were copied unchanged into `static/css/`. The four JavaScript
files were placed in `static/js/` with the adjustments described above. The
templates load them with `{% static %}`, and the `defer` attribute is kept so
scripts still run after the page has parsed.

---

## 4. Summary of the rules followed

- **Vanilla HTML/CSS/JS** was used for every front-end change; no frameworks or
  libraries were added.
- **`querySelector` only** — no `getElementById` was introduced anywhere.
- **No `onclick` in HTML** — all interactivity is wired with `addEventListener`
  in the JavaScript files. The forms now submit via standard `<form>` POST.
- **Django built-in forms** (`AuthenticationForm`, `UserCreationForm`) were
  subclassed rather than building forms from scratch.
- **Named URLs everywhere** — no template or setting links to a page by a raw
  path; everything uses `{% url 'app:name' %}` / `reverse('app:name')`.
- **Each app has its own app name** (`home`, `catalogue`, `accounts`) to avoid
  URL-name collisions.
- Code was kept simple and close to the original wherever possible.

---

## 5. Files that changed, and why (quick reference)

| Original file | Became | Why |
|---|---|---|
| `home.html` | `templates/home/index.html` | Extends `base.html`; links use `{% url %}` and `{% static %}` |
| `browse.html` | `templates/catalogue/browse.html` | Same, plus `json_script` to feed products to JS |
| `login.html` | `templates/accounts/login.html` | Renders Django forms inside the original tab layout |
| `general_script.js` | `static/js/general_script.js` | No longer injects nav/footer (now in `base.html`); just highlights the active link |
| `home.js` | `static/js/home.js` | Reads products from `json_script`; featured selection moved to the view |
| `browse.js` | `static/js/browse.js` | One line changed: reads `PRODUCTS` from `json_script` instead of `data.js` |
| `login.js` | `static/js/login.js` | Validation removed (Django handles it); only tab + password-toggle UI kept |
| `data.js` | `catalogue/models.py` + `catalogue/fixtures/products.json` | Data moved into the database |
| nav/footer (was built in JS) | `templates/base.html` | Server-rendered shared layout using named URLs |
| *(new)* | `accounts/forms.py`, `accounts/models.py` | Built-in form subclasses + `Profile` for trade fields |
| `*_style.css` (×4) | `static/css/*` | Copied unchanged |

---

## 6. Optional follow-ups (not done, to keep the scope tight)

- The "Remember me" checkbox and "Forgot password?" link are kept as visual
  elements but are not yet wired to backend behaviour.
- `general_style.css` has a harmless empty `font-family:` declaration on the
  `html` selector (it was already there in the original); the browser ignores
  it, so it was left untouched.
- For deployment you would later set `DEBUG = False`, configure `ALLOWED_HOSTS`,
  and run `collectstatic`.

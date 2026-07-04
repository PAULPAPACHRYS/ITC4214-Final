# WaveBar Supply — Django Documentation (Vol. 3)

This document covers **only the changes made in this round**: removing
`general_script.js`, and rebuilding the database from a single `Product` table
into the full relational schema (Categories, Brands, Products, Users, Orders,
Order_Items), including bcrypt password hashing and every file that had to change
because of it. Nothing from Vol. 1 or Vol. 2 is repeated here.

---

## 1. Removed `general_script.js`

The file was deleted, and its `<script>` tag was removed from `base.html`. It
previously only highlighted the active navbar link; nothing else depended on it,
so the site behaves the same minus that highlight.

---

## 2. The new database schema

The database now has six tables. Each model sets an explicit `db_table` so the
SQLite table names match the requested schema exactly (`categories`, `brands`,
`products`, `users`, `orders`, `order_items`), and every foreign key produces the
requested `_id` column (`category_id`, `brand_id`, `user_id`, `order_id`,
`product_id`) — this is Django's default: you declare the field as `category` and
the column becomes `category_id`.

The tables live in these apps:

- **`catalogue`** — `Category`, `Brand`, `Product`
- **`accounts`** — `Users`
- **`orders`** — `Order`, `OrderItem` (a **new app** created this round)

### 2.1 Splitting the old Product table

The old `Product` table held everything in one row (brand, category and
subcategory as plain text). Those were pulled out into their own tables:

**`Category`** (`categories`) — `id`, `name`, `subcategory`. Each row is one
(category, sub-category) pair, e.g. `('non-alcohol', 'Soft Drinks')`. As
required, `name` **keeps the exact three choices** the old `Product.category`
field had (`non-alcohol`, `fermented`, `distilled`) and its `max_length=20`;
`subcategory` keeps the old `max_length=50`. There are 14 category rows (one per
distinct pair in the data).

**`Brand`** (`brands`) — `id`, `name`, `country`. `name` keeps the old
`Product.brand` `max_length=100`. `country` is a **new** field that did not exist
before, so plausible countries were assigned to each of the 51 brands (e.g.
Mythos → Greece, Heineken → Netherlands, Absolut → Sweden).

**`Product`** (`products`) — `id`, `name`, `price`, `volume`, `abv`, `emoji`,
`tags`, `category_id` (FK), `brand_id` (FK). Fields that carried over kept their
old restrictions: `name` `max_length=100`, `price` `DecimalField(max_digits=6,
decimal_places=2)`, `emoji` `max_length=8`, `tags` `JSONField`. Two fields
**changed type** as the schema required:

- **`volume`: text → integer.** Old values like `"330ml"` and `"1L"` are now
  stored as an integer number of millilitres (`330`, `1000`). It's a
  `PositiveIntegerField`.
- **`abv`: choice text → decimal.** The old `abv` was a bucket
  (`none`/`low`/`medium`/`high`); it is now a real percentage
  `DecimalField(max_digits=4, decimal_places=1)` such as `4.7`, `13.0`, `40.0`.
  Realistic values were assigned per product (0.0 for everything
  non-alcoholic). Because the ERD changed this from a choices field to a number,
  the old choice restriction no longer applies to it.

Foreign keys use `on_delete=models.PROTECT` so a category or brand that still has
products can't be deleted by accident.

### 2.2 The Users table (with bcrypt)

**`Users`** (`users`) — `id`, `full_name`, `role`, `password`, `bar_name`,
`bar_location`, `email`, `phone`.

- `role` is a choices field (`customer` / `employee` / `admin`), defaulting to
  `customer`.
- `email` is unique.
- `password` stores a **bcrypt hash**, never the plain text. The model has two
  helpers:
  - `set_password(raw)` — hashes with `bcrypt.hashpw(..., bcrypt.gensalt())` and
    stores the result.
  - `check_password(raw)` — verifies with `bcrypt.checkpw(...)`.

  `bcrypt` was added to `requirements.txt` (`pip install bcrypt`).

This custom table **replaces the old `Profile` model**, which was deleted. Note
that this is the site's *own* accounts table and is separate from Django's admin
login — the `/admin/` site still uses a Django superuser (created with
`createsuperuser`), while customer sign-ups live in the `users` table.

### 2.3 Orders and Order_Items (new `orders` app)

**`Order`** (`orders`) — `id`, `user_id` (FK → Users), `order_date` (a `DateField`
set automatically on creation), `status` (choices `pending`/`completed`/
`canceled`, default `pending`).

**`OrderItem`** (`order_items`) — `id`, `order_id` (FK → Order), `product_id`
(FK → Product), `quantity` (integer), `unit_price` (decimal). The `order` FK uses
`related_name='items'` so an order's lines can be read with `order.items`.

There is no ordering screen yet — these tables just give the database the right
structure for a future "place order" feature. They start empty and can be managed
through the admin.

---

## 3. Files that changed because of the new schema

### 3.1 `catalogue/views.py` — flattening related data for the front-end

The Browse and Home pages render product cards in JavaScript from a block of
JSON. The JavaScript still expects the old flat shape (a `brand` string, a
`category` string, a `subcategory` string, etc.), so the view's helper
`_products_as_dicts()` now reads the related tables and flattens them back into
that shape:

- `brand` comes from `product.brand.name`, `category` from
  `product.category.name`, `subcategory` from `product.category.subcategory`.
- `volume` is turned back into a display string (`330` → `"330ml"`) so the card
  text and the volume filter look exactly as before.
- `price` and `abv` are cast to `float` so the JSON carries numbers.
- `select_related('category', 'brand')` is used so all the data is fetched in one
  query instead of one query per product.

`home/views.py` did not need changing — it calls the same helper.

### 3.2 `browse.js` — one change, for the numeric ABV

Since `abv` is now a real number instead of a band string, the alcohol-content
filter needed a small update. A helper `abv_band(abv)` maps the number to the
same four checkbox bands (`none` = 0, `low` < 8, `medium` 8–20, `high` 20+), and
the filter now compares against that. Everything else in `browse.js` is
unchanged. `home.js` is unchanged.

### 3.3 Authentication rewired to the `Users` table

Because the project no longer uses Django's built-in auth user, the login and
register flow was moved onto the new `Users` table:

- **`accounts/forms.py`** — `RegisterForm` is now a `ModelForm` on `Users` (plus
  password confirmation and a terms checkbox); on `save()` it hashes the password
  with bcrypt and sets `role='customer'`. `LoginForm` is a plain form that looks
  the user up by email and verifies the password with `check_password()`. The
  business fields collected are `full_name` (a single field now, replacing the
  old first/last name pair) and `bar_location` (kept as the region dropdown, but
  stored as a string).
- **`accounts/views.py`** — login state is kept in the session
  (`request.session['user_id']`) rather than Django's `login()`. Logout clears
  it.
- **`accounts/context_processors.py`** (new) — exposes the logged-in row to every
  template as `current_user`. It is registered in `settings.py` under the
  template `context_processors`.
- **`base.html`** — the navbar now checks `{% if current_user %}` (instead of the
  old Django `user.is_authenticated`) to show Logout vs Login.
- **`templates/accounts/login.html`** — updated to render the new fields (single
  "Full Name", email-based login). `login.js` did not need changing: the rendered
  field ids (`id_password`, `id_password1`, `id_password2`) still match what its
  password toggles look for.

### 3.4 Admin

`admin.py` in `catalogue`, `accounts` and `orders` registers all six models so
they can be browsed and edited at `/admin/`. Orders show their line items inline.

---

## 4. Fixtures

The single old `products.json` was replaced by three fixtures that respect the
foreign keys:

- `catalogue/fixtures/categories.json` — 14 category rows.
- `catalogue/fixtures/brands.json` — 51 brand rows (with the new countries).
- `catalogue/fixtures/products.json` — 52 products, each pointing at a
  `category` id and `brand` id, with integer `volume` and decimal `abv`.

They must be loaded **categories and brands first**, then products (products
reference them):

```bash
python manage.py loaddata categories brands products
```

The `users`, `orders` and `order_items` tables have no fixture — they are filled
in through the app (registration) or the admin.

---

## 5. Migrations were regenerated

This was a large structural change on a disposable development database, so
rather than stack alter-migrations on top of the old ones, the old initial
migrations for `catalogue` and `accounts` (and the old `db.sqlite3`) were
deleted, and fresh initial migrations were created for all three data apps:

```bash
python manage.py makemigrations
python manage.py migrate
```

(If you had real data to preserve you would instead write incremental migrations;
here the data comes from fixtures, so starting clean is simpler.)

---

## 6. Updated setup steps

```bash
pip install -r requirements.txt        # now also installs bcrypt
python manage.py migrate
python manage.py loaddata categories brands products
python manage.py createsuperuser       # optional, for /admin/
python manage.py runserver
```

---

## 7. Assumptions made

- **Volume unit** is millilitres; `"1L"` became `1000`, and cards display
  `"1000ml"` rather than `"1L"`.
- **ABV percentages** were assigned realistic values (e.g. lager ≈ 4.5–5%, wine
  ≈ 11–13.5%, spirits ≈ 37.5–47.3%), since the old data only had bands.
- **Brand countries** were assigned per brand, as the old data had none.
- The **`Users` table is independent of Django's admin login**; the admin still
  uses a Django superuser. Adding a user directly through the admin would store
  the `password` field as typed (not bcrypt-hashed) — hashing happens in the
  registration form. Wiring the admin to hash on save could be a later
  refinement.
- **"Remember me"** and **"Forgot password?"** remain non-functional placeholders,
  as before.

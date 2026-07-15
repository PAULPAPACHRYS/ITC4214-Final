from django.db.models import Count, Q
from django.shortcuts import render

from likes.models import Like
from presets.forms import PresetForm
from presets.models import Preset
from .models import Category, Product, Subcategory


def _products_as_dicts(queryset, user=None):
    """Flatten Product rows (with their related category/brand) into the same
    shape the front-end JavaScript already expects.

    - brand / category / subcategory come from the related tables.
    - volume is turned back into a display string (e.g. 330 -> "330ml").
    - price and abv are cast to float so the JSON carries numbers, not strings.
    - like_count / liked drive the like button on each product card.

    Both like fields are gathered in just two queries no matter how many
    products there are: the count is annotated onto the queryset, and the set of
    products the current user already liked is fetched once.
    """
    queryset = (queryset
                .select_related('subcategory__category', 'brand')
                .prefetch_related('tags')
                .annotate(like_count=Count('likes', distinct=True)))

    liked_ids = set()
    if user is not None and user.is_authenticated:
        liked_ids = set(Like.objects
                        .filter(user=user, product__in=queryset)
                        .values_list('product_id', flat=True))

    products = []
    for p in queryset:
        products.append({
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name,
            'category': p.subcategory.category.name,
            'subcategory': p.subcategory.name,
            'price': float(p.price),
            'volume': f"{p.volume}ml",
            'abv': float(p.abv),
            'image': p.image_url,
            'tags': [t.name for t in p.tags.all()],
            'like_count': p.like_count,
            'liked': p.id in liked_ids,
        })
    return products


def browse(request):
    products = _products_as_dicts(Product.objects.all(), user=request.user)

    # Default presets (user is null) are shown to everyone; a logged-in user also
    # sees the presets they created themselves.
    preset_filter = Q(user=None)
    if request.user.is_authenticated:
        preset_filter |= Q(user=request.user)
    presets = []
    for p in Preset.objects.filter(preset_filter).prefetch_related('ingredients'):
        data = p.to_dict()
        data['owned'] = (request.user.is_authenticated and p.user_id == request.user.id)
        presets.append(data)

    # Show the user's own presets before the default ones. sort() is stable, so
    # presets keep their relative order within each group; owned=True sorts first.
    presets.sort(key=lambda d: not d['owned'])

    # The sub-category filter options, grouped under their category. This is
    # built from the Subcategory table, so a sub-category added on the Database
    # page shows up in the filter straight away (it used to be a hard-coded list
    # in the JavaScript, which had to be edited by hand to stay in step).
    subcategories = {}
    for sub in Subcategory.objects.select_related('category').order_by('id'):
        subcategories.setdefault(sub.category.name, []).append(sub.name)

    # The category tabs, also built from the database. They used to be typed out
    # by hand in the template, which meant a category added on the Database page
    # never got a tab here.
    categories = [{'slug': c.name, 'label': c.display_name}
                  for c in Category.objects.order_by('id')]

    return render(request, 'catalogue/browse.html', {
        'products': products,
        'presets': presets,
        'subcategories': subcategories,
        'categories': categories,
        'preset_form': PresetForm(),
    })

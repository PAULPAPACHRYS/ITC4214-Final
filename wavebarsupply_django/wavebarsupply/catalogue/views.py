from django.db.models import Count, Q
from django.shortcuts import render
from likes.models import Like
from presets.forms import PresetForm
from presets.models import Preset
from .models import Category, Product, Subcategory


def _products_as_dicts(queryset, user=None):
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

    # default cocktail presets, user is null, they are shown to everyone logged in or not
    preset_filter = Q(user=None)
    if request.user.is_authenticated:
        preset_filter |= Q(user=request.user)
    presets = []
    for p in Preset.objects.filter(preset_filter).prefetch_related('ingredients'):
        data = p.to_dict()
        data['owned'] = (request.user.is_authenticated and p.user_id == request.user.id)
        presets.append(data)

    # displays the user created presets first using sort() and owned=True sorts first.
    presets.sort(key=lambda d: not d['owned'])

    subcategories = {}
    for sub in Subcategory.objects.select_related('category').order_by('id'):
        subcategories.setdefault(sub.category.name, []).append(sub.name)

    categories = [{'slug': c.name, 'label': c.display_name}
                  for c in Category.objects.order_by('id')]

    return render(request, 'catalogue/browse.html', {
        'products': products,
        'presets': presets,
        'subcategories': subcategories,
        'categories': categories,
        'preset_form': PresetForm(),
    })

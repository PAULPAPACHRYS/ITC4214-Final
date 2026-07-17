from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from catalogue.models import Product
from catalogue.views import _products_as_dicts
from orders.models import Order

"""
Content Similarity Scoring

Every product is scored against a product already in the cart by adding up a weighted score 
higher score = stronger signal for reccommendation
it works purely from the product attributes we already store in the database
"""
SAME_SUBCATEGORY = 5      # ex: gin is very similar to another gin (strongest)
SAME_CATEGORY = 2         # same top-level category but different subcategory
SAME_BRAND = 2
SHARED_TAG = 1.5          # for every tag the two products have in common
PRICE_NEAR = 1            # price within €2
PRICE_CLOSE = 0.5         # price within €5

HOW_MANY = 4              # number of suggestions to return


def _similarity(target, candidate):
    # score how similar the candidate is to the target
    score = 0

    if target.subcategory_id == candidate.subcategory_id:
        score += SAME_SUBCATEGORY
    elif target.subcategory.category_id == candidate.subcategory.category_id:
        score += SAME_CATEGORY

    if target.brand_id == candidate.brand_id:
        score += SAME_BRAND

    #tags are rows now, so compare them by id
    target_tags = {t.id for t in target.tags.all()}
    candidate_tags = {t.id for t in candidate.tags.all()}
    score += SHARED_TAG * len(target_tags & candidate_tags)

    price_gap = abs(float(target.price) - float(candidate.price))
    if price_gap <= 2:
        score += PRICE_NEAR
    elif price_gap <= 5:
        score += PRICE_CLOSE

    return score


def _rank(cart_products, candidates, limit=HOW_MANY):
    """
    Rank candidates by total similarity to everything in the cart

    a candidate's score is the sum of its similarity to each cart product, 
    so items similar to the cart as a whole rise to the top, 
    only positive scores are kept and ties break by id
    """
    scored = []
    for candidate in candidates:
        total = sum(_similarity(t, candidate) for t in cart_products)
        if total > 0:
            scored.append((total, candidate.id, candidate))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return [candidate for _, _, candidate in scored[:limit]]


@login_required
def for_cart(request):
    """
    Return up to HOW_MANY products similar to what is in the user's cart

    response -> {ok, products: [...]}
    products already in the cart are never suggested 
    if the cart is empty or nothing scores then products is empty
    """
    order = Order.objects.filter(user=request.user, is_cart=True).first()
    cart_items = list(
        order.items.select_related('product', 'product__subcategory', 'product__brand')
                   .prefetch_related('product__tags')
    ) if order else []

    if not cart_items:
        return JsonResponse({'ok': True, 'products': []})

    cart_products = [item.product for item in cart_items]
    cart_ids = {p.id for p in cart_products}

    candidates = (Product.objects
                  .select_related('subcategory__category', 'brand')
                  .prefetch_related('tags')
                  .exclude(id__in=cart_ids))

    ranked = _rank(cart_products, candidates)
    ranked_ids = [p.id for p in ranked]

    products = _products_as_dicts(
        Product.objects.filter(id__in=ranked_ids), user=request.user)
    position = {pid: i for i, pid in enumerate(ranked_ids)}
    products.sort(key=lambda p: position[p['id']])

    return JsonResponse({'ok': True, 'products': products})

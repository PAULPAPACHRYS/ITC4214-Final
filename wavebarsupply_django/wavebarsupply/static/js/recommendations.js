// ----------------------------------------------------------------------------
// "You might also like" strip on the cart page.
// On load, ask the recommendations endpoint for products similar to what's in
// the cart, build a card for each, and reveal the strip. If there are none (or
// the request fails), the strip stays hidden — nothing is forced on the user.
// ----------------------------------------------------------------------------
const recommend_section = document.querySelector('.recommend_section');

if (recommend_section) {
  const grid = recommend_section.querySelector('.recommend_grid');
  const url = recommend_section.dataset.recommendUrl;

  // Same markup as the Browse/Home product cards, so the existing "+ Order" and
  // Like handlers (already loaded on this page) work on these cards too, and the
  // shared .product_card styles apply.
  function build_product_card(product) {
    const card = document.createElement('div');
    card.className = 'product_card';
    card.innerHTML = `
      <div class="product_card_thumb">${product.emoji}</div>
      <div class="product_card_body">
        <span class="product_card_category">${product.subcategory}</span>
        <p class="product_card_name">${product.name}</p>
        <p class="product_card_brand">${product.brand} · ${product.volume}</p>
        <div class="product_card_meta">
          ${product.tags.slice(0, 3).map(t => `<span class="product_tag">${t}</span>`).join('')}
        </div>
        <div class="product_card_footer">
          <p class="product_card_price">€${product.price.toFixed(2)}<span>/unit</span></p>
          <div class="qty_control">
            <button class="qty_btn qty_minus" type="button">-</button>
            <input class="qty_input" type="number" min="1" value="1" />
            <button class="qty_btn qty_plus" type="button">+</button>
          </div>
          <button class="button_add_to_order" data-id="${product.id}">+ Order</button>
        </div>
        <div class="like_control">
          <button class="like_button ${product.liked ? 'liked' : ''}" type="button" data-id="${product.id}" aria-pressed="${product.liked ? 'true' : 'false'}"><span class="like_heart">♥</span> Like</button>
          <span class="like_count">${product.like_count}</span>
        </div>
      </div>
    `;
    return card;
  }

  // Fetch similar products and (re)fill the strip. Clearing the grid first means
  // this can run again later — e.g. after the cart changes — and reflect the new
  // cart. If nothing similar remains, the strip is hidden.
  function load_recommendations() {
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(response => response.json())
      .then(data => {
        grid.innerHTML = '';
        if (!data.ok || data.products.length === 0) {
          recommend_section.classList.add('hidden');   // nothing to show
          return;
        }
        data.products.forEach(product => grid.appendChild(build_product_card(product)));
        recommend_section.classList.remove('hidden');
      })
      .catch(() => {});   // on failure, leave the strip as it is
  }

  load_recommendations();

  // The cart page fires this after an item is removed; refresh so the
  // suggestions match the new cart (and disappear if nothing similar remains).
  document.addEventListener('cart:changed', load_recommendations);
}

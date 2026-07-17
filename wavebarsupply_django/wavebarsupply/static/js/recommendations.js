const recommend_section = document.querySelector('.recommend_section');

if (recommend_section) {
  const grid = recommend_section.querySelector('.recommend_grid');
  const url = recommend_section.dataset.recommendUrl;

  function build_product_card(product) {
    const card = document.createElement('div');
    card.className = 'product_card';
    card.innerHTML = `
      <div class="product_card_thumb">${product.image ? `<img class="product_card_image" src="${product.image}" alt="${product.name}">` : ''}</div>
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

  function load_recommendations() {
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(response => response.json())
      .then(data => {
        grid.innerHTML = '';
        if (!data.ok || data.products.length === 0) {
          recommend_section.classList.add('hidden');   //nothing to show
          return;
        }
        data.products.forEach(product => grid.appendChild(build_product_card(product)));
        recommend_section.classList.remove('hidden');
      })
      .catch(() => {});   //on failure, leave the strip as it is
  }

  load_recommendations();

  //the cart page fires this after an item is removed, so the suggestions match the new cart
  document.addEventListener('cart:changed', load_recommendations);
}

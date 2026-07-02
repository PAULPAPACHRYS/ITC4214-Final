// The featured products are chosen by the Django view and handed to this page
// inside a <script id="products_data"> block (Django's json_script filter).
const PRODUCTS = JSON.parse(document.querySelector('#products_data').textContent);

// creates each featured product card on the homepage
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
        ${product.tags.slice(0,2).map(t => `<span class="product_tag">${t}</span>`).join('')}
      </div>
      <div class="product_card_footer">
        <p class="product_card_price">€${product.price.toFixed(2)}<span>/unit</span></p>
        <button class="button_add_to_order" data-id="${product.id}">+ Order</button>
      </div>
    </div>
  `;
  return card;
}

function render_featured_products() {
  const grid = document.querySelector('#featured_grid');
  // The view already selected and ordered the featured products for us.
  PRODUCTS.forEach(product => {
    grid.appendChild(build_product_card(product));
  });
}

// Initialize
render_featured_products();

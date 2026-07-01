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

  // Pick a varied selection, will change it later to be random or latest additions
  const featured_ids = [22, 39, 50, 28, 19, 1, 46, 43];
  //grab the product details from the data.js 
  const selected = PRODUCTS.filter(p => featured_ids.includes(p.id));

  //call build_product_card for each product to create the card with its information
  selected.forEach(product => {
    grid.appendChild(build_product_card(product));
  });
}

//Initialize 
render_featured_products();


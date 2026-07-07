// Product cards (Browse + Home): the quantity stepper and the "+ Order" button.
// Adding to the cart is an AJAX POST so the user stays on the page.
const csrf_el = document.querySelector('meta[name="csrf-token"]');
const CSRF = csrf_el ? csrf_el.content : '';
const AUTHED = document.body.dataset.authenticated === 'true';
const CART_ADD_URL = document.body.dataset.cartAddUrl;

// + / - stepper buttons on the product cards
document.addEventListener('click', (event) => {
  const step = event.target.closest('.qty_plus, .qty_minus');
  if (step) {
    const input = step.closest('.qty_control').querySelector('.qty_input');
    let value = parseInt(input.value) || 1;
    value = step.classList.contains('qty_plus') ? value + 1 : value - 1;
    if (value < 1) value = 1;
    input.value = value;
    return;
  }

  // "+ Order" button
  const order_button = event.target.closest('.button_add_to_order');
  if (!order_button) return;

  if (!AUTHED) {
    alert('Please log in or register to add items to your cart.');
    return;
  }

  const card = order_button.closest('.product_card');
  const input = card.querySelector('.qty_input');
  let quantity = parseInt(input.value) || 1;
  if (quantity < 1) quantity = 1;

  fetch(CART_ADD_URL, {
    method: 'POST',
    headers: {
      'X-CSRFToken': CSRF,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `product_id=${order_button.dataset.id}&quantity=${quantity}`,
  })
    .then(response => response.json())
    .then(data => {
      if (!data.ok) return;
      const label = order_button.textContent;
      order_button.textContent = 'Added ✓';
      order_button.disabled = true;
      setTimeout(() => {
        order_button.textContent = label;
        order_button.disabled = false;
      }, 1200);
    })
    .catch(() => {});
});

// keep a typed quantity valid (at least 1)
document.addEventListener('change', (event) => {
  const input = event.target.closest('.product_card .qty_input');
  if (!input) return;
  let value = parseInt(input.value) || 1;
  if (value < 1) value = 1;
  input.value = value;
});

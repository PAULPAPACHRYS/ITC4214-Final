// Cart page: change quantities (+ / - / typed) and remove items, all persisted
// through the cart endpoints. Line totals and the cart total update live.
const cart_list = document.querySelector('#cart_list');
const cart_total = document.querySelector('#cart_total');
const csrf_meta = document.querySelector('meta[name="csrf-token"]');
const csrf_token = csrf_meta ? csrf_meta.content : '';

function post(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrf_token,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body,
  }).then(response => response.json());
}

function set_quantity(item, quantity) {
  if (quantity < 1) quantity = 1;
  const id = item.dataset.itemId;
  post(cart_list.dataset.updateUrl, `item_id=${id}&quantity=${quantity}`)
    .then(data => {
      if (!data.ok) return;
      item.querySelector('.cart_qty').value = data.quantity;
      item.querySelector('.cart_line_total').textContent = '€' + data.line_total;
      cart_total.textContent = '€' + data.cart_total;
    });
}

if (cart_list) {
  // + / - / remove buttons
  cart_list.addEventListener('click', (event) => {
    const item = event.target.closest('.cart_item');
    if (!item) return;
    const input = item.querySelector('.cart_qty');

    if (event.target.closest('.cart_plus')) {
      set_quantity(item, (parseInt(input.value) || 1) + 1);
    } else if (event.target.closest('.cart_minus')) {
      set_quantity(item, (parseInt(input.value) || 1) - 1);
    } else if (event.target.closest('.cart_remove')) {
      const id = item.dataset.itemId;
      post(cart_list.dataset.removeUrl, `item_id=${id}`).then(data => {
        if (!data.ok) return;
        item.remove();
        cart_total.textContent = '€' + data.cart_total;
        if (data.empty) window.location.reload();   // show the empty-cart message
      });
    }
  });

  // typed quantity
  cart_list.addEventListener('change', (event) => {
    const input = event.target.closest('.cart_qty');
    if (!input) return;
    const item = input.closest('.cart_item');
    set_quantity(item, parseInt(input.value) || 1);
  });
}

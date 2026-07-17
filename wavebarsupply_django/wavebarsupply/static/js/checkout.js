(function () {

const overlay = document.querySelector('#checkout_overlay');
const open_button = document.querySelector('#checkout_open');
const close_button = document.querySelector('#checkout_close');
const form = document.querySelector('#checkout_form');
const proceed = document.querySelector('#checkout_proceed');
const form_view = document.querySelector('#checkout_form_view');
const done_view = document.querySelector('#checkout_done');
const overlay_total = document.querySelector('#checkout_total');
const cart_total = document.querySelector('#cart_total');
const csrf_meta = document.querySelector('meta[name="csrf-token"]');
const csrf_token = csrf_meta ? csrf_meta.content : '';

let purchased = false;

function open_overlay() {
  // sync the amount with the live cart total
  if (overlay_total && cart_total) overlay_total.textContent = cart_total.textContent;
  overlay.classList.remove('hidden');
}

function close_overlay() {
  if (purchased) {
    window.location.reload();   //cart is now empty
  } else {
    overlay.classList.add('hidden');
  }
}

if (open_button) open_button.addEventListener('click', open_overlay);
if (close_button) close_button.addEventListener('click', close_overlay);
if (overlay) {
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) close_overlay();   //click on the backdrop
  });
}

if (form) {
  const fields = [...form.querySelectorAll('input')];

  // proceed is enabled only when every field has a value
  function update_proceed() {
    proceed.disabled = !fields.every(field => field.value.trim() !== '');
  }
  fields.forEach(field => field.addEventListener('input', update_proceed));

  // numeric input for card number and CVV
  const card = form.querySelector('[name="card_number"]');
  const cvv = form.querySelector('[name="cvv"]');
  const exp = form.querySelector('[name="expiration"]');
  if (card) card.addEventListener('input', () => { card.value = card.value.replace(/\D/g, ''); });
  if (cvv) cvv.addEventListener('input', () => { cvv.value = cvv.value.replace(/\D/g, ''); });

  if (exp) exp.addEventListener('input', () => {
    let v = exp.value.replace(/\D/g, '').slice(0, 4);
    if (v.length >= 3) v = v.slice(0, 2) + '/' + v.slice(2);
    exp.value = v;
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (proceed.disabled) return;

    fetch(form.dataset.checkoutUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams(new FormData(form)).toString(),
    })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          purchased = true;
          document.querySelector('#checkout_order_number').textContent = '#' + data.order_number;
          form_view.classList.add('hidden');
          done_view.classList.remove('hidden');
        } else {
          showMessage('Please check your details and try again.');
        }
      })
      .catch(() => {});
  });
}
})();

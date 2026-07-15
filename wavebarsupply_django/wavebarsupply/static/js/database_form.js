// Behaviour for the Database page add/edit forms.

(function () {
  // ---- Order items: fill the unit price in from the chosen product ----------
  // Each product <option> carries a data-price attribute (put there by
  // ProductPriceSelect in database/forms.py), so picking a product can fill the
  // price in without anyone having to look it up and retype it.
  const product_select = document.querySelector('.db_form select[name="product"]');
  const price_input = document.querySelector('.db_form input[name="unit_price"]');

  if (!product_select || !price_input) return;   // not the order-item form

  function selected_price() {
    const option = product_select.options[product_select.selectedIndex];
    return option ? option.dataset.price : '';
  }

  function fill_price() {
    const price = selected_price();
    if (price) price_input.value = price;
  }

  // When a product is picked, put its price in the box.
  product_select.addEventListener('change', fill_price);

  // On a fresh form the price box is empty, so fill it in for whatever product
  // happens to be selected. An existing line keeps the price it was saved with.
  if (!price_input.value) fill_price();
})();

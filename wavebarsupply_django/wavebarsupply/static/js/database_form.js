(function () {
  const product_select = document.querySelector('.db_form select[name="product"]');
  const price_input = document.querySelector('.db_form input[name="unit_price"]');

  if (!product_select || !price_input) return;

  function selected_price() {
    const option = product_select.options[product_select.selectedIndex];
    return option ? option.dataset.price : '';
  }

  function fill_price() {
    const price = selected_price();
    if (price) price_input.value = price;
  }

  product_select.addEventListener('change', fill_price);

  if (!price_input.value) fill_price();
})();

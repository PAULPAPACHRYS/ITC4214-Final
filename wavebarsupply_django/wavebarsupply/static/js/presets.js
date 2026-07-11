// ----------------------------------------------------------------------------
// Cocktail presets on the Browse page.
//   * builds a card per preset (default presets + the user's own),
//   * each card has a servings stepper and a "+ Order" that adds EVERY ingredient
//     to the cart (quantity = servings),
//   * logged-in users can create their own presets via the overlay.
// All of this is vanilla JS and self-contained in an IIFE.
// ----------------------------------------------------------------------------
(function () {
  const grid = document.querySelector('.preset_grid');
  if (!grid) return;

  const CSRF = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
  const AUTHED = document.body.dataset.authenticated === 'true';
  const ADD_URL = grid.dataset.addUrl;
  const CREATE_URL = grid.dataset.createUrl;

  const PRESETS = JSON.parse(document.querySelector('#presets_data').textContent);
  const PRODUCTS = JSON.parse(document.querySelector('#products_data').textContent);

  // ---- Build and render preset cards ----------------------------------------
  function servings_line(count) {
    const word = count === 1 ? 'serving' : 'servings';
    return `Makes <span class="preset_servings_count">${count}</span> ${word}`;
  }

  function build_preset_card(preset) {
    const card = document.createElement('div');
    card.className = 'preset_card';
    card.dataset.id = preset.id;
    card.innerHTML = `
      <div class="preset_card_thumb" style="background:${preset.color}"></div>
      <div class="preset_card_body">
        <span class="preset_card_label">Cocktail Preset</span>
        <p class="preset_card_name">${preset.name}</p>
        <p class="preset_card_ingredients"><strong>Ingredients:</strong> ${preset.ingredient_names.join(', ')}</p>
        <p class="preset_card_servings">${servings_line(1)}</p>
        <div class="preset_card_footer">
          <div class="qty_control">
            <button class="qty_btn preset_minus" type="button">-</button>
            <input class="qty_input preset_qty" type="number" min="1" value="1" />
            <button class="qty_btn preset_plus" type="button">+</button>
          </div>
          <button class="preset_order_button" type="button">+ Order</button>
        </div>
      </div>
    `;
    return card;
  }

  function render_presets() {
    grid.innerHTML = '';
    PRESETS.forEach(preset => grid.appendChild(build_preset_card(preset)));
  }
  render_presets();

  // ---- Servings stepper + "+ Order" -----------------------------------------
  function update_servings(card) {
    let value = parseInt(card.querySelector('.preset_qty').value) || 1;
    if (value < 1) value = 1;
    card.querySelector('.preset_qty').value = value;
    card.querySelector('.preset_card_servings').innerHTML = servings_line(value);
  }

  document.addEventListener('click', (event) => {
    // + / - stepper (own classes, so the product-card stepper never touches these)
    const step = event.target.closest('.preset_plus, .preset_minus');
    if (step) {
      const card = step.closest('.preset_card');
      const input = card.querySelector('.preset_qty');
      let value = parseInt(input.value) || 1;
      value = step.classList.contains('preset_plus') ? value + 1 : value - 1;
      if (value < 1) value = 1;
      input.value = value;
      update_servings(card);
      return;
    }

    // "+ Order" -> add all ingredients of this preset to the cart
    const order = event.target.closest('.preset_order_button');
    if (!order) return;

    if (!AUTHED) {
      alert('Please log in or register to add items to your cart.');
      return;
    }

    const card = order.closest('.preset_card');
    let servings = parseInt(card.querySelector('.preset_qty').value) || 1;
    if (servings < 1) servings = 1;

    const label = order.textContent;
    order.disabled = true;
    fetch(ADD_URL, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `preset_id=${card.dataset.id}&servings=${servings}`,
    })
      .then(response => response.json())
      .then(data => {
        order.textContent = data.ok ? 'Added ✓' : '+ Order';
        setTimeout(() => { order.textContent = label; order.disabled = false; }, 1200);
      })
      .catch(() => { order.textContent = label; order.disabled = false; });
  });

  // keep a typed servings value valid and the label in sync
  document.addEventListener('input', (event) => {
    const input = event.target.closest('.preset_qty');
    if (input) update_servings(input.closest('.preset_card'));
  });

  // ---- Create-preset overlay (logged-in users only) -------------------------
  const overlay = document.querySelector('.preset_overlay');
  const add_button = document.querySelector('.preset_add_button');
  if (!overlay || !add_button) return;

  const form = overlay.querySelector('.preset_form');
  const search = overlay.querySelector('.preset_ingredient_search');
  const results = overlay.querySelector('.preset_search_results');
  const selected = overlay.querySelector('.preset_selected');
  const error = overlay.querySelector('.preset_form_error');
  const name_input = form.querySelector('input[name="name"]');
  const chosen = new Set();   // product ids already added

  function open_overlay() { overlay.classList.remove('hidden'); name_input.focus(); }
  function close_overlay() { overlay.classList.add('hidden'); }

  add_button.addEventListener('click', open_overlay);
  overlay.querySelector('.preset_modal_close').addEventListener('click', close_overlay);
  overlay.addEventListener('click', (event) => {          // click on the backdrop
    if (event.target === overlay) close_overlay();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !overlay.classList.contains('hidden')) close_overlay();
  });

  // Search the already-loaded catalogue for ingredients to add.
  search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    results.innerHTML = '';
    if (!query) return;
    PRODUCTS
      .filter(p => p.name.toLowerCase().includes(query) ||
                   p.brand.toLowerCase().includes(query) ||
                   p.subcategory.toLowerCase().includes(query))
      .slice(0, 8)
      .forEach(p => {
        const row = document.createElement('button');
        row.type = 'button';
        row.className = 'preset_result_row';
        row.dataset.id = p.id;
        row.dataset.name = p.name;
        row.textContent = `${p.name} — ${p.brand}`;
        if (chosen.has(p.id)) row.disabled = true;
        results.appendChild(row);
      });
  });

  // Add an ingredient (click a search result).
  results.addEventListener('click', (event) => {
    const row = event.target.closest('.preset_result_row');
    if (!row) return;
    const id = parseInt(row.dataset.id);
    if (chosen.has(id)) return;
    chosen.add(id);
    const chip = document.createElement('span');
    chip.className = 'preset_chip';
    chip.dataset.id = id;
    chip.innerHTML = `${row.dataset.name}<button type="button" class="preset_chip_remove" title="Remove">✕</button>` +
                     `<input type="hidden" name="ingredients" value="${id}" />`;
    selected.appendChild(chip);
    row.disabled = true;
  });

  // Remove an ingredient chip.
  selected.addEventListener('click', (event) => {
    const remove = event.target.closest('.preset_chip_remove');
    if (!remove) return;
    const chip = remove.closest('.preset_chip');
    chosen.delete(parseInt(chip.dataset.id));
    chip.remove();
  });

  // Submit -> create the preset, then show it alongside the defaults.
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    error.textContent = '';
    if (chosen.size === 0) {
      error.textContent = 'Add at least one ingredient.';
      return;
    }
    fetch(CREATE_URL, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      body: new URLSearchParams(new FormData(form)),
    })
      .then(response => response.json())
      .then(data => {
        if (!data.ok) {
          error.textContent = 'Could not create the preset — check the name and ingredients.';
          return;
        }
        PRESETS.push(data.preset);
        grid.appendChild(build_preset_card(data.preset));
        form.reset();
        selected.innerHTML = '';
        results.innerHTML = '';
        chosen.clear();
        close_overlay();
      })
      .catch(() => { error.textContent = 'Something went wrong. Please try again.'; });
  });
})();

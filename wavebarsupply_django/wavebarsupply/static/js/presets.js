// ----------------------------------------------------------------------------
// Cocktail presets on the Browse page.
//   * builds a card per preset (default presets + the user's own),
//   * each card has a servings stepper and a "+ Order" that adds EVERY ingredient
//     to the cart (quantity = servings),
//   * the user's OWN presets also get Edit and Delete buttons,
//   * logged-in users can create/edit presets via the overlay.
// All of this is vanilla JS and self-contained in an IIFE.
// ----------------------------------------------------------------------------
(function () {
  const grid = document.querySelector('.preset_grid');
  if (!grid) return;

  const CSRF = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
  const AUTHED = document.body.dataset.authenticated === 'true';
  const ADD_URL = grid.dataset.addUrl;
  const CREATE_URL = grid.dataset.createUrl;
  const EDIT_URL = grid.dataset.editUrl;      // .../presets/0/edit/  (0 is a placeholder)
  const DELETE_URL = grid.dataset.deleteUrl;  // .../presets/0/delete/

  const PRESETS = JSON.parse(document.querySelector('#presets_data').textContent);
  const PRODUCTS = JSON.parse(document.querySelector('#products_data').textContent);

  // Build a concrete edit/delete URL for a given preset id from the placeholder.
  const edit_url = (id) => EDIT_URL.replace('/0/', '/' + id + '/');
  const delete_url = (id) => DELETE_URL.replace('/0/', '/' + id + '/');

  // ---- Build and render preset cards ----------------------------------------
  // Each unit of a preset's ingredients makes roughly 10 servings, so the figure
  // shown is (quantity × 10) and therefore moves in steps of 10.
  function servings_line(quantity) {
    return `About <span class="preset_servings_count">${quantity * 10}</span> servings`;
  }

  function build_preset_card(preset) {
    const card = document.createElement('div');
    card.className = 'preset_card';
    card.dataset.id = preset.id;
    const owner_actions = preset.owned ? `
      <div class="preset_owner_actions">
        <button class="preset_edit_button" type="button" title="Edit preset">✎</button>
        <button class="preset_delete_button" type="button" title="Delete preset">🗑</button>
      </div>` : '';
    card.innerHTML = `
      <div class="preset_card_thumb" style="background:${preset.color}">${owner_actions}</div>
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

  // ---- Search the presets by name -------------------------------------------
  // Filters the visible cards as the user types. Matching is by preset name and
  // by ingredient names, so searching e.g. "rum" also finds presets using rum.
  const preset_search = document.querySelector('.preset_search_input');
  const preset_search_clear = document.querySelector('.preset_search_clear');
  const preset_no_match = document.querySelector('.preset_no_match');

  function filter_presets() {
    const query = (preset_search ? preset_search.value : '').trim().toLowerCase();
    let visible = 0;
    grid.querySelectorAll('.preset_card').forEach(card => {
      const preset = PRESETS.find(p => String(p.id) === String(card.dataset.id));
      const haystack = preset
        ? (preset.name + ' ' + preset.ingredient_names.join(' ')).toLowerCase()
        : card.textContent.toLowerCase();
      const match = query === '' || haystack.includes(query);
      card.classList.toggle('hidden', !match);
      if (match) visible += 1;
    });
    if (preset_no_match) preset_no_match.classList.toggle('hidden', visible !== 0);
  }

  if (preset_search) {
    preset_search.addEventListener('input', filter_presets);
  }
  if (preset_search_clear) {
    preset_search_clear.addEventListener('click', () => {
      if (preset_search) preset_search.value = '';
      filter_presets();
    });
  }

  // ---- Read-only ingredient overlay (opens when a card is clicked) -----------
  const view_overlay = document.querySelector('.preset_view_overlay');

  function open_view(preset) {
    if (!view_overlay) return;
    view_overlay.querySelector('.preset_view_title').textContent = preset.name;
    const list = view_overlay.querySelector('.preset_view_list');
    list.innerHTML = '';
    preset.ingredient_names.forEach(name => {
      const li = document.createElement('li');
      li.textContent = name;
      list.appendChild(li);
    });
    view_overlay.classList.remove('hidden');
  }
  function close_view() { if (view_overlay) view_overlay.classList.add('hidden'); }

  if (view_overlay) {
    view_overlay.querySelector('.preset_view_close').addEventListener('click', close_view);
    view_overlay.addEventListener('click', (event) => {   // click on the backdrop
      if (event.target === view_overlay) close_view();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !view_overlay.classList.contains('hidden')) close_view();
    });
  }

  // ---- Servings stepper + "+ Order" + edit/delete ---------------------------
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

    // Delete the user's own preset
    const del = event.target.closest('.preset_delete_button');
    if (del) {
      const card = del.closest('.preset_card');
      const id = card.dataset.id;
      if (!window.confirm('Delete this preset?')) return;
      fetch(delete_url(id), {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF },
      })
        .then(response => response.json())
        .then(data => {
          if (!data.ok) return;
          card.remove();
          const idx = PRESETS.findIndex(p => String(p.id) === String(id));
          if (idx !== -1) PRESETS.splice(idx, 1);
          filter_presets();
        })
        .catch(() => {});
      return;
    }

    // Edit the user's own preset -> open the overlay pre-filled
    const editBtn = event.target.closest('.preset_edit_button');
    if (editBtn) {
      const id = editBtn.closest('.preset_card').dataset.id;
      const preset = PRESETS.find(p => String(p.id) === String(id));
      if (preset) open_edit(preset);
      return;
    }

    // "+ Order" -> add all ingredients of this preset to the cart
    const order = event.target.closest('.preset_order_button');
    if (order) {
      if (!AUTHED) {
        showMessage('Please log in or register to add items to your cart.');
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
      return;
    }

    // A plain click anywhere else on the card opens the ingredient overlay
    // (the quantity input is excluded so the user can still type in it).
    const view_card = event.target.closest('.preset_card');
    if (view_card && !event.target.closest('.preset_qty')) {
      const preset = PRESETS.find(p => String(p.id) === String(view_card.dataset.id));
      if (preset) open_view(preset);
    }
  });

  // keep a typed servings value valid and the label in sync
  document.addEventListener('input', (event) => {
    const input = event.target.closest('.preset_qty');
    if (input) update_servings(input.closest('.preset_card'));
  });

  // ---- Create / edit overlay (logged-in users only) -------------------------
  const overlay = document.querySelector('.preset_overlay');
  const add_button = document.querySelector('.preset_add_button');
  if (!overlay || !add_button) return;

  const form = overlay.querySelector('.preset_form');
  const search = overlay.querySelector('.preset_ingredient_search');
  const results = overlay.querySelector('.preset_search_results');
  const selected = overlay.querySelector('.preset_selected');
  const error = overlay.querySelector('.preset_form_error');
  const name_input = form.querySelector('input[name="name"]');
  const color_input = form.querySelector('input[name="color"]');
  const modal_title = overlay.querySelector('.preset_modal_title');
  const submit_button = overlay.querySelector('.preset_submit');
  const chosen = new Set();   // product ids already added
  let editing_id = null;      // null = creating, otherwise the preset being edited

  function reset_form() {
    form.reset();
    selected.innerHTML = '';
    results.innerHTML = '';
    error.textContent = '';
    chosen.clear();
  }

  function add_ingredient(id, product_name) {
    id = parseInt(id);
    if (chosen.has(id)) return;
    chosen.add(id);
    const chip = document.createElement('span');
    chip.className = 'preset_chip';
    chip.dataset.id = id;
    chip.innerHTML = `${product_name}<button type="button" class="preset_chip_remove" title="Remove">✕</button>` +
                     `<input type="hidden" name="ingredients" value="${id}" />`;
    selected.appendChild(chip);
  }

  function open_create() {
    editing_id = null;
    reset_form();
    modal_title.textContent = 'Create a Cocktail Preset';
    submit_button.textContent = 'Create Preset';
    overlay.classList.remove('hidden');
    name_input.focus();
  }

  function open_edit(preset) {
    editing_id = preset.id;
    reset_form();
    name_input.value = preset.name;
    if (color_input) color_input.value = preset.color;
    preset.ingredient_ids.forEach((id, i) => add_ingredient(id, preset.ingredient_names[i]));
    modal_title.textContent = 'Edit Cocktail Preset';
    submit_button.textContent = 'Save Changes';
    overlay.classList.remove('hidden');
    name_input.focus();
  }

  function close_overlay() { overlay.classList.add('hidden'); }

  add_button.addEventListener('click', open_create);
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
    add_ingredient(row.dataset.id, row.dataset.name);
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

  // Submit -> create a new preset or save an edited one.
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    error.textContent = '';
    if (chosen.size === 0) {
      error.textContent = 'Add at least one ingredient.';
      return;
    }
    const url = editing_id ? edit_url(editing_id) : CREATE_URL;
    fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      body: new URLSearchParams(new FormData(form)),
    })
      .then(response => response.json())
      .then(data => {
        if (!data.ok) {
          error.textContent = 'Could not save the preset — check the name and ingredients.';
          return;
        }
        data.preset.owned = true;   // it's the current user's preset
        if (editing_id) {
          // replace the existing card and stored data
          const idx = PRESETS.findIndex(p => String(p.id) === String(editing_id));
          if (idx !== -1) PRESETS[idx] = data.preset;
          const oldCard = grid.querySelector(`.preset_card[data-id="${editing_id}"]`);
          if (oldCard) oldCard.replaceWith(build_preset_card(data.preset));
        } else {
          // A brand-new preset belongs to the user, so it goes to the front,
          // ahead of the default presets, matching the server-side ordering.
          PRESETS.unshift(data.preset);
          grid.prepend(build_preset_card(data.preset));
        }
        reset_form();
        close_overlay();
        filter_presets();
      })
      .catch(() => { error.textContent = 'Something went wrong. Please try again.'; });
  });
})();

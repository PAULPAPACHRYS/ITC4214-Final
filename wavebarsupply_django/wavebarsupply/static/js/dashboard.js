(function () {
  const dashboard = document.querySelector('.dashboard');
  if (!dashboard) return;

  const CSRF = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
  const EDIT_URL = dashboard.dataset.editUrl;
  const DELETE_URL = dashboard.dataset.deleteUrl;
  const edit_url = (id) => EDIT_URL.replace('/0/', '/' + id + '/');
  const delete_url = (id) => DELETE_URL.replace('/0/', '/' + id + '/');

  const presets_el = document.querySelector('#presets_data');
  const products_el = document.querySelector('#products_data');
  const PRESETS = presets_el ? JSON.parse(presets_el.textContent) : [];
  const PRODUCTS = products_el ? JSON.parse(products_el.textContent) : [];

  //reveal and hide the orders item list
  dashboard.addEventListener('click', (event) => {
    const toggle = event.target.closest('.order_toggle');
    if (!toggle) return;
    const items = toggle.closest('.order_card').querySelector('.order_items');
    const nowHidden = items.classList.toggle('hidden');
    toggle.classList.toggle('open', !nowHidden);
  });

  // delete preset
  dashboard.addEventListener('click', (event) => {
    const del = event.target.closest('.dash_preset_delete');
    if (!del) return;
    const card = del.closest('.dash_preset_card');
    const id = card.dataset.id;
    if (!window.confirm('Delete this preset?')) return;
    fetch(delete_url(id), { method: 'POST', headers: { 'X-CSRFToken': CSRF } })
      .then(response => response.json())
      .then(data => {
        if (!data.ok) return;
        card.remove();
        const idx = PRESETS.findIndex(p => String(p.id) === String(id));
        if (idx !== -1) PRESETS.splice(idx, 1);
        show_empty_if_needed();
      })
      .catch(() => {});
  });

  function show_empty_if_needed() {
    const list = dashboard.querySelector('.dash_preset_list');
    if (list && !list.querySelector('.dash_preset_card')) {
      const message = document.createElement('p');
      message.className = 'dash_empty';
      message.textContent = "You haven't created any cocktail presets yet.";
      list.replaceWith(message);
    }
  }

  // edit preset
  const overlay = document.querySelector('.preset_overlay');
  if (!overlay) return;

  const form = overlay.querySelector('.preset_form');
  const search = overlay.querySelector('.preset_ingredient_search');
  const results = overlay.querySelector('.preset_search_results');
  const selected = overlay.querySelector('.preset_selected');
  const error = overlay.querySelector('.preset_form_error');
  const name_input = form.querySelector('input[name="name"]');
  const color_input = form.querySelector('input[name="color"]');
  const chosen = new Set();
  let editing_id = null;

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

  function open_edit(preset) {
    editing_id = preset.id;
    form.reset();
    selected.innerHTML = '';
    results.innerHTML = '';
    error.textContent = '';
    chosen.clear();
    name_input.value = preset.name;
    if (color_input) color_input.value = preset.color;
    preset.ingredient_ids.forEach((id, i) => add_ingredient(id, preset.ingredient_names[i]));
    overlay.classList.remove('hidden');
    name_input.focus();
  }
  function close_overlay() { overlay.classList.add('hidden'); }

  // open the overlay from a preset card's edit button
  dashboard.addEventListener('click', (event) => {
    const editBtn = event.target.closest('.dash_preset_edit');
    if (!editBtn) return;
    const id = editBtn.closest('.dash_preset_card').dataset.id;
    const preset = PRESETS.find(p => String(p.id) === String(id));
    if (preset) open_edit(preset);
  });

  overlay.querySelector('.preset_modal_close').addEventListener('click', close_overlay);
  overlay.addEventListener('click', (event) => { if (event.target === overlay) close_overlay(); });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !overlay.classList.contains('hidden')) close_overlay();
  });

  //search the catalogue for ingredients to add
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

  results.addEventListener('click', (event) => {
    const row = event.target.closest('.preset_result_row');
    if (!row) return;
    add_ingredient(row.dataset.id, row.dataset.name);
    row.disabled = true;
  });

  selected.addEventListener('click', (event) => {
    const remove = event.target.closest('.preset_chip_remove');
    if (!remove) return;
    const chip = remove.closest('.preset_chip');
    chosen.delete(parseInt(chip.dataset.id));
    chip.remove();
  });

  // save the changes and update
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    error.textContent = '';
    if (chosen.size === 0) {
      error.textContent = 'Add at least one ingredient.';
      return;
    }
    fetch(edit_url(editing_id), {
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
        const preset = { ...data.preset, owned: true };
        const idx = PRESETS.findIndex(p => String(p.id) === String(editing_id));
        if (idx !== -1) PRESETS[idx] = preset;
        const card = dashboard.querySelector(`.dash_preset_card[data-id="${editing_id}"]`);
        if (card) {
          card.querySelector('.dash_preset_swatch').style.background = preset.color;
          card.querySelector('.dash_preset_name').textContent = preset.name;
          card.querySelector('.dash_preset_ingredients').textContent = preset.ingredient_names.join(', ');
        }
        close_overlay();
      })
      .catch(() => { error.textContent = 'Something went wrong. Please try again.'; });
  });
})();

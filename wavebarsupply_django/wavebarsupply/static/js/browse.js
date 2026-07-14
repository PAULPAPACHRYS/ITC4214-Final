// The full catalogue is supplied by the Django view inside a
// <script id="products_data"> block (Django's json_script filter), replacing
// the old global PRODUCTS array that used to live in data.js.
const PRODUCTS = JSON.parse(document.querySelector('#products_data').textContent);

// track the state of the selected filters
const state = {
  search:      '',
  category:    'all',
  subcategory: [],
  brands:      [],
  volumes:     [],
  alcohol:     [],
  price_min:   0,
  price_max:   200,
  sort:        'default',
};

//remove dupplicate values
function unique(arr) {
  return [...new Set(arr)].sort();
}

// abv is now a real number (e.g. 4.7, 13.0, 40.0). Map it to the same bands the
// alcohol-content checkboxes use: none (0%), low (<8%), medium (8-20%), high (20%+).
function abv_band(abv) {
  if (abv === 0)  return 'none';
  if (abv < 8)    return 'low';
  if (abv < 20)   return 'medium';
  return 'high';
}

//subcategory options, grouped by category, sent by the server from the
//Subcategory table (so adding a sub-category in the Database page is enough)
const SUBCATEGORIES = JSON.parse(
  document.querySelector('#subcategories_data').textContent);

//changes dynamicaly the product subcategories when the main category changes
function build_subcategory_filter() {
  const list = document.querySelector('#subcategory_list');
  list.innerHTML = '';

  //if no category is selected then load all elements of the 3 arrays inside SUBCATEGORIES into subs (using .flat() at the end)
  //otherwise only take the elements from the subcategory array or an empty one if it does not exist
  const subs = state.category === 'all' ? Object.values(SUBCATEGORIES).flat() : (SUBCATEGORIES[state.category] || []);

  //loops through the list and create a checkbox for each element
  subs.forEach(sub => {
    const label = document.createElement('label');
    label.className = 'filter_check_label';
    const checked = state.subcategory.includes(sub) ? 'checked' : ''; //keeps user's selected options after every render
    label.innerHTML = `<input type="checkbox" class="sub_filter_check" value="${sub}" ${checked} /> ${sub}`;
    list.appendChild(label);
  });

  // attach listeners to every new sub_filter_check we created previously
  list.querySelectorAll('.sub_filter_check').forEach(cb => {
    cb.addEventListener('change', () => {
      // the ... converts the type to an array so that .map() can be used to get the value of each element
      // save everything to state.subcategory to reflect the user's selection
      state.subcategory = [...list.querySelectorAll('.sub_filter_check:checked')].map(c => c.value);
      render();
    });
  });
}

// create the product brand filters
function build_brand_filter() {
  const all_brands = unique(PRODUCTS.map(p => p.brand)); //grabs all brands and removes dublicates
  const list = document.querySelector('#brand_filter_list');
  list.innerHTML = '';

  //loops through the brands and create checkbox for each
  all_brands.forEach(brand => {
    const label = document.createElement('label');
    label.className = 'filter_check_label';
    const checked = state.brands.includes(brand) ? 'checked' : '';
    label.innerHTML = `<input type="checkbox" class="brand_filter_check" value="${brand}" ${checked} /> ${brand}`;
    list.appendChild(label);
  });

  // attach event listeners for every brand_filter_check we create
  list.querySelectorAll('.brand_filter_check').forEach(cb => {
    cb.addEventListener('change', () => {
      state.brands = [...list.querySelectorAll('.brand_filter_check:checked')].map(c => c.value);
      render();
    });
  });
}

//similar to the above but create the product volume filters
function build_volume_filter() {
  const all_volumes = unique(PRODUCTS.map(p => p.volume));
  const list = document.querySelector('#volume_filter_list');
  list.innerHTML = '';

  all_volumes.forEach(vol => {
    const label = document.createElement('label');
    label.className = 'filter_check_label';
    const checked = state.volumes.includes(vol) ? 'checked' : '';
    label.innerHTML = `<input type="checkbox" class="volume_filter_check" value="${vol}" ${checked} /> ${vol}`;
    list.appendChild(label);
  });

  list.querySelectorAll('.volume_filter_check').forEach(cb => {
    cb.addEventListener('change', () => {
      state.volumes = [...list.querySelectorAll('.volume_filter_check:checked')].map(c => c.value);
      render();
    });
  });
}

//handles all filtering
function filter_products() {
  let results = [...PRODUCTS];

  // keeps only the products from the category the user selected
  if (state.category !== 'all')
    results = results.filter(p => p.category === state.category);

   // same as above but for subcategory, use include because users can select multiple checkboxes
  if (state.subcategory.length > 0)
    results = results.filter(p => state.subcategory.includes(p.subcategory));

  // checks if search field contains something
  if (state.search.trim()) {
    const q = state.search.trim().toLowerCase();
    //tries to match the search with name, brand, subcategory or tags
    results = results.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.brand.toLowerCase().includes(q) ||
      p.subcategory.toLowerCase().includes(q) ||
      p.tags.some(t => t.toLowerCase().includes(q))
    );
    //using .some() for tags because we want to see if any tag match, so if at least one tag matches we keep it
  }

  // filters price by including products only within the min and max values
  results = results.filter(p => p.price >= state.price_min && p.price <= state.price_max);

  // keeps only products of selected brands
  if (state.brands.length > 0)
    results = results.filter(p => state.brands.includes(p.brand));

  // keeps only products of selected volumns
  if (state.volumes.length > 0)
    results = results.filter(p => state.volumes.includes(p.volume));

  //keeps only products of selected alcohol precentage (band derived from abv %)
  if (state.alcohol.length > 0)
    results = results.filter(p => state.alcohol.includes(abv_band(p.abv)));

  // apply any sorting selected
  if (state.sort === 'price_asc')  results.sort((a,b) => a.price - b.price);
  if (state.sort === 'price_desc') results.sort((a,b) => b.price - a.price);

  //localCompare is a better option because it compares strings according to language rules
  if (state.sort === 'name_asc')   results.sort((a,b) => a.name.localeCompare(b.name));
  if (state.sort === 'name_desc')  results.sort((a,b) => b.name.localeCompare(a.name));

  return results;
}

// creates the product cards for each product
function build_product_card(product) {
  const card = document.createElement('div');
  card.className = 'product_card';

  card.innerHTML = `
    <div class="product_card_thumb">${product.image ? `<img class="product_card_image" src="${product.image}" alt="${product.name}">` : ''}</div>
    <div class="product_card_body">
      <span class="product_card_category">${product.subcategory}</span>
      <p class="product_card_name">${product.name}</p>
      <p class="product_card_brand">${product.brand} · ${product.volume}</p>
      <div class="product_card_meta">
        ${product.tags.slice(0,3).map(t => `<span class="product_tag">${t}</span>`).join('')}
      </div>
      <div class="product_card_footer">
        <p class="product_card_price">€${product.price.toFixed(2)}<span>/unit</span></p>
        <div class="qty_control">
          <button class="qty_btn qty_minus" type="button">-</button>
          <input class="qty_input" type="number" min="1" value="1" />
          <button class="qty_btn qty_plus" type="button">+</button>
        </div>
        <button class="button_add_to_order" data-id="${product.id}">+ Order</button>
      </div>
      <div class="like_control">
        <button class="like_button ${product.liked ? 'liked' : ''}" type="button" data-id="${product.id}" aria-pressed="${product.liked ? 'true' : 'false'}"><span class="like_heart">♥</span> Like</button>
        <span class="like_count">${product.like_count}</span>
      </div>
    </div>
  `;
  return card;
}

//updates the page
function render() {
  const results = filter_products(); // displays eveything in the results after calling filter_products
  const grid    = document.querySelector('#product_grid');
  const empty   = document.querySelector('#empty_state');
  const count   = document.querySelector('#results_count');

  grid.innerHTML = '';

  if (results.length === 0) {
    empty.classList.remove('hidden');
    count.textContent = 'No products found';
  } else {
    empty.classList.add('hidden');
    count.textContent = `Showing ${results.length} product${results.length !== 1 ? 's' : ''}`;
    results.forEach(p => grid.appendChild(build_product_card(p)));
  }
}

//read the URL and apply filters from the home page
function apply_url_params() {
  //window.location.search returns the url part after the '?'
  //URLSearchParams creates an object that can read query parameters
  const params = new URLSearchParams(window.location.search);
  const cat = params.get('cat');
  if (cat && ['non-alcohol','fermented','distilled'].includes(cat)) {
    state.category = cat;
    document.querySelectorAll('.category_tab').forEach(tab => {
      //pre-selects a category if the user clicked on of the category buttons from the home page
      tab.classList.toggle('active', tab.dataset.cat === cat);
    });
    build_subcategory_filter();
  }
}

// reset filters and bring the page to the original state
function reset_filters() {
  state.search      = '';
  state.category    = 'all';
  state.subcategory = [];
  state.brands      = [];
  state.volumes     = [];
  state.alcohol     = [];
  state.price_min   = 0;
  state.price_max   = 200;
  state.sort        = 'default';

  document.querySelector('#search_input').value = '';
  document.querySelector('#price_min_slider').value = 0;
  document.querySelector('#price_max_slider').value = 200;
  document.querySelector('#price_min_display').textContent = '0';
  document.querySelector('#price_max_display').textContent = '200';
  document.querySelector('#sort_select').value = 'default';

  document.querySelectorAll('.category_tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.cat === 'all');
  });

  document.querySelectorAll('.alcohol_filter_check').forEach(cb => { cb.checked = false; });

  build_subcategory_filter();
  build_brand_filter();
  build_volume_filter();
  render();
}

/*
 * Event Listeners Section
 */

// search input
document.querySelector('#search_input').addEventListener('input', (e) => {
  state.search = e.target.value;
  render();
});

// clear search
document.querySelector('#search_clear_button').addEventListener('click', () => {
  state.search = '';
  document.querySelector('#search_input').value = '';
  render();
});

// category tabs
document.querySelectorAll('.category_tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.category_tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    state.category    = tab.dataset.cat;
    state.subcategory = [];
    build_subcategory_filter();
    render();
  });
});

// price sliders for min and max price
document.querySelector('#price_min_slider').addEventListener('input', (e) => {
  let val = parseInt(e.target.value);
  if (val > state.price_max - 1) val = state.price_max - 1;
  state.price_min = val;
  document.querySelector('#price_min_display').textContent = val;
  e.target.value = val;
  render();
});

document.querySelector('#price_max_slider').addEventListener('input', (e) => {
  let val = parseInt(e.target.value);
  if (val < state.price_min + 1) val = state.price_min + 1;
  state.price_max = val;
  document.querySelector('#price_max_display').textContent = val;
  e.target.value = val;
  render();
});

//alcohol filter checkboxes
document.querySelector('#alcohol_filter_list').addEventListener('change', () => {
  state.alcohol = [...document.querySelectorAll('.alcohol_filter_check:checked')].map(c => c.value);
  render();
});

//sort selection
document.querySelector('#sort_select').addEventListener('change', (e) => {
  state.sort = e.target.value;
  render();
});

// reset filters button on the sidebar
document.querySelector('#reset_filters_button').addEventListener('click', reset_filters);

// reset filters button on empty search
document.querySelector('#empty_reset_button').addEventListener('click', reset_filters);

// Initialize
build_subcategory_filter();
build_brand_filter();
build_volume_filter();
apply_url_params();
render();

// ----------------------------------------------------------------------------
// Database page behaviour: delete confirmation, column sorting, and per-table
// search. All rows are already rendered by Django, so sorting and searching are
// done client-side on the existing table.
// ----------------------------------------------------------------------------

// --- Ask for confirmation before a delete form is submitted (unchanged) ---
document.querySelectorAll('.db_delete_form').forEach(form => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm('Delete this record? This cannot be undone.')) {
      event.preventDefault();
    }
  });
});

// --- Sorting + search (only runs on the table page) ---
const table = document.querySelector('.db_table');
if (table) {
  const tbody = table.querySelector('tbody');
  const noMatchRow = tbody.querySelector('.db_no_match');
  const headers = [...table.querySelectorAll('thead th.db_sortable')];

  // Real data rows only: they always have an actions cell. This skips both the
  // "No records yet" row and the hidden "No matching records" row.
  function dataRows() {
    return [...tbody.querySelectorAll('tr')].filter(tr => tr.querySelector('.db_actions_col'));
  }

  // The trimmed text of a row's cell at a given column index.
  function cellText(row, index) {
    const cell = row.children[index];
    return cell ? cell.textContent.trim() : '';
  }

  // ---- Column type detection (drives how a column is compared) ----
  function columnIsNumeric(index) {
    let sawValue = false;
    for (const row of dataRows()) {
      const text = cellText(row, index);
      if (text === '') continue;
      sawValue = true;
      if (isNaN(Number(text))) return false;
    }
    return sawValue;
  }

  // A date column: not numeric, but every value has a digit and parses as a date
  // (e.g. "July 9, 2026"). This keeps the Orders date column in real order.
  function columnIsDate(index) {
    let sawValue = false;
    for (const row of dataRows()) {
      const text = cellText(row, index);
      if (text === '') continue;
      sawValue = true;
      if (!/\d/.test(text) || isNaN(Date.parse(text))) return false;
    }
    return sawValue;
  }

  // ---- Sorting ----
  let sortIndex = -1;
  let sortAsc = true;

  function sortBy(index) {
    if (sortIndex === index) {
      sortAsc = !sortAsc;          // same column clicked -> flip direction
    } else {
      sortIndex = index;
      sortAsc = true;              // new column -> start ascending
    }

    const numeric = columnIsNumeric(index);
    const date = !numeric && columnIsDate(index);
    const rows = dataRows();

    rows.sort((a, b) => {
      const av = cellText(a, index);
      const bv = cellText(b, index);
      let cmp;
      if (numeric) {
        cmp = Number(av) - Number(bv);
      } else if (date) {
        cmp = Date.parse(av) - Date.parse(bv);
      } else {
        cmp = av.localeCompare(bv, undefined, { sensitivity: 'base', numeric: true });
      }
      return sortAsc ? cmp : -cmp;
    });

    // Re-insert in the new order, keeping the no-match row last.
    rows.forEach(row => tbody.insertBefore(row, noMatchRow));

    // Update the arrow indicators.
    headers.forEach((th, i) => {
      const arrow = th.querySelector('.db_sort_arrow');
      if (i === index) {
        th.classList.add('db_sorted');
        arrow.textContent = sortAsc ? '▲' : '▼';
      } else {
        th.classList.remove('db_sorted');
        arrow.textContent = '';
      }
    });
  }

  headers.forEach((th, i) => {
    th.addEventListener('click', () => sortBy(i));
    th.addEventListener('keydown', (event) => {   // keyboard support (Enter / Space)
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        sortBy(i);
      }
    });
  });

  // ---- Search ----
  const searchInput = document.querySelector('.db_search_input');
  const clearButton = document.querySelector('.db_search_clear');

  function applySearch() {
    const query = searchInput.value.trim().toLowerCase();
    const rows = dataRows();
    let visible = 0;

    rows.forEach(row => {
      // Match against every cell except the actions column.
      const cells = [...row.children].filter(td => !td.classList.contains('db_actions_col'));
      const text = cells.map(td => td.textContent).join(' ').toLowerCase();
      const match = text.includes(query);
      row.classList.toggle('hidden', !match);
      if (match) visible++;
    });

    // Show "No matching records" only when an active search hides every row.
    if (noMatchRow) {
      noMatchRow.classList.toggle('hidden', !(query !== '' && visible === 0 && rows.length > 0));
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', applySearch);
  }
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      applySearch();
      searchInput.focus();
    });
  }
}

// toggles the Account page between the read view and the edit form
const account_view = document.querySelector('#account_view');
const account_edit = document.querySelector('#account_edit');
const edit_button = document.querySelector('#edit_button');
const cancel_button = document.querySelector('#cancel_button');

if (edit_button) {
  edit_button.addEventListener('click', () => {
    account_view.classList.add('hidden');
    account_edit.classList.remove('hidden');
  });
}

if (cancel_button) {
  cancel_button.addEventListener('click', () => {
    account_edit.classList.add('hidden');
    account_view.classList.remove('hidden');
  });
}

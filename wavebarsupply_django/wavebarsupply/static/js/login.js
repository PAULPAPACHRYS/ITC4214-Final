// Form validation and submission are now handled server-side by Django's
// built-in forms (AuthenticationForm + UserCreationForm). This file keeps only
// the front-end UI behaviours: tab switching and the show/hide password toggle.

// hides or reveals the selected form (Login or Register)
function switch_panel(panel_name) {
  const login_panel    = document.querySelector('#panel_login');
  const register_panel = document.querySelector('#panel_register');
  const tab_login      = document.querySelector('#tab_login');
  const tab_register   = document.querySelector('#tab_register');

  if (panel_name === 'login') {
    login_panel.classList.remove('hidden');
    register_panel.classList.add('hidden');
    tab_login.classList.add('active');
    tab_register.classList.remove('active');
  } else {
    login_panel.classList.add('hidden');
    register_panel.classList.remove('hidden');
    tab_login.classList.remove('active');
    tab_register.classList.add('active');
  }
}

// hides or shows a password field when its toggle button is clicked
function setup_toggle(button_id, input_id) {
  const button = document.querySelector(`#${button_id}`);
  const input  = document.querySelector(`#${input_id}`);
  if (!button || !input) return;
  button.addEventListener('click', () => {
    if (input.type === 'password') {
      input.type = 'text';
      button.textContent = 'Hide';
    } else {
      input.type = 'password';
      button.textContent = 'Show';
    }
  });
}

// Initialise password toggles. The password inputs are rendered by Django, so
// their ids follow the "id_<field name>" convention.
setup_toggle('toggle_login_password', 'id_password');
setup_toggle('toggle_reg_password',   'id_password1');
setup_toggle('toggle_reg_confirm',    'id_password2');

// Tab buttons
document.querySelector('#tab_login').addEventListener('click',    () => switch_panel('login'));
document.querySelector('#tab_register').addEventListener('click', () => switch_panel('register'));

// Panel switch links inside each form
document.querySelector('#switch_to_register').addEventListener('click', (e) => {
  e.preventDefault();
  switch_panel('register');
});
document.querySelector('#switch_to_login').addEventListener('click', (e) => {
  e.preventDefault();
  switch_panel('login');
});

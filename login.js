
// displays an error message underneath an input field
function show_error(field_id, message) {
  const el = document.querySelector(`#${field_id}`);
  if (!el) return;
  el.textContent = message;
  el.classList.remove('hidden');
}

// removes the error text and hides the error field
function clear_error(field_id) {
  const el = document.querySelector(`#${field_id}`);
  if (!el) return;
  el.textContent = '';
  el.classList.add('hidden');
}

//used to change the appearance of the input box when the input message is not acceptable
function set_input_error(input, has_error) {
  if (has_error) {
    input.classList.add('input_error');
  } else {
    input.classList.remove('input_error');
  }
}

// displays a message for the entire form
function show_message(panel_id, type, message) {
  const el = document.querySelector(`#${panel_id}`);
  if (!el) return;
  el.textContent = message;
  el.className = `form_message ${type}`;
  el.classList.remove('hidden');
}

//hides the displayed message
function hide_message(panel_id) {
  const el = document.querySelector(`#${panel_id}`);
  if (!el) return;
  el.classList.add('hidden');
}

// uses a regular expression to check if the email has an acceptable pattern
function is_valid_email(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

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

// Validate the Login form input
function validate_login() {
  //get the elements that need validation
  const email    = document.querySelector('#login_email');
  const password = document.querySelector('#login_password');
  let valid      = true;

  //clear the fields just in case 
  clear_error('login_email_error');
  clear_error('login_password_error');
  hide_message('login_message');

  //check if there is on input and if the email entered follows an appropriate email pattern
  if (!email.value.trim()) {
    show_error('login_email_error', 'Email is required.');
    set_input_error(email, true);
    valid = false;
  } else if (!is_valid_email(email.value.trim())) { 
    show_error('login_email_error', 'Please enter a valid email address.');
    set_input_error(email, true);
    valid = false;
  } else {
    set_input_error(email, false);
  }

  //checks if there is no input
  if (!password.value) {
    show_error('login_password_error', 'Password is required.');
    set_input_error(password, true);
    valid = false;
  } else {
    set_input_error(password, false);
  }

  // if everything there are no issues then accept login and redirect to the browse page
  if (valid) {
    show_message('login_message', 'success', 'Logged in successfully! Redirecting to catalogue…');
    setTimeout(() => { window.location.href = 'browse.html'; }, 1800);
  }
}

// Validate the Register form input
function validate_register() {
  // get all the elements that need validation
  const first_name = document.querySelector('#reg_first_name');
  const last_name = document.querySelector('#reg_last_name');
  const bar_name = document.querySelector('#reg_bar_name');
  const email = document.querySelector('#reg_email');
  const phone = document.querySelector('#reg_phone');
  const location = document.querySelector('#reg_location');
  const password = document.querySelector('#reg_password');
  const confirm = document.querySelector('#reg_confirm_password');
  const terms = document.querySelector('#reg_terms');
  let valid = true;

  //clear the fields
  const errorFields = ['reg_first_name','reg_last_name','reg_bar_name','reg_email',
    'reg_phone','reg_location','reg_password','reg_confirm','reg_terms'];
  errorFields.forEach(f => clear_error(`${f}_error`));
  hide_message('register_message');

  //check if any field is left empty
  if (!first_name.value.trim()) {
    show_error('reg_first_name_error', 'First name is required.');
    set_input_error(first_name, true); valid = false;
  } else { 
    set_input_error(first_name, false); 
  }
  if (!last_name.value.trim()) {
    show_error('reg_last_name_error', 'Last name is required.');
    set_input_error(last_name, true); valid = false;
  } else { set_input_error(last_name, false); }

  if (!bar_name.value.trim()) {
    show_error('reg_bar_name_error', 'Business name is required.');
    set_input_error(bar_name, true); valid = false;
  } else { set_input_error(bar_name, false); }

  if (!email.value.trim()) {
    show_error('reg_email_error', 'Email is required.');
    set_input_error(email, true); valid = false;
  } else if (!is_valid_email(email.value.trim())) {
    show_error('reg_email_error', 'Please enter a valid email address.');
    set_input_error(email, true); valid = false;
  } else { set_input_error(email, false); }

  if (!phone.value.trim()) {
    show_error('reg_phone_error', 'Phone number is required.');
    set_input_error(phone, true); valid = false;
  } else { set_input_error(phone, false); }

  if (!location.value) {
    show_error('reg_location_error', 'Please select your region.');
    set_input_error(location, true); valid = false;
  } else { set_input_error(location, false); }

  //for password field also ask for the length to be greater than 8 characters for security
  if (!password.value) {
    show_error('reg_password_error', 'Password is required.');
    set_input_error(password, true); valid = false;
  } else if (password.value.length < 8) {
    show_error('reg_password_error', 'Password must be at least 8 characters.');
    set_input_error(password, true); valid = false;
  } else { set_input_error(password, false); }

  // also check if the input matches the password field
  if (!confirm.value) {
    show_error('reg_confirm_error', 'Please confirm your password.');
    set_input_error(confirm, true); valid = false;
  } else if (confirm.value !== password.value) {
    show_error('reg_confirm_error', 'Passwords do not match.');
    set_input_error(confirm, true); valid = false;
  } else { set_input_error(confirm, false); }

  //make sure terms and conditions are accepted
  if (!terms.checked) {
    show_error('reg_terms_error', 'You must accept the terms to continue.');
    valid = false;
  }

  //if no issue is present then display a confirmation message and redirect to browser page
  if (valid) {
    show_message('register_message', 'success', `Account created for ${first_name.value}! Welcome to WaveBar Supply.`);
    setTimeout(() => { window.location.href = 'browse.html'; }, 2000);
  }
}

/*
 *Event listeners 
 */

// hides or shows the password and confirm password's input fields
function setup_toggle(button_id, input_id) {
  const button   = document.querySelector(`#${button_id}`);
  const input = document.querySelector(`#${input_id}`);
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

// Initialize password toggles of the hide/show password button
setup_toggle('toggle_login_password',  'login_password');
setup_toggle('toggle_reg_password',    'reg_password');
setup_toggle('toggle_reg_confirm',     'reg_confirm_password');

// Tab buttons
document.querySelector('#tab_login').addEventListener('click',    () => switch_panel('login'));
document.querySelector('#tab_register').addEventListener('click', () => switch_panel('register'));

// Panel switch links for Login/Register
document.querySelector('#switch_to_register').addEventListener('click', (e) => {
  e.preventDefault();
  switch_panel('register');
});
document.querySelector('#switch_to_login').addEventListener('click', (e) => {
  e.preventDefault();
  switch_panel('login');
});

// Form submit buttons
document.querySelector('#login_submit_button').addEventListener('click',    validate_login);
document.querySelector('#register_submit_button').addEventListener('click', validate_register);

// Clear errors on input change
document.querySelector('#login_email').addEventListener('input',    () => clear_error('login_email_error'));
document.querySelector('#login_password').addEventListener('input', () => clear_error('login_password_error'));

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

//initialise password toggles
setup_toggle('toggle_login_password', 'id_password');
setup_toggle('toggle_reg_password',   'id_password1');
setup_toggle('toggle_reg_confirm',    'id_password2');

//tab buttons
document.querySelector('#tab_login').addEventListener('click',    () => switch_panel('login'));
document.querySelector('#tab_register').addEventListener('click', () => switch_panel('register'));

// panel switch links inside each form
document.querySelector('#switch_to_register').addEventListener('click', (e) => {
  e.preventDefault();
  switch_panel('register');
});
document.querySelector('#switch_to_login').addEventListener('click', (e) => {
  e.preventDefault();
  switch_panel('login');
});

// forgot password overlay and message
(function () {
  const link     = document.querySelector('#forgot_password_link');
  const overlay  = document.querySelector('#forgot_overlay');
  const close_btn = document.querySelector('#forgot_close');
  const done_btn  = document.querySelector('#forgot_done');
  const form      = document.querySelector('#forgot_form');
  const request_step = document.querySelector('#forgot_request');
  const success_step = document.querySelector('#forgot_success');
  if (!link || !overlay) return;

  function open_overlay() {
    request_step.classList.remove('hidden');
    success_step.classList.add('hidden');
    overlay.classList.remove('hidden');
  }

  function close_overlay() {
    overlay.classList.add('hidden');
  }

  link.addEventListener('click', (e) => {
    e.preventDefault();
    open_overlay();
  });

  close_btn.addEventListener('click', close_overlay);
  done_btn.addEventListener('click', close_overlay);

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      close_overlay();
    }
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!form.reportValidity()) return;
    request_step.classList.add('hidden');
    success_step.classList.remove('hidden');
  });
})();

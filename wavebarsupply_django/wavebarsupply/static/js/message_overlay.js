// replaces the browser's alert() pop-up with an overlay.
(function () {
  const overlay = document.querySelector('#message_overlay');
  if (!overlay) return;

  const text_holder  = overlay.querySelector('.message_text');
  const close_button = overlay.querySelector('.message_close');

  //exposed globally so other scripts can call it instead of alert()
  window.showMessage = function (message) {
    text_holder.textContent = message;
    overlay.classList.remove('hidden');
  };

  function hide_overlay() {
    overlay.classList.add('hidden');
  }

  close_button.addEventListener('click', hide_overlay);

  overlay.addEventListener('click', function (event) {
    if (event.target === overlay) {
      hide_overlay();
    }
  });
})();

jQuery(function ($) {
  // CSRF token, auth state and the endpoint URL come from the page just as thr cart AJAX gets them
  const CSRF = $('meta[name="csrf-token"]').attr('content');
  const AUTHED = document.body.dataset.authenticated === 'true';
  const TOGGLE_URL = document.body.dataset.likeToggleUrl;

  $(document).on('click', '.like_button', function () {
    const $button = $(this);

    if (!AUTHED) {
      showMessage('Please log in or register to like products.');
      return;
    }
    if ($button.hasClass('is_busy')) {
      return;
    }
    $button.addClass('is_busy');

    const productId = $button.data('id');
    const $count = $button.siblings('.like_count');

    $.ajax({
      url: TOGGLE_URL,
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      data: { product_id: productId },
    })
      .done(function (data) {
        if (!data.ok) return;
        $button.toggleClass('liked', data.liked);
        $button.attr('aria-pressed', data.liked ? 'true' : 'false');
        $count.text(data.count);
      })
      .always(function () {
        $button.removeClass('is_busy');
      });
  });
});

// ----------------------------------------------------------------------------
// Product "like" button — the ONLY part of the project written with jQuery.
// A click sends an AJAX POST ($.ajax) to the likes:toggle endpoint, then the
// button's state and the like count next to it are updated from the response.
// ----------------------------------------------------------------------------
jQuery(function ($) {
  // CSRF token, auth state and the endpoint URL come from the page (base.html),
  // the same way the cart AJAX gets them.
  const CSRF = $('meta[name="csrf-token"]').attr('content');
  const AUTHED = document.body.dataset.authenticated === 'true';
  const TOGGLE_URL = document.body.dataset.likeToggleUrl;

  // Cards are built dynamically, so the handler is delegated from the document.
  $(document).on('click', '.like_button', function () {
    const $button = $(this);

    if (!AUTHED) {
      alert('Please log in or register to like products.');
      return;
    }
    if ($button.hasClass('is_busy')) {
      return;                       // ignore extra clicks while a request runs
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

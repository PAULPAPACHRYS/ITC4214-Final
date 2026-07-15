// Checks name fields in the browser, so a mistake is caught before the form is
// sent. The server checks the same rule again (see accounts/validators.py) -
// this is only the fast feedback on top of it.
//
// Any input marked with data-name-check is checked. \p{L} means "a letter in any
// alphabet", so Greek and accented names pass, while digits and symbols do not.
// It is done here rather than with an HTML pattern attribute because browsers
// do not all handle a unicode pattern the same way.

(function () {
  const NAME_PATTERN = /^\p{L}+(?:[ '\-.]\p{L}+)*$/u;
  const MESSAGE = "Please use letters only. A name may include spaces, hyphens (-) "
                + "and apostrophes ('), but not numbers or symbols.";

  const fields = document.querySelectorAll('input[data-name-check]');

  fields.forEach(function (field) {
    function check() {
      const value = field.value.trim();
      // An empty box is left to the field's own "required" rule to report.
      if (value === '' || NAME_PATTERN.test(value)) {
        field.setCustomValidity('');       // valid: clear any previous message
      } else {
        field.setCustomValidity(MESSAGE);  // invalid: the browser blocks submit
      }
    }

    field.addEventListener('input', check);
    field.addEventListener('blur', check);
  });
})();

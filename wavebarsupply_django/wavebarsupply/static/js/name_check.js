// checks name fields in the browser before the form is sent, the server checks the same rule again 
// Greek and accented names pass, while digits and symbols do not
(function () {
  const NAME_PATTERN = /^\p{L}+(?:[ '\-.]\p{L}+)*$/u;
  const MESSAGE = "Please use letters only. A name may include spaces, hyphens (-) "
                + "and apostrophes ('), but not numbers or symbols.";

  const fields = document.querySelectorAll('input[data-name-check]');

  fields.forEach(function (field) {
    function check() {
      const value = field.value.trim();
      //an empty box is left to the field's own "required" rule
      if (value === '' || NAME_PATTERN.test(value)) {
        field.setCustomValidity('');       //valid: clear any previous message
      } else {
        field.setCustomValidity(MESSAGE);  //invalid: the browser blocks submit
      }
    }

    field.addEventListener('input', check);
    field.addEventListener('blur', check);
  });
})();

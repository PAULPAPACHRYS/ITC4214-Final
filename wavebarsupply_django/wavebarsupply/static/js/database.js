// Ask for confirmation before a delete form is submitted.
document.querySelectorAll('.db_delete_form').forEach(form => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm('Delete this record? This cannot be undone.')) {
      event.preventDefault();
    }
  });
});

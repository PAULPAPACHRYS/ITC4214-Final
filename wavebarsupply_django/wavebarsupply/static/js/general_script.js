// The navigation bar and footer now live in base.html (server-rendered with
// Django's {% url %} tags). This script just highlights the link for the page
// the visitor is currently on, matching the .nav_link.active style.
const current_path = window.location.pathname;
document.querySelectorAll('.nav_link').forEach(link => {
  if (link.getAttribute('href') === current_path) {
    link.classList.add('active');
  }
});

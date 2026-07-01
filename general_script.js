// navigation bar code
document.querySelector('.site_header').innerHTML=`
    <nav class="nav_bar">
      <a href="home.html" class="nav_logo">WaveBar<span>Supply</span></a>
      <ul class="nav_links">
        <li><a href="home.html" class="nav_link">Home</a></li>
        <li><a href="browse.html" class="nav_link">Browse</a></li>
        <li><a href="login.html" class="nav_link">Login / Register</a></li>
      </ul>
      <a href="browse.html" class="button_primary nav_cta">Shop Now</a>
    </nav>
`;

document.querySelector('.site_footer').innerHTML = `
    <div class="footer_inner">
      <p class="footer_logo">WaveBar<span>Supply</span></p>
      <p class="footer_copy">© 2025 WaveBar Supply. B2B wholesale beverages for beach bars.</p>
      <nav class="footer_nav">
        <a href="home.html">Home</a>
        <a href="browse.html">Browse</a>
        <a href="login.html">Login</a>
      </nav>
    </div>
`;
// Navbar Scroll Effect: Change background color when scrolling
window.onscroll = function() {changeNavbarColor()};

function changeNavbarColor() {
  var navbar = document.querySelector(".navbar");
  if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
    navbar.style.backgroundColor = "#003366"; // Dark blue when scrolled
  } else {
    navbar.style.backgroundColor = "transparent"; // Transparent when at the top
  }
}

// Smooth Scroll Effect for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth"
    });
  });
});

// Navbar Toggler Animation (if needed)
document.querySelector(".navbar-toggler").addEventListener("click", function() {
  this.classList.toggle("toggled");
  var navbarNav = document.querySelector("#navbarNav");
  navbarNav.classList.toggle("show");
});

// Example: Add hover effect for navbar links
const navLinks = document.querySelectorAll('.navbar-nav .nav-item .nav-link');
navLinks.forEach(link => {
  link.addEventListener('mouseenter', () => {
    link.style.color = '#ffeb3b';  // Change color on hover
  });
  link.addEventListener('mouseleave', () => {
    link.style.color = '';  // Reset color when hover ends
  });
});
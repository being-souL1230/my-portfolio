// Shimmer loader: hide after page load
window.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.getElementById('shimmer-loader').classList.remove('shimmer-active');
    }, 1200); // 1.2s shimmer
});

// Responsive navbar toggle
const navbarToggle = document.getElementById('navbar-toggle');
const navbarLinks = document.querySelector('.navbar-links');
if (navbarToggle && navbarLinks) {
    navbarToggle.addEventListener('click', function() {
        navbarLinks.classList.toggle('active');
    });
}

// Placeholder for details button interactivity
const detailsButtons = document.querySelectorAll('.details-btn');
detailsButtons.forEach(btn => {
    btn.addEventListener('click', function() {
        alert('Details coming soon!');
    });
}); 
/*
  Liquid Glass Interaction Engine
*/

// Mouse tracking for interior radial glows
document.querySelectorAll('.liquid-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    // Get mouse position relative to the card
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Update CSS variables for the pseudo-element glow
    card.style.setProperty('--mouse-x', `${x}px`);
    card.style.setProperty('--mouse-y', `${y}px`);
  });
});

// Staggered Entry Animations (Intersection Observer)
const observeOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      observer.unobserve(entry.target);
    }
  });
}, observeOptions);

document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));

// Video Interaction - Play on Hover for Liquid Cards
document.querySelectorAll('.liquid-card').forEach(card => {
  const video = card.querySelector('video');
  if (video && !video.hasAttribute('autoplay')) {
    card.addEventListener('mouseenter', () => {
      video.play();
      video.style.filter = 'saturate(1.5)';
    });
    
    card.addEventListener('mouseleave', () => {
      video.pause();
      video.style.filter = 'saturate(1)';
    });
  }
});

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});

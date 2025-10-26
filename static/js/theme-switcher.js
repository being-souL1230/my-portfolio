class ThemeSwitcher {
  constructor() {
    this.themeToggle = document.getElementById('theme-toggle');
    // Check if mobile device
    this.isMobile = window.innerWidth <= 768;
    // Set default theme: blue for both mobile and desktop (or saved preference)
    this.theme = this.isMobile ? 'blue' : (localStorage.getItem('theme') || 'blue');
    this.isAnimating = false;
    this.init();
  }

  init() {
    this.setTheme(this.theme);
    this.setupEventListeners();
  }

  setTheme(theme) {
    // Remove any existing theme styles
    const oldLink = document.getElementById('theme-style');
    if (oldLink) {
      oldLink.remove();
    }

    // Add the appropriate theme stylesheet
    const link = document.createElement('link');
    link.id = 'theme-style';
    link.rel = 'stylesheet';
    link.href = `/static/css/main${theme === 'blue' ? '_blue_theme' : ''}.css`;
    document.head.appendChild(link);

    // Save to localStorage only on desktop
    if (!this.isMobile) {
      localStorage.setItem('theme', theme);
    }
    
    // Update toggle button state
    if (this.themeToggle) {
      this.themeToggle.setAttribute('data-theme', theme);
      this.themeToggle.classList.toggle('blue-theme', theme === 'blue');
    }
  }

  toggleTheme() {
    // Disable theme switching on mobile
    if (this.isMobile || this.isAnimating) return;
    this.isAnimating = true;
    
    // Toggle between red and blue themes
    this.theme = this.theme === 'red' ? 'blue' : 'red';
    
    // Add animation class
    if (this.themeToggle) {
      this.themeToggle.classList.add('animating');
    }

    this.setTheme(this.theme);

    // Remove animation class after transition
    setTimeout(() => {
      if (this.themeToggle) {
        this.themeToggle.classList.remove('animating');
      }
      this.isAnimating = false;
    }, 400);
  }

  setupEventListeners() {
    if (this.themeToggle) {
      this.themeToggle.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleTheme();
      });
    } else {
      console.warn('Theme toggle button not found - theme switching disabled');
    }
  }
}

// Initialize theme switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new ThemeSwitcher();
});

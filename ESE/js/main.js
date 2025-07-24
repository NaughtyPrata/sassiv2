/**
 * Emotion State Engine™ - Main JavaScript
 * Modern, performance-optimized interactions
 */

// Utility functions
const throttle = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  
  // Mobile menu functionality
  initMobileMenu();
  
  // Smooth scrolling for navigation links
  initSmoothScroll();
  
  // Parallax effects
  initParallax();
  
  // Intersection Observer for animations
  initScrollAnimations();
  
  // Enhanced button interactions
  initButtonEffects();
  
  // Performance monitoring
  if (window.performance && window.performance.mark) {
    window.performance.mark('app-initialized');
  }
});

/**
 * Mobile Menu Toggle
 */
function initMobileMenu() {
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  
  if (!mobileMenuBtn || !mobileMenu) return;
  
  mobileMenuBtn.addEventListener('click', function() {
    const isOpen = !mobileMenu.classList.contains('hidden');
    
    if (isOpen) {
      mobileMenu.classList.add('hidden');
      mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    } else {
      mobileMenu.classList.remove('hidden');
      mobileMenuBtn.innerHTML = '<i class="fas fa-times"></i>';
    }
  });
  
  // Close mobile menu when clicking links
  const mobileLinks = mobileMenu.querySelectorAll('a');
  mobileLinks.forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.add('hidden');
      mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    });
  });
}

/**
 * Smooth Scrolling Navigation
 */
function initSmoothScroll() {
  const navLinks = document.querySelectorAll('a[href^="#"]');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        const headerOffset = 80;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

/**
 * Subtle Parallax Effects
 */
function initParallax() {
  const parallaxElements = document.querySelectorAll('.parallax-element');
  
  if (parallaxElements.length === 0) return;
  
  // Check if user prefers reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;
  
  const handleParallax = throttle(() => {
    const scrolled = window.pageYOffset;
    
    parallaxElements.forEach(element => {
      const speed = element.dataset.speed || 0.5;
      const yPos = -(scrolled * speed);
      element.style.transform = `translateY(${yPos}px)`;
    });
  }, 16); // ~60fps
  
  window.addEventListener('scroll', handleParallax, { passive: true });
}

/**
 * Scroll-triggered Animations
 */
function initScrollAnimations() {
  // Only proceed if IntersectionObserver is supported
  if (!('IntersectionObserver' in window)) return;
  
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-slide-up');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  // Observe sections and cards
  const animatedElements = document.querySelectorAll(
    'section > div, .card, .card-feature, h2, h3, .grid > div'
  );
  
  animatedElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
  
  // Custom animation for slide-up
  const style = document.createElement('style');
  style.textContent = `
    .animate-slide-up {
      opacity: 1 !important;
      transform: translateY(0) !important;
    }
  `;
  document.head.appendChild(style);
}

/**
 * Enhanced Button Interactions
 */
function initButtonEffects() {
  const buttons = document.querySelectorAll('button, .btn-primary, .btn-secondary');
  
  buttons.forEach(button => {
    // Ripple effect on click
    button.addEventListener('click', function(e) {
      if (this.querySelector('.ripple')) return;
      
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      
      ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        pointer-events: none;
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
      `;
      
      this.style.position = 'relative';
      this.appendChild(ripple);
      
      setTimeout(() => {
        if (ripple.parentNode) {
          ripple.parentNode.removeChild(ripple);
        }
      }, 600);
    });
    
    // Hover effects for primary buttons
    if (button.classList.contains('bg-primary') || 
        button.textContent.includes('Request Demo') || 
        button.textContent.includes('Download')) {
      
      button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px) scale(1.02)';
        this.style.boxShadow = '0 10px 25px rgba(220, 38, 38, 0.3)';
      });
      
      button.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
        this.style.boxShadow = 'none';
      });
    }
  });
  
  // Add ripple animation CSS
  const rippleStyle = document.createElement('style');
  rippleStyle.textContent = `
    @keyframes ripple-animation {
      from {
        transform: scale(0);
        opacity: 1;
      }
      to {
        transform: scale(2);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(rippleStyle);
}

/**
 * Navbar Background on Scroll
 */
function initNavbarScroll() {
  const navbar = document.querySelector('nav');
  if (!navbar) return;
  
  const handleScroll = throttle(() => {
    if (window.scrollY > 50) {
      navbar.classList.add('nav-scrolled');
    } else {
      navbar.classList.remove('nav-scrolled');
    }
  }, 16);
  
  window.addEventListener('scroll', handleScroll, { passive: true });
  
  // Add corresponding CSS
  const navStyle = document.createElement('style');
  navStyle.textContent = `
    .nav-scrolled {
      background-color: rgba(0, 0, 0, 0.95) !important;
      backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(220, 38, 38, 0.2);
    }
  `;
  document.head.appendChild(navStyle);
}

/**
 * Typing Effect for Hero Section
 */
function initTypingEffect() {
  const typingElement = document.querySelector('.typing-text');
  if (!typingElement) return;
  
  const texts = [
    'Persistent Emotional Intelligence',
    'Advanced Prompt Engineering',
    'Clinical Training Solutions',
    'Authentic AI Interactions'
  ];
  
  let textIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  
  function typeText() {
    const currentText = texts[textIndex];
    
    if (isDeleting) {
      typingElement.textContent = currentText.substring(0, charIndex - 1);
      charIndex--;
    } else {
      typingElement.textContent = currentText.substring(0, charIndex + 1);
      charIndex++;
    }
    
    let timeout = isDeleting ? 50 : 100;
    
    if (!isDeleting && charIndex === currentText.length) {
      timeout = 2000;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      textIndex = (textIndex + 1) % texts.length;
      timeout = 500;
    }
    
    setTimeout(typeText, timeout);
  }
  
  typeText();
}

/**
 * Enhanced Card Hover Effects
 */
function initCardEffects() {
  const cards = document.querySelectorAll('.card, .card-feature');
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-8px) scale(1.02)';
      this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.3)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
      this.style.boxShadow = 'none';
    });
  });
}

/**
 * Performance Monitoring
 */
function initPerformanceMonitoring() {
  // Monitor Core Web Vitals if supported
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          console.log(`${entry.name}: ${entry.value}`);
        }
      });
      
      observer.observe({ entryTypes: ['measure', 'navigation'] });
    } catch (e) {
      // Silently fail if not supported
    }
  }
}

/**
 * Accessibility Enhancements
 */
function initAccessibility() {
  // Skip to main content link
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.textContent = 'Skip to main content';
  skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary text-white px-4 py-2 rounded z-50';
  document.body.insertBefore(skipLink, document.body.firstChild);
  
  // Enhance focus indicators
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-navigation');
    }
  });
  
  document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
  });
  
  // Add focus styles
  const focusStyle = document.createElement('style');
  focusStyle.textContent = `
    .keyboard-navigation *:focus {
      outline: 2px solid #DC2626 !important;
      outline-offset: 2px !important;
    }
    
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
    
    .focus\\:not-sr-only:focus {
      position: static !important;
      width: auto !important;
      height: auto !important;
      padding: 0.5rem 1rem !important;
      margin: 0 !important;
      overflow: visible !important;
      clip: auto !important;
      white-space: normal !important;
    }
  `;
  document.head.appendChild(focusStyle);
}

// Initialize additional features after main load
window.addEventListener('load', function() {
  initNavbarScroll();
  initCardEffects();
  initPerformanceMonitoring();
  initAccessibility();
});

// Error handling
window.addEventListener('error', function(e) {
  console.error('JavaScript error:', e.error);
  // Optionally send to error tracking service
});

// Service worker registration (if available)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    // Uncomment when service worker is implemented
    // navigator.serviceWorker.register('/sw.js');
  });
}
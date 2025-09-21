/* MoodSync Main JavaScript - Enhanced Version */

document.addEventListener('DOMContentLoaded', function() {
    console.log('MoodSync enhanced JavaScript loaded successfully!');
    
    // Initialize all components
    initTooltips();
    initPopovers();
    initScrollAnimations();
    initEmotionSelectors();
    initRatingSystem();
    initDarkMode();
    initColorSchemeToggle();
    initInteractiveElements();
    initParticleAnimations();
    initNavigation();
    initMoodTracker();
});

// Initialize Bootstrap tooltips with enhanced settings
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            delay: { "show": 300, "hide": 100 },
            trigger: 'hover focus'
        });
    });
    
    console.log(`Initialized ${tooltipList.length} tooltips`);
}

// Initialize Bootstrap popovers with enhanced settings
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            animation: true,
            trigger: 'focus',
            html: true
        });
    });
    
    console.log(`Initialized ${popoverList.length} popovers`);
}

// Enhanced scroll animations with Intersection Observer API
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .fade-in, .slide-up');
    
    if (!animatedElements.length) return;
    
    // Use Intersection Observer for better performance
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const animationType = element.dataset.animation || 'fade-in';
                
                // Add animation class
                element.classList.add(animationType);
                
                // Add animated class after a delay for staggered effects
                const delay = parseInt(element.dataset.delay) || 0;
                
                setTimeout(() => {
                    element.classList.add('animated');
                    
                    // Dispatch custom event for additional actions
                    element.dispatchEvent(new CustomEvent('animationStart', {
                        bubbles: true,
                        detail: { element, animationType }
                    }));
                }, delay);
                
                // Stop observing after animation is triggered
                observer.unobserve(element);
            }
        });
    }, observerOptions);
    
    // Observe all animated elements
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    console.log(`Observing ${animatedElements.length} elements for scroll animations`);
}

// Enhanced emotion selection with visual feedback
function initEmotionSelectors() {
    const emotionSelectors = document.querySelectorAll('.emotion-selector');
    
    if (!emotionSelectors.length) return;
    
    emotionSelectors.forEach(selector => {
        // Add hover effects
        selector.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'scale(1.05)';
                this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
            }
        });
        
        selector.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = '';
                this.style.boxShadow = '';
            }
        });
        
        // Handle click selection
        selector.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all selectors
            emotionSelectors.forEach(s => {
                s.classList.remove('active');
                s.style.transform = '';
                s.style.boxShadow = '';
            });
            
            // Add active class to clicked selector with animation
            this.classList.add('active');
            this.style.transform = 'scale(1.1)';
            this.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.3)';
            
            // Pulse animation effect
            this.classList.add('pulse');
            setTimeout(() => this.classList.remove('pulse'), 600);
            
            // Update hidden input value
            const emotionInput = document.getElementById('selected_emotion');
            if (emotionInput) {
                emotionInput.value = this.dataset.emotion;
                
                // Visual feedback for selection
                emotionInput.classList.add('selected');
                setTimeout(() => emotionInput.classList.remove('selected'), 1000);
            }
            
            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('emotionSelected', {
                detail: { emotion: this.dataset.emotion }
            }));
            
            console.log(`Selected emotion: ${this.dataset.emotion}`);
        });
    });
    
    console.log(`Initialized ${emotionSelectors.length} emotion selectors`);
}

// Enhanced rating system with visual feedback
function initRatingSystem() {
    const ratingStars = document.querySelectorAll('.rating-star');
    
    if (!ratingStars.length) return;
    
    ratingStars.forEach(star => {
        // Add hover effects
        star.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            const stars = this.closest('.rating').querySelectorAll('.rating-star');
            
            stars.forEach(s => {
                if (parseInt(s.dataset.rating) <= rating) {
                    s.classList.add('hover');
                    s.style.transform = 'scale(1.2)';
                }
            });
        });
        
        star.addEventListener('mouseleave', function() {
            const stars = this.closest('.rating').querySelectorAll('.rating-star');
            stars.forEach(s => {
                s.classList.remove('hover');
                s.style.transform = '';
            });
        });
        
        // Handle click rating
        star.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            const suggestionId = this.closest('.rating').dataset.suggestionId;
            const stars = this.closest('.rating').querySelectorAll('.rating-star');
            
            // Update visual state with animation
            stars.forEach(s => {
                const starRating = parseInt(s.dataset.rating);
                
                if (starRating <= rating) {
                    s.classList.remove('bi-star');
                    s.classList.add('bi-star-fill');
                    
                    // Add animation
                    s.style.transform = 'scale(1.3)';
                    setTimeout(() => s.style.transform = '', 300);
                } else {
                    s.classList.remove('bi-star-fill');
                    s.classList.add('bi-star');
                }
            });
            
            // Send rating to server via fetch API
            rateSuggestion(suggestionId, rating);
        });
    });
    
    console.log(`Initialized ${ratingStars.length} rating stars`);
}

// Function to send rating to server
async function rateSuggestion(suggestionId, rating) {
    try {
        const response = await fetch('/api/suggestions/rate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({
                suggestion_id: suggestionId,
                rating: rating
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`Successfully rated suggestion ${suggestionId} with ${rating} stars`);
            
            // Show success feedback
            showNotification('Rating saved successfully!', 'success');
        } else {
            throw new Error('Server returned an error');
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
        showNotification('Error saving rating. Please try again.', 'error');
    }
}

// Enhanced dark mode toggle with system preference detection
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (!darkModeToggle) return;
    
    // Check for saved theme preference or respect OS preference
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme');
    
    // Apply theme with smooth transition
    document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDarkMode)) {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }
    
    // Handle toggle change with animation
    darkModeToggle.addEventListener('change', function() {
        // Add transition class for smooth change
        document.body.classList.add('theme-transition');
        
        if (this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            
            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('themeChanged', {
                detail: { theme: 'dark' }
            }));
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
            
            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('themeChanged', {
                detail: { theme: 'light' }
            }));
        }
        
        // Remove transition class after animation completes
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 300);
        
        console.log(`Theme changed to: ${this.checked ? 'dark' : 'light'}`);
    });
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                document.body.classList.add('dark-mode');
                darkModeToggle.checked = true;
            } else {
                document.body.classList.remove('dark-mode');
                darkModeToggle.checked = false;
            }
        }
    });
    
    console.log('Dark mode toggle initialized');
}

// Initialize color scheme toggle
function initColorSchemeToggle() {
    const colorToggle = document.getElementById('colorToggle');
    const colorOptions = document.getElementById('colorOptions');
    
    if (!colorToggle || !colorOptions) return;
    
    colorToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        colorOptions.classList.toggle('active');
    });
    
    // Change color scheme
    const colorOptionsList = document.querySelectorAll('.color-option');
    colorOptionsList.forEach(option => {
        option.addEventListener('click', function(e) {
            e.stopPropagation();
            const newColor = this.getAttribute('data-color');
            
            // Update CSS variable with transition
            document.documentElement.style.setProperty('--primary', newColor);
            
            // Save preference
            localStorage.setItem('colorScheme', newColor);
            
            // Close color options
            colorOptions.classList.remove('active');
            
            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('colorSchemeChanged', {
                detail: { color: newColor }
            }));
            
            console.log(`Color scheme changed to: ${newColor}`);
        });
    });
    
    // Close color options when clicking outside
    document.addEventListener('click', function(e) {
        if (!colorToggle.contains(e.target) && !colorOptions.contains(e.target)) {
            colorOptions.classList.remove('active');
        }
    });
    
    // Load saved color scheme
    const savedColor = localStorage.getItem('colorScheme');
    if (savedColor) {
        document.documentElement.style.setProperty('--primary', savedColor);
    }
    
    console.log('Color scheme toggle initialized');
}

// Initialize interactive elements
function initInteractiveElements() {
    // Add hover effects to all cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        btn.addEventListener('mouseup', function() {
            this.style.transform = '';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    console.log(`Enhanced ${cards.length} cards and ${buttons.length} buttons`);
}

// Initialize particle animations
function initParticleAnimations() {
    const particlesContainer = document.getElementById('particles');
    
    if (!particlesContainer) return;
    
    // Create particles if container exists
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        const size = Math.random() * 20 + 5;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        
        particle.style.animationDelay = `${Math.random() * 5}s`;
        
        particlesContainer.appendChild(particle);
    }
    
    console.log('Particle animations initialized');
}

// Initialize navigation effects
function initNavigation() {
    const navbar = document.querySelector('.navbar');
    
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.padding = '10px 0';
            navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.1)';
            navbar.style.backdropFilter = 'blur(10px)';
        } else {
            navbar.style.padding = '15px 0';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            navbar.style.backdropFilter = 'blur(5px)';
        }
    });
    
    console.log('Navigation effects initialized');
}

// Initialize mood tracker animations
function initMoodTracker() {
    const moodTracker = document.getElementById('moodTracker');
    
    if (!moodTracker) return;
    
    // Animate mood bars on page load
    const moodBars = moodTracker.querySelectorAll('.mood-bar');
    moodBars.forEach((bar, index) => {
        setTimeout(() => {
            bar.style.transition = 'height 1.5s ease';
            bar.style.height = bar.dataset.height || '50%';
        }, index * 100);
    });
    
    console.log(`Animated ${moodBars.length} mood bars`);
}

// Helper function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi ${type === 'success' ? 'bi-check-circle' : type === 'error' ? 'bi-exclamation-circle' : 'bi-info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Export functions for use in other modules
window.MoodSync = {
    showNotification,
    rateSuggestion,
    initScrollAnimations
};
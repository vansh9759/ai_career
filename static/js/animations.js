/**
 * CareerOS AI - Dynamic Animations & Scroll Reveal Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Intersection Observer for Scroll Reveals
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.12
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                
                // Trigger counter animation if element has data-counter
                if (entry.target.hasAttribute('data-counter')) {
                    animateCounter(entry.target);
                }
                
                // Also check child elements with data-counter
                entry.target.querySelectorAll('[data-counter]').forEach(el => animateCounter(el));
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Auto-attach observer to glass cards, stat cards, hero elements and elements with .animate-on-scroll
    const animatableElements = document.querySelectorAll('.glass-card, .stat-card, .glass-panel, .hero-pill, .hero-title, .hero-subtitle, .animate-on-scroll');
    
    animatableElements.forEach((el, idx) => {
        el.classList.add('animate-on-scroll');
        
        // Apply staggered animation delay within grid containers
        const gridParent = el.closest('.dashboard-grid');
        if (gridParent) {
            const childIndex = Array.from(gridParent.children).indexOf(el);
            el.style.transitionDelay = `${(childIndex % 4) * 0.12}s`;
        }

        scrollObserver.observe(el);
    });

    // 2. Smooth Number Counter Animation Function
    function animateCounter(element) {
        const targetVal = parseInt(element.getAttribute('data-counter'), 10);
        if (isNaN(targetVal) || element.getAttribute('data-counter-done') === 'true') return;
        
        element.setAttribute('data-counter-done', 'true');
        const prefix = element.getAttribute('data-prefix') || '';
        const suffix = element.getAttribute('data-suffix') || '';
        const duration = 1500; // ms
        const startTime = performance.now();

        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentVal = Math.floor(easeProgress * targetVal);

            element.innerText = `${prefix}${currentVal}${suffix}`;

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            } else {
                element.innerText = `${prefix}${targetVal}${suffix}`;
            }
        }

        requestAnimationFrame(updateNumber);
    }
});

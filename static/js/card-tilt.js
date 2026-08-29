/**
 * CareerOS AI - 3D Card Hover Tilt & Animated Counter FX
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. 3D Card Hover Tilt Effect
    const cards = document.querySelectorAll('.glass-card, .stat-card, .feature-card');
    cards.forEach(card => {
        card.style.transition = 'transform 0.25s ease, box-shadow 0.25s ease';
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -6;
            const rotateY = ((x - centerX) / centerX) * 6;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
            card.style.boxShadow = `0 15px 35px -10px rgba(16, 185, 129, 0.25), 0 0 20px rgba(59, 130, 246, 0.15)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
            card.style.boxShadow = '';
        });
    });

    // 2. Animated Number Counters on Scroll
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.getAttribute('data-counter'), 10);
                    const suffix = entry.target.getAttribute('data-suffix') || '';
                    let current = 0;
                    const step = Math.max(1, Math.ceil(target / 40));

                    const timer = setInterval(() => {
                        current += step;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        entry.target.innerText = current + suffix;
                    }, 30);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => observer.observe(counter));
    }
});

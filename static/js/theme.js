/* ==========================================================================
   CareerOS AI - Client Interaction & Theme Switcher Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark/Light Theme Switching
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const storedTheme = localStorage.getItem('careeros_theme') || 'dark';
    
    document.documentElement.setAttribute('data-theme', storedTheme);
    updateThemeIcon(storedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('careeros_theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
        }
    }

    // 2. Mobile Sidebar Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.querySelector('.app-sidebar');
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // 3. Tab Switching Helper
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            const parent = btn.closest('.tab-container');
            if (parent) {
                parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                parent.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                const targetPane = document.getElementById(targetId);
                if (targetPane) targetPane.classList.add('active');
            }
        });
    });
});

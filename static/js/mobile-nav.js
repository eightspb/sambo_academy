/**
 * Mobile Navigation
 * Handles hamburger menu and mobile overlay
 */

(function() {
    // Create mobile menu button
    function createMobileMenuButton() {
        const btn = document.createElement('button');
        btn.className = 'mobile-menu-btn';
        btn.innerHTML = '☰';
        btn.setAttribute('aria-label', 'Открыть меню');
        btn.onclick = toggleMobileMenu;
        document.body.appendChild(btn);
        return btn;
    }
    
    // Create overlay
    function createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        overlay.onclick = closeMobileMenu;
        document.body.appendChild(overlay);
        return overlay;
    }
    
    // Toggle mobile menu
    function toggleMobileMenu() {
        const nav = document.querySelector('.nav');
        const overlay = document.querySelector('.mobile-overlay');
        const btn = document.querySelector('.mobile-menu-btn');
        
        if (nav.classList.contains('mobile-open')) {
            closeMobileMenu();
        } else {
            nav.classList.add('mobile-open');
            overlay.classList.add('active');
            btn.innerHTML = '✕';
            btn.setAttribute('aria-label', 'Закрыть меню');
            document.body.style.overflow = 'hidden'; // Prevent scroll
        }
    }
    
    // Close mobile menu
    function closeMobileMenu() {
        const nav = document.querySelector('.nav');
        const overlay = document.querySelector('.mobile-overlay');
        const btn = document.querySelector('.mobile-menu-btn');
        
        nav.classList.remove('mobile-open');
        overlay.classList.remove('active');
        btn.innerHTML = '☰';
        btn.setAttribute('aria-label', 'Открыть меню');
        document.body.style.overflow = ''; // Restore scroll
    }
    
    // Close menu on link click
    function closeOnNavClick() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    closeMobileMenu();
                }
            });
        });
    }
    
    // Handle window resize
    function handleResize() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    }
    
    // Initialize
    function init() {
        // Wait for components to load
        setTimeout(() => {
            const nav = document.querySelector('.nav');
            if (nav) {
                createMobileMenuButton();
                createOverlay();
                closeOnNavClick();
                window.addEventListener('resize', handleResize);
            }
        }, 100);
    }
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Expose functions globally if needed
    window.mobileNav = {
        toggle: toggleMobileMenu,
        close: closeMobileMenu
    };
})();

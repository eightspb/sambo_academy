/**
 * Mobile Navigation
 * Handles hamburger menu and mobile overlay
 */

(function() {
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
        const btn = document.querySelector('.mobile-menu-btn .menu-icon');
        
        if (nav && nav.classList.contains('mobile-open')) {
            closeMobileMenu();
        } else if (nav) {
            nav.classList.add('mobile-open');
            if (overlay) overlay.classList.add('active');
            if (btn) btn.textContent = '✕';
            document.body.style.overflow = 'hidden'; // Prevent scroll
        }
    }
    
    // Close mobile menu
    function closeMobileMenu() {
        const nav = document.querySelector('.nav');
        const overlay = document.querySelector('.mobile-overlay');
        const btn = document.querySelector('.mobile-menu-btn .menu-icon');
        
        if (nav) nav.classList.remove('mobile-open');
        if (overlay) overlay.classList.remove('active');
        if (btn) btn.textContent = '☰';
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
    
    // Expose functions globally for header button
    window.toggleMobileMenu = toggleMobileMenu;
    window.closeMobileMenu = closeMobileMenu;
})();

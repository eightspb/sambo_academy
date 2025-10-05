/**
 * Component loader for shared UI elements
 */

const ComponentLoader = {
    /**
     * Load a component and insert it into the DOM
     */
    async loadComponent(componentName, targetId) {
        try {
            const response = await fetch(`/templates/components/${componentName}.html`);
            if (!response.ok) {
                console.error(`Failed to load component: ${componentName}`);
                return;
            }
            
            const html = await response.text();
            const target = document.getElementById(targetId);
            if (target) {
                target.innerHTML = html;
            }
        } catch (error) {
            console.error(`Error loading component ${componentName}:`, error);
        }
    },
    
    /**
     * Load all common components (header and nav)
     */
    async loadCommonComponents() {
        await Promise.all([
            this.loadComponent('header', 'app-header'),
            this.loadComponent('nav', 'app-nav')
        ]);
        
        // Highlight current page in navigation
        this.highlightCurrentPage();
    },
    
    /**
     * Highlight the current page in navigation
     */
    highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            if (linkPath === currentPath) {
                link.classList.add('active');
            }
        });
    }
};

// Auto-load components when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        ComponentLoader.loadCommonComponents();
    });
} else {
    ComponentLoader.loadCommonComponents();
}

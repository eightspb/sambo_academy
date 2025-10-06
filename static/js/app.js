// Main application JavaScript
const API_BASE_URL = '/api';

// Authentication utilities
const auth = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    
    setToken(token) {
        localStorage.setItem('access_token', token);
    },
    
    removeToken() {
        localStorage.removeItem('access_token');
    },
    
    isAuthenticated() {
        return !!this.getToken();
    },
    
    async checkAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    },
    
    async logout() {
        this.removeToken();
        window.location.href = '/login';
    }
};

// API utilities
const api = {
    async request(endpoint, options = {}) {
        const token = auth.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            
            if (response.status === 401) {
                auth.removeToken();
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }
            
            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

// UI utilities
const ui = {
    showLoading() {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loading-spinner';
        document.body.appendChild(spinner);
    },
    
    hideLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },
    
    showError(message) {
        alert(`Ошибка: ${message}`);
    },
    
    showSuccess(message) {
        alert(message);
    },
    
    confirm(message) {
        return window.confirm(message);
    },
    
    // Безопасная установка имени пользователя
    setUserName(fullName) {
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = fullName;
        }
    }
};

// Modal utilities
const modal = {
    open(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    },
    
    close(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    },
    
    closeAll() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }
};

// Date utilities
const dateUtils = {
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU');
    },
    
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU');
    },
    
    toISODate(dateString) {
        const date = new Date(dateString);
        return date.toISOString().split('T')[0];
    }
};

// Initialize service worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

// Navigation
function setActiveNav() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setActiveNav();
    
    // Close modals on outside click
    document.querySelectorAll('.modal').forEach(modalEl => {
        modalEl.addEventListener('click', (e) => {
            if (e.target === modalEl) {
                modal.close(modalEl.id);
            }
        });
    });
    
    // Close modals on close button click
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            modal.closeAll();
        });
    });
});

// Export for use in other scripts
window.auth = auth;
window.api = api;
window.ui = ui;
window.modal = modal;
window.dateUtils = dateUtils;

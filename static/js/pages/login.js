/**
 * Login Page Script
 */

// Redirect if already authenticated
if (auth.isAuthenticated()) {
    window.location.href = '/';
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('errorMessage');
    
    errorDiv.classList.add('hidden');
    
    try {
        ui.showLoading();
        
        // Create form data for OAuth2
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        ui.hideLoading();
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка входа');
        }
        
        const data = await response.json();
        auth.setToken(data.access_token);
        
        window.location.href = '/';
    } catch (error) {
        ui.hideLoading();
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});

/**
 * Settings Page Script
 */
async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        document.getElementById('userName').textContent = user.full_name;
        
        // Check if user is admin
        if (!user.is_admin) {
            ui.showError('Доступ к настройкам только для администраторов');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }
        
        // Load current prices
        await loadPrices();
    } catch (error) {
        ui.showError(error.message);
    }
}

async function loadPrices() {
    try {
        const prices = await api.get('/settings/prices');
        document.getElementById('subscription8SeniorPrice').value = prices.subscription_8_senior_price;
        document.getElementById('subscription12SeniorPrice').value = prices.subscription_12_senior_price;
        document.getElementById('subscription8JuniorPrice').value = prices.subscription_8_junior_price;
        document.getElementById('subscription12JuniorPrice').value = prices.subscription_12_junior_price;
    } catch (error) {
        console.error('Error loading prices:', error);
        ui.showError('Не удалось загрузить настройки цен');
    }
}

document.getElementById('pricesForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        subscription_8_senior_price: parseInt(formData.get('subscription_8_senior_price')),
        subscription_12_senior_price: parseInt(formData.get('subscription_12_senior_price')),
        subscription_8_junior_price: parseInt(formData.get('subscription_8_junior_price')),
        subscription_12_junior_price: parseInt(formData.get('subscription_12_junior_price'))
    };
    
    try {
        ui.showLoading();
        await api.put('/settings/prices/update', data);
        ui.hideLoading();
        
        ui.showSuccess('Настройки сохранены');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

loadData();

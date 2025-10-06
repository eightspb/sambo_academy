/**
 * Payments Page Script
 */
let students = [];
let subscriptions = [];
let payments = [];
let groups = [];
let subscriptionPrices = null; // Will be loaded from API

async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        document.getElementById('userName').textContent = user.full_name;
        
        // Load groups first
        groups = await api.get('/groups');
        
        // Then load students
        students = await api.get('/students?is_active=true');
        populateStudentSelects();
        
        // Load subscription prices from settings
        await loadSubscriptionPrices();
        
        // Set default month to current
        const now = new Date();
        document.getElementById('monthFilter').value = 
            `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        
        await loadPayments();
    } catch (error) {
        ui.showError(error.message);
    }
}

async function loadSubscriptionPrices() {
    try {
        subscriptionPrices = await api.get('/settings/prices');
        // Set initial price when form loads
        updatePriceByType();
    } catch (error) {
        console.error('Error loading subscription prices:', error);
        ui.showError('Не удалось загрузить цены абонементов');
    }
}

function updatePriceByType() {
    const typeSelect = document.getElementById('subscriptionType');
    const studentSelect = document.getElementById('studentSelect');
    const priceInput = document.getElementById('subscriptionPrice');
    const priceHint = document.getElementById('priceHint');
    
    if (!typeSelect || !priceInput || !studentSelect || !subscriptionPrices) return;
    
    const selectedType = typeSelect.value;
    const selectedStudentId = studentSelect.value;
    
    // Find selected student and their group
    const student = students.find(s => s.id === selectedStudentId);
    if (!student) return;
    
    const group = groups.find(g => g.id === student.group_id);
    if (!group) return;
    
    // Determine age group (senior or junior)
    const ageGroup = group.age_group; // 'senior' or 'junior'
    let price = 0;
    let hint = '';
    
    if (selectedType === '8_sessions') {
        if (ageGroup === 'senior') {
            price = subscriptionPrices.subscription_8_senior_price;
            hint = 'Цена для старших - 8 занятий';
        } else {
            price = subscriptionPrices.subscription_8_junior_price;
            hint = 'Цена для младших - 8 занятий';
        }
    } else if (selectedType === '12_sessions') {
        if (ageGroup === 'senior') {
            price = subscriptionPrices.subscription_12_senior_price;
            hint = 'Цена для старших - 12 занятий';
        } else {
            price = subscriptionPrices.subscription_12_junior_price;
            hint = 'Цена для младших - 12 занятий';
        }
    }
    
    priceInput.value = price;
    priceHint.textContent = hint;
}

function populateStudentSelects() {
    const options = students.map(s => 
        `<option value="${s.id}">${s.full_name}</option>`
    ).join('');
    
    document.getElementById('studentSelect').innerHTML = options;
    document.getElementById('studentPaymentSelect').innerHTML = options;
}

// Add event listeners for subscription type and student change
document.addEventListener('DOMContentLoaded', () => {
    const typeSelect = document.getElementById('subscriptionType');
    const studentSelect = document.getElementById('studentSelect');
    
    if (typeSelect) {
        typeSelect.addEventListener('change', updatePriceByType);
    }
    
    if (studentSelect) {
        studentSelect.addEventListener('change', updatePriceByType);
    }
});

async function loadPayments() {
    const monthValue = document.getElementById('monthFilter').value;
    if (!monthValue) return;
    
    const [year, month] = monthValue.split('-');
    
    try {
        payments = await api.get(`/payments/month/${year}/${month}`);
        renderPayments();
    } catch (error) {
        ui.showError(error.message);
    }
}

function renderPayments() {
    const container = document.getElementById('paymentsList');
    
    if (payments.length === 0) {
        container.innerHTML = '<div class="card"><p class="text-secondary">Платежей за этот месяц не найдено</p></div>';
        return;
    }
    
    const totalAmount = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
    
    container.innerHTML = `
        <div class="stat-card mb-2">
            <div class="stat-value">${totalAmount.toFixed(2)} ₽</div>
            <div class="stat-label">Общая сумма за месяц</div>
        </div>
        
        <!-- Desktop: Table view -->
        <div class="card" style="overflow-x: auto;">
            <table class="table">
                <thead>
                    <tr>
                        <th>Ученик</th>
                        <th>Сумма</th>
                        <th>Дата платежа</th>
                        <th>Абонемент</th>
                        <th>Тип платежа</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    ${payments.map(payment => `
                        <tr>
                            <td>${payment.student_name}</td>
                            <td>${parseFloat(payment.amount).toFixed(2)} ₽</td>
                            <td>${dateUtils.formatDate(payment.payment_date)}</td>
                            <td>${payment.subscription_type === '8_sessions' ? '8 занятий' : payment.subscription_type === '12_sessions' ? '12 занятий' : '-'}</td>
                            <td>${payment.payment_type === 'full' ? 'Полная' : payment.payment_type === 'partial' ? 'Частичная' : 'Скидка'}</td>
                            <td>
                                <span class="badge ${
                                    payment.status === 'paid' ? 'badge-success' :
                                    payment.status === 'pending' ? 'badge-warning' :
                                    'badge-danger'
                                }">
                                    ${
                                        payment.status === 'paid' ? 'Оплачено' :
                                        payment.status === 'pending' ? 'Ожидается' :
                                        'Просрочено'
                                    }
                                </span>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <!-- Mobile: Card view -->
        <div class="mobile-cards">
            ${payments.map(payment => `
                <div class="mobile-card">
                    <div class="mobile-card-header">
                        ${payment.student_name}
                        <span style="font-size: 1.1rem; color: var(--primary-color);">${parseFloat(payment.amount).toFixed(2)} ₽</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Дата:</span>
                        <span class="mobile-card-value">${dateUtils.formatDate(payment.payment_date)}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Абонемент:</span>
                        <span class="mobile-card-value">${payment.subscription_type === '8_sessions' ? '8 занятий' : payment.subscription_type === '12_sessions' ? '12 занятий' : '-'}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Тип:</span>
                        <span class="mobile-card-value">${payment.payment_type === 'full' ? 'Полная' : payment.payment_type === 'partial' ? 'Частичная' : 'Скидка'}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Статус:</span>
                        <span class="mobile-card-value">
                            <span class="badge ${
                                payment.status === 'paid' ? 'badge-success' :
                                payment.status === 'pending' ? 'badge-warning' :
                                'badge-danger'
                            }">
                                ${
                                    payment.status === 'paid' ? 'Оплачено' :
                                    payment.status === 'pending' ? 'Ожидается' :
                                    'Просрочено'
                                }
                            </span>
                        </span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function openCreateSubscriptionModal() {
    modal.open('createSubscriptionModal');
}

function openCreatePaymentModal() {
    modal.open('createPaymentModal');
}

document.getElementById('createSubscriptionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        student_id: formData.get('student_id'),
        subscription_type: formData.get('subscription_type'),
        price: parseFloat(formData.get('price')),
        start_date: formData.get('start_date'),
        expiry_date: formData.get('expiry_date')
    };
    
    try {
        ui.showLoading();
        await api.post('/subscriptions', data);
        ui.hideLoading();
        
        modal.close('createSubscriptionModal');
        e.target.reset();
        ui.showSuccess('Абонемент создан');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

document.getElementById('createPaymentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const monthValue = formData.get('payment_month');
    const paymentMonth = monthValue + '-01'; // First day of month
    
    const data = {
        student_id: formData.get('student_id'),
        amount: parseFloat(formData.get('amount')),
        payment_date: formData.get('payment_date'),
        payment_month: paymentMonth,
        payment_type: formData.get('payment_type'),
        status: formData.get('status')
    };
    
    try {
        ui.showLoading();
        await api.post('/payments', data);
        ui.hideLoading();
        
        modal.close('createPaymentModal');
        e.target.reset();
        loadPayments();
        ui.showSuccess('Платеж добавлен');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

loadData();

/**
 * Payments New Page Script
 */
let groups = [];
let students = [];
let subscriptionPrices = null;
let paymentsData = [];
let currentMonth = '';
let currentGroupId = '';
let currentPaymentId = null;
let currentSubscriptionId = null;

async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        ui.setUserName(user.full_name);
        
        // Load groups
        groups = await api.get('/groups');
        populateGroupFilter();
        
        // Load subscription prices
        subscriptionPrices = await api.get('/settings/prices');
        
        // Set default month to current
        const now = new Date();
        document.getElementById('monthFilter').value = 
            `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        
    } catch (error) {
        ui.showError(error.message);
    }
}

let selectedGroupId = null;

function populateGroupFilter() {
    const groupChips = document.getElementById('groupChips');
    
    groups.forEach(group => {
        const chip = document.createElement('div');
        chip.className = 'chip';
        chip.textContent = group.name;
        chip.dataset.groupId = group.id;
        chip.onclick = () => selectGroup(group.id);
        groupChips.appendChild(chip);
    });
}

function selectGroup(groupId) {
    selectedGroupId = groupId;
    
    // Update chips UI
    document.querySelectorAll('#groupChips .chip').forEach(chip => {
        chip.classList.remove('active');
    });
    
    const activeChip = document.querySelector(`#groupChips .chip[data-group-id="${groupId}"]`);
    if (activeChip) {
        activeChip.classList.add('active');
    }
    
    onFilterChange();
}

function onFilterChange() {
    const monthFilter = document.getElementById('monthFilter').value;
    if (selectedGroupId && monthFilter) {
        loadPaymentsList();
    }
}

async function loadPaymentsList() {
    const month = document.getElementById('monthFilter').value;
    const groupId = selectedGroupId;
    
    if (!month || !groupId) {
        ui.showError('Выберите месяц и группу');
        return;
    }
    
    currentMonth = month;
    currentGroupId = groupId;
    
    try {
        ui.showLoading();
        
        // Load students of the group
        students = await api.get(`/students?group_id=${groupId}&is_active=true`);
        
        // Load payments for this month
        const [year, monthNum] = month.split('-');
        try {
            paymentsData = await api.get(`/payments/month/${year}/${monthNum}`);
        } catch (e) {
            paymentsData = [];
        }
        
        renderPaymentsTable();
        updateSummary();
        
        document.getElementById('noDataMessage').style.display = 'none';
        document.getElementById('summary').style.display = 'block';
        document.getElementById('paymentsListContainer').style.display = 'block';
        
        ui.hideLoading();
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

function renderPaymentsTable() {
    const tbody = document.getElementById('paymentsTableBody');
    const mobileContainer = document.getElementById('paymentsMobileCards');
    const group = groups.find(g => g.id === currentGroupId);
    
    if (students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-secondary">В группе нет учеников</td></tr>';
        if (mobileContainer) mobileContainer.innerHTML = '<div class="card"><p class="text-secondary">В группе нет учеников</p></div>';
        return;
    }
    
    // Desktop: Table view
    tbody.innerHTML = students.map((student, index) => {
        const payment = findStudentPayment(student.id);
        const isPaid = payment !== null;
        const rowClass = isPaid ? 'paid-row' : '';
        
        // Calculate standard price
        const ageGroup = group.age_group;
        let standardPrice8 = ageGroup === 'senior' 
            ? subscriptionPrices.subscription_8_senior_price 
            : subscriptionPrices.subscription_8_junior_price;
        let standardPrice12 = ageGroup === 'senior' 
            ? subscriptionPrices.subscription_12_senior_price 
            : subscriptionPrices.subscription_12_junior_price;
        
        // Use student's active subscription type, not payment's subscription type
        let subscriptionType = student.subscription_type || '8_sessions';
        let standardPrice = subscriptionType === '12_sessions' ? standardPrice12 : standardPrice8;
        let actualAmount = payment ? payment.amount : 0;
        
        let statusBadge = '';
        let amountInfo = '';
        
        if (isPaid) {
            if (actualAmount > standardPrice) {
                amountInfo = `<span class="overpaid-indicator">+${actualAmount - standardPrice}₽</span>`;
                statusBadge = '<span class="badge badge-success">Оплачено</span>';
            } else if (actualAmount < standardPrice) {
                amountInfo = `<span class="underpaid-indicator">-${standardPrice - actualAmount}₽</span>`;
                statusBadge = '<span class="badge badge-warning">Частично</span>';
            } else {
                statusBadge = '<span class="badge badge-success">Оплачено</span>';
            }
        } else {
            statusBadge = '<span class="badge badge-danger">Не оплачено</span>';
        }
        
        return `
            <tr class="${rowClass}">
                <td style="text-align: center;">${index + 1}</td>
                <td>${student.full_name}</td>
                <td>${subscriptionType === '12_sessions' ? '12 занятий' : '8 занятий'}</td>
                <td>${standardPrice}₽</td>
                <td>${isPaid ? actualAmount + '₽' : '-'} ${amountInfo}</td>
                <td>${statusBadge}</td>
                <td>
                    <div class="flex gap-1">
                        ${isPaid 
                            ? `<button class="btn btn-sm btn-outline" onclick='viewPaymentDetails("${payment.id}")'>Детали</button>`
                            : `
                                <button class="btn btn-sm btn-success" onclick='quickStandardPayment("${student.id}", "${student.full_name.replace(/"/g, '&quot;')}")'>Стандартная оплата</button>
                                <button class="btn btn-sm btn-outline" onclick='openPaymentModal("${student.id}", "${student.full_name.replace(/"/g, '&quot;')}")'>Оплатить</button>
                            `
                        }
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    // Mobile: Card view
    if (mobileContainer) {
        mobileContainer.innerHTML = students.map((student, index) => {
            const payment = findStudentPayment(student.id);
            const isPaid = payment !== null;
            
            // Calculate standard price
            const ageGroup = group.age_group;
            let standardPrice8 = ageGroup === 'senior' 
                ? subscriptionPrices.subscription_8_senior_price 
                : subscriptionPrices.subscription_8_junior_price;
            let standardPrice12 = ageGroup === 'senior' 
                ? subscriptionPrices.subscription_12_senior_price 
                : subscriptionPrices.subscription_12_junior_price;
            
            let subscriptionType = student.subscription_type || '8_sessions';
            let standardPrice = subscriptionType === '12_sessions' ? standardPrice12 : standardPrice8;
            let actualAmount = payment ? payment.amount : 0;
            
            let statusBadge = '';
            let amountInfo = '';
            
            if (isPaid) {
                if (actualAmount > standardPrice) {
                    amountInfo = `<span class="overpaid-indicator">+${actualAmount - standardPrice}₽</span>`;
                    statusBadge = '<span class="badge badge-success">Оплачено</span>';
                } else if (actualAmount < standardPrice) {
                    amountInfo = `<span class="underpaid-indicator">-${standardPrice - actualAmount}₽</span>`;
                    statusBadge = '<span class="badge badge-warning">Частично</span>';
                } else {
                    statusBadge = '<span class="badge badge-success">Оплачено</span>';
                }
            } else {
                statusBadge = '<span class="badge badge-danger">Не оплачено</span>';
            }
            
            return `
                <div class="mobile-card ${isPaid ? 'paid-row' : ''}">
                    <div class="mobile-card-header">
                        ${index + 1}. ${student.full_name}
                        ${statusBadge}
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Абонемент:</span>
                        <span class="mobile-card-value">${subscriptionType === '12_sessions' ? '12 занятий' : '8 занятий'}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Стандарт:</span>
                        <span class="mobile-card-value">${standardPrice}₽</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Оплачено:</span>
                        <span class="mobile-card-value">${isPaid ? actualAmount + '₽' : '-'} ${amountInfo}</span>
                    </div>
                    <div class="mobile-card-actions">
                        ${isPaid 
                            ? `<button class="btn btn-sm btn-outline" onclick='viewPaymentDetails("${payment.id}")'>Детали</button>`
                            : `
                                <button class="btn btn-sm btn-success" onclick='quickStandardPayment("${student.id}", "${student.full_name.replace(/"/g, '&quot;')}")' style="flex: 1;">Стандартная</button>
                                <button class="btn btn-sm btn-outline" onclick='openPaymentModal("${student.id}", "${student.full_name.replace(/"/g, '&quot;')}")'>Оплатить</button>
                            `
                        }
                    </div>
                </div>
            `;
        }).join('');
    }
}

function findStudentPayment(studentId) {
    return paymentsData.find(p => p.student_id === studentId) || null;
}

function updateSummary() {
    const total = students.length;
    const paid = students.filter(s => findStudentPayment(s.id) !== null).length;
    const unpaid = total - paid;
    
    document.getElementById('totalStudents').textContent = total;
    document.getElementById('paidStudents').textContent = paid;
    document.getElementById('unpaidStudents').textContent = unpaid;
}

async function quickStandardPayment(studentId, studentName) {
    if (!ui.confirm(`Зарегистрировать стандартную оплату для ${studentName}?`)) {
        return;
    }
    
    const group = groups.find(g => g.id === currentGroupId);
    const ageGroup = group.age_group;
    
    // Calculate standard price for 8 sessions
    const standardPrice = ageGroup === 'senior' 
        ? subscriptionPrices.subscription_8_senior_price 
        : subscriptionPrices.subscription_8_junior_price;
    
    const subscriptionType = '8_sessions';
    const [year, month] = currentMonth.split('-');
    
    try {
        ui.showLoading();
        
        // Check if student has active subscription
        let subscriptionId = null;
        try {
            const subscriptions = await api.get(`/subscriptions/student/${studentId}`);
            const activeSubscription = subscriptions.find(s => s.is_active === true);
            if (activeSubscription) {
                subscriptionId = activeSubscription.id;
            }
        } catch (e) {
            console.log('No active subscription found, will create new one');
        }
        
        // Create subscription only if doesn't exist
        if (!subscriptionId) {
            const subscriptionData = {
                student_id: studentId,
                subscription_type: subscriptionType,
                price: standardPrice,
                start_date: `${year}-${month}-01`
            };
            const newSubscription = await api.post('/subscriptions', subscriptionData);
            subscriptionId = newSubscription.id;
        }
        
        // Create payment
        const paymentData = {
            student_id: studentId,
            subscription_id: subscriptionId,
            amount: standardPrice,
            payment_type: 'full',
            payment_date: new Date().toISOString().split('T')[0],
            payment_month: `${year}-${month}-01`,
            status: 'paid',
            notes: 'Стандартная оплата'
        };
        
        await api.post('/payments', paymentData);
        
        ui.hideLoading();
        ui.showSuccess(`Оплата зарегистрирована: ${standardPrice}₽`);
        
        // Reload payments list
        await loadPaymentsList();
        
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

function openPaymentModal(studentId, studentName) {
    const student = students.find(s => s.id === studentId);
    const group = groups.find(g => g.id === currentGroupId);
    
    document.getElementById('paymentStudentId').value = studentId;
    document.getElementById('paymentStudentName').value = studentName;
    document.getElementById('paymentMonth').value = currentMonth;
    
    // Calculate standard price
    const ageGroup = group.age_group;
    const standardPrice8 = ageGroup === 'senior' 
        ? subscriptionPrices.subscription_8_senior_price 
        : subscriptionPrices.subscription_8_junior_price;
    
    document.getElementById('paymentStandardPrice').value = standardPrice8;
    document.getElementById('paymentActualAmount').value = standardPrice8;
    document.getElementById('paymentSubscriptionType').value = '8_sessions';
    document.getElementById('paymentNotes').value = '';
    
    modal.open('paymentModal');
}

// Update standard price when subscription type changes
document.addEventListener('DOMContentLoaded', () => {
    const typeSelect = document.getElementById('paymentSubscriptionType');
    if (typeSelect) {
        typeSelect.addEventListener('change', () => {
            const studentId = document.getElementById('paymentStudentId').value;
            const student = students.find(s => s.id === studentId);
            const group = groups.find(g => g.id === currentGroupId);
            
            if (!group || !subscriptionPrices) return;
            
            const ageGroup = group.age_group;
            const type = typeSelect.value;
            
            let standardPrice;
            if (type === '12_sessions') {
                standardPrice = ageGroup === 'senior' 
                    ? subscriptionPrices.subscription_12_senior_price 
                    : subscriptionPrices.subscription_12_junior_price;
            } else {
                standardPrice = ageGroup === 'senior' 
                    ? subscriptionPrices.subscription_8_senior_price 
                    : subscriptionPrices.subscription_8_junior_price;
            }
            
            document.getElementById('paymentStandardPrice').value = standardPrice;
            document.getElementById('paymentActualAmount').value = standardPrice;
        });
    }
});

document.getElementById('paymentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const studentId = document.getElementById('paymentStudentId').value;
    const subscriptionType = document.getElementById('paymentSubscriptionType').value;
    const amount = parseFloat(document.getElementById('paymentActualAmount').value);
    const notes = document.getElementById('paymentNotes').value;
    const [year, month] = currentMonth.split('-');
    
    try {
        ui.showLoading();
        
        // Check if student has active subscription
        let subscriptionId = null;
        try {
            const subscriptions = await api.get(`/subscriptions/student/${studentId}`);
            const activeSubscription = subscriptions.find(s => s.is_active === true);
            if (activeSubscription) {
                subscriptionId = activeSubscription.id;
            }
        } catch (e) {
            console.log('No active subscription found, will create new one');
        }
        
        // Create subscription only if doesn't exist
        if (!subscriptionId) {
            const subscriptionData = {
                student_id: studentId,
                subscription_type: subscriptionType,
                price: amount,
                start_date: `${year}-${month}-01`
            };
            const newSubscription = await api.post('/subscriptions', subscriptionData);
            subscriptionId = newSubscription.id;
        }
        
        // Create payment
        const paymentData = {
            student_id: studentId,
            subscription_id: subscriptionId,
            amount: amount,
            payment_type: 'full',
            payment_date: new Date().toISOString().split('T')[0],
            payment_month: `${year}-${month}-01`,
            status: 'paid',
            notes: notes || 'Нестандартная оплата'
        };
        
        await api.post('/payments', paymentData);
        
        ui.hideLoading();
        modal.close('paymentModal');
        
        ui.showSuccess('Оплата зарегистрирована');
        
        // Reload payments list
        await loadPaymentsList();
        
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

async function viewPaymentDetails(paymentId) {
    try {
        ui.showLoading();
        
        // Find payment in current data
        const payment = paymentsData.find(p => p.id === paymentId);
        if (!payment) {
            ui.showError('Платеж не найден');
            return;
        }
        
        // Find student
        const student = students.find(s => s.id === payment.student_id);
        const group = groups.find(g => g.id === currentGroupId);
        
        // Get subscription details
        let subscription = null;
        if (payment.subscription_id) {
            try {
                const subscriptions = await api.get(`/subscriptions/student/${payment.student_id}`);
                subscription = subscriptions.find(s => s.id === payment.subscription_id);
            } catch (e) {
                console.error('Error loading subscription:', e);
            }
        }
        
        // Calculate standard price
        const ageGroup = group.age_group;
        let standardPrice;
        if (subscription) {
            const type = subscription.subscription_type;
            if (type === '12_sessions') {
                standardPrice = ageGroup === 'senior' 
                    ? subscriptionPrices.subscription_12_senior_price 
                    : subscriptionPrices.subscription_12_junior_price;
            } else {
                standardPrice = ageGroup === 'senior' 
                    ? subscriptionPrices.subscription_8_senior_price 
                    : subscriptionPrices.subscription_8_junior_price;
            }
        } else {
            standardPrice = payment.amount;
        }
        
        // Fill modal
        document.getElementById('detailsStudentName').value = student.full_name;
        document.getElementById('detailsSubscriptionType').value = 
            subscription ? (subscription.subscription_type === '12_sessions' ? '12 занятий' : '8 занятий') : '-';
        document.getElementById('detailsStandardPrice').value = standardPrice;
        document.getElementById('detailsActualAmount').value = payment.amount;
        document.getElementById('detailsPaymentDate').value = payment.payment_date;
        document.getElementById('detailsStatus').value = 
            payment.status === 'paid' ? 'Оплачено' : 
            payment.status === 'pending' ? 'Ожидается' : 'Просрочено';
        document.getElementById('detailsNotes').value = payment.notes || '';
        
        currentPaymentId = paymentId;
        currentSubscriptionId = payment.subscription_id;
        
        ui.hideLoading();
        modal.open('paymentDetailsModal');
        
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

async function updatePayment() {
    if (!currentPaymentId) return;
    
    const newAmount = parseFloat(document.getElementById('detailsActualAmount').value);
    const notes = document.getElementById('detailsNotes').value;
    
    if (!ui.confirm('Сохранить изменения в оплате?')) {
        return;
    }
    
    try {
        ui.showLoading();
        
        // Update payment
        await api.put(`/payments/${currentPaymentId}`, {
            amount: newAmount,
            notes: notes
        });
        
        // Update subscription price if exists
        if (currentSubscriptionId) {
            await api.put(`/subscriptions/${currentSubscriptionId}`, {
                price: newAmount
            });
        }
        
        ui.hideLoading();
        modal.close('paymentDetailsModal');
        
        ui.showSuccess('Оплата обновлена');
        await loadPaymentsList();
        
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

async function cancelPayment() {
    if (!currentPaymentId) return;
    
    if (!ui.confirm('Вы уверены, что хотите отменить эту оплату? Это действие удалит оплату и абонемент.')) {
        return;
    }
    
    try {
        ui.showLoading();
        
        // Delete subscription first (if exists)
        if (currentSubscriptionId) {
            try {
                await api.delete(`/subscriptions/${currentSubscriptionId}`);
            } catch (e) {
                console.error('Error deleting subscription:', e);
            }
        }
        
        // Delete payment
        await api.delete(`/payments/${currentPaymentId}`);
        
        ui.hideLoading();
        modal.close('paymentDetailsModal');
        
        ui.showSuccess('Оплата отменена');
        await loadPaymentsList();
        
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}


// Wait for all scripts to load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadData);
} else {
    loadData();
}

/**
 * Settings Page Script
 */
async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        ui.setUserName(user.full_name);
        
        // Check if user is admin
        if (!user.is_admin) {
            ui.showError('Доступ к настройкам только для администраторов');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }
        
        // Load all data
        await Promise.all([
            loadPrices(),
            loadInactiveStudents(),
            loadInactiveGroups()
        ]);
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


async function loadInactiveStudents() {
    const container = document.getElementById('inactiveStudentsList');
    
    try {
        const students = await api.get('/students?is_active=false');
        
        if (students.length === 0) {
            container.innerHTML = '<p class="text-secondary">✅ Нет неактивных учеников</p>';
            return;
        }
        
        container.innerHTML = `
            <div style="overflow-x: auto;">
                <table class="table">
                    <thead>
                        <tr>
                            <th>ФИО</th>
                            <th>Группа</th>
                            <th>Телефон</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${students.map(student => `
                            <tr>
                                <td><strong>${student.full_name}</strong></td>
                                <td>${student.group_name || '-'}</td>
                                <td>${student.phone || '-'}</td>
                                <td>
                                    <button 
                                        class="btn btn-sm btn-success" 
                                        onclick="activateStudent('${student.id}', '${student.full_name.replace(/'/g, "\\'")}')"
                                    >
                                        ✓ Активировать
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <!-- Mobile view -->
            <div class="mobile-cards">
                ${students.map(student => `
                    <div class="mobile-card">
                        <div class="mobile-card-header">
                            ${student.full_name}
                            <span class="badge badge-danger">Неактивен</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Группа:</span>
                            <span class="mobile-card-value">${student.group_name || '-'}</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Телефон:</span>
                            <span class="mobile-card-value">${student.phone || '-'}</span>
                        </div>
                        <div class="mobile-card-actions">
                            <button 
                                class="btn btn-sm btn-success" 
                                onclick="activateStudent('${student.id}', '${student.full_name.replace(/'/g, "\\'")}')"
                                style="width: 100%;"
                            >
                                ✓ Активировать
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p class="text-danger">Ошибка загрузки: ${error.message}</p>`;
    }
}

async function loadInactiveGroups() {
    const container = document.getElementById('inactiveGroupsList');
    
    try {
        const allGroups = await api.get('/groups');
        const inactiveGroups = allGroups.filter(g => !g.is_active);
        
        if (inactiveGroups.length === 0) {
            container.innerHTML = '<p class="text-secondary">✅ Нет неактивных групп</p>';
            return;
        }
        
        container.innerHTML = `
            <div style="overflow-x: auto;">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Расписание</th>
                            <th>Возраст</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${inactiveGroups.map(group => `
                            <tr>
                                <td><strong>${group.name}</strong></td>
                                <td>${formatSchedule(group.schedule_type)}</td>
                                <td>${group.age_group === 'senior' ? 'Старшие' : 'Младшие'}</td>
                                <td>
                                    <button 
                                        class="btn btn-sm btn-success" 
                                        onclick="activateGroup('${group.id}', '${group.name.replace(/'/g, "\\'")}')"
                                    >
                                        ✓ Активировать
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <!-- Mobile view -->
            <div class="mobile-cards">
                ${inactiveGroups.map(group => `
                    <div class="mobile-card">
                        <div class="mobile-card-header">
                            ${group.name}
                            <span class="badge badge-danger">Неактивна</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Расписание:</span>
                            <span class="mobile-card-value">${formatSchedule(group.schedule_type)}</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Возраст:</span>
                            <span class="mobile-card-value">${group.age_group === 'senior' ? 'Старшие' : 'Младшие'}</span>
                        </div>
                        <div class="mobile-card-actions">
                            <button 
                                class="btn btn-sm btn-success" 
                                onclick="activateGroup('${group.id}', '${group.name.replace(/'/g, "\\'")}')"
                                style="width: 100%;"
                            >
                                ✓ Активировать
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p class="text-danger">Ошибка загрузки: ${error.message}</p>`;
    }
}

function formatSchedule(scheduleType) {
    const schedules = {
        'mon_wed_fri': 'ПН-СР-ПТ',
        'tue_thu': 'ВТ-ЧТ'
    };
    return schedules[scheduleType] || scheduleType;
}

async function activateStudent(studentId, studentName) {
    if (!ui.confirm(`Активировать ученика ${studentName}?`)) {
        return;
    }
    
    try {
        ui.showLoading();
        await api.put(`/students/${studentId}`, { is_active: true });
        ui.hideLoading();
        
        ui.showSuccess(`${studentName} активирован`);
        await loadInactiveStudents();
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

async function activateGroup(groupId, groupName) {
    if (!ui.confirm(`Активировать группу ${groupName}?`)) {
        return;
    }
    
    try {
        ui.showLoading();
        await api.put(`/groups/${groupId}`, { is_active: true });
        ui.hideLoading();
        
        ui.showSuccess(`Группа "${groupName}" активирована`);
        await loadInactiveGroups();
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

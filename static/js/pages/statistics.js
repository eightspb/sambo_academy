/**
 * Statistics Page Script
 */

const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

let currentTab = 'attendance';

async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = user.full_name;
        }
        
        // Populate years
        const currentYear = new Date().getFullYear();
        const yearSelect = document.getElementById('yearFilter');
        for (let year = currentYear; year >= currentYear - 5; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        }
        
        // Populate months
        const currentMonth = new Date().getMonth() + 1;
        const monthSelect = document.getElementById('monthFilter');
        for (let month = 1; month <= 12; month++) {
            const option = document.createElement('option');
            option.value = month;
            option.textContent = monthNames[month - 1];
            if (month === currentMonth) option.selected = true;
            monthSelect.appendChild(option);
        }
        
        switchTab('attendance');
    } catch (error) {
        ui.showError(error.message);
    }
}

function switchTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    document.getElementById('tabAttendance').classList.remove('btn-primary');
    document.getElementById('tabPayments').classList.remove('btn-primary');
    document.getElementById('tabUnpaid').classList.remove('btn-primary');
    
    document.getElementById('tab' + tab.charAt(0).toUpperCase() + tab.slice(1)).classList.add('btn-primary');
    
    // Hide all content
    document.getElementById('attendanceContent').style.display = 'none';
    document.getElementById('paymentsContent').style.display = 'none';
    document.getElementById('unpaidContent').style.display = 'none';
    
    // Show/hide month filter based on tab
    if (tab === 'payments') {
        document.getElementById('monthFilterContainer').style.display = 'none';
    } else {
        document.getElementById('monthFilterContainer').style.display = 'block';
    }
    
    // Show current content
    document.getElementById(tab + 'Content').style.display = 'block';
    
    loadCurrentTabData();
}

async function loadCurrentTabData() {
    if (currentTab === 'attendance') {
        await loadAttendanceStats();
    } else if (currentTab === 'payments') {
        await loadPaymentStats();
    } else if (currentTab === 'unpaid') {
        await loadUnpaidStudents();
    }
}

async function loadAttendanceStats() {
    const year = document.getElementById('yearFilter').value;
    const month = document.getElementById('monthFilter').value;
    
    try {
        const stats = await api.get(`/attendance/statistics/summary?year=${year}&month=${month}`);
        renderAttendanceStats(stats);
    } catch (error) {
        ui.showError(error.message);
    }
}

async function loadPaymentStats() {
    const year = document.getElementById('yearFilter').value;
    
    try {
        const stats = await api.get(`/payments/statistics/summary?year=${year}`);
        renderPaymentStats(stats, year);
    } catch (error) {
        ui.showError(error.message);
    }
}

async function loadUnpaidStudents() {
    const year = document.getElementById('yearFilter').value;
    const month = document.getElementById('monthFilter').value;
    
    console.log('Loading unpaid students for:', year, month);
    
    try {
        ui.showLoading();
        const data = await api.get(`/payments/unpaid-students?year=${year}&month=${month}`);
        console.log('Unpaid students data:', data);
        ui.hideLoading();
        renderUnpaidStudents(data);
    } catch (error) {
        ui.hideLoading();
        console.error('Error loading unpaid students:', error);
        ui.showError(error.message);
    }
}

function renderAttendanceStats(stats) {
    const container = document.getElementById('attendanceContent');
    const overall = stats.overall;
    
    container.innerHTML = `
        <!-- Overall Stats -->
        <div class="grid grid-4 mb-2">
            <div class="stat-card">
                <div class="stat-value">${overall.total_sessions}</div>
                <div class="stat-label">Всего отметок</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #10b981, #059669);">
                <div class="stat-value">${overall.present}</div>
                <div class="stat-label">Присутствовали</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                <div class="stat-value">${overall.absent}</div>
                <div class="stat-label">Отсутствовали</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                <div class="stat-value">${overall.attendance_rate}%</div>
                <div class="stat-label">Процент посещаемости</div>
            </div>
        </div>
        
        <!-- Desktop: Groups Stats Table -->
        <div class="card" style="overflow-x: auto;">
            <h2 class="card-title mb-2">Статистика по группам</h2>
            ${stats.groups.length === 0 ? '<p class="text-secondary">Нет данных за выбранный месяц</p>' : `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Группа</th>
                            <th>Всего</th>
                            <th>Присутствовали</th>
                            <th>Отсутствовали</th>
                            <th>Перенос</th>
                            <th>% Посещаемости</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${stats.groups.map(g => `
                            <tr>
                                <td><strong>${g.group_name}</strong></td>
                                <td>${g.total_sessions}</td>
                                <td><span class="badge badge-success">${g.present}</span></td>
                                <td><span class="badge badge-danger">${g.absent}</span></td>
                                <td><span class="badge badge-warning">${g.transferred}</span></td>
                                <td><strong>${g.attendance_rate}%</strong></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `}
        </div>
        
        <!-- Mobile: Groups Stats Cards -->
        ${stats.groups.length > 0 ? `
        <div class="mobile-cards">
            <h2 class="card-title mb-2" style="padding: 0 1rem;">Статистика по группам</h2>
            ${stats.groups.map(g => `
                <div class="mobile-card">
                    <div class="mobile-card-header">
                        ${g.group_name}
                        <span style="font-size: 1.2rem; color: var(--primary-color);">${g.attendance_rate}%</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Всего отметок:</span>
                        <span class="mobile-card-value">${g.total_sessions}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Присутствовали:</span>
                        <span class="mobile-card-value"><span class="badge badge-success">${g.present}</span></span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Отсутствовали:</span>
                        <span class="mobile-card-value"><span class="badge badge-danger">${g.absent}</span></span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Перенос:</span>
                        <span class="mobile-card-value"><span class="badge badge-warning">${g.transferred}</span></span>
                    </div>
                </div>
            `).join('')}
        </div>
        ` : ''}
    `;
}

function renderPaymentStats(stats, year) {
    const container = document.getElementById('paymentsContent');
    
    if (stats.length === 0) {
        container.innerHTML = '<div class="card"><p class="text-secondary">Нет данных за выбранный год</p></div>';
        return;
    }
    
    const yearTotal = stats.reduce((sum, s) => sum + parseFloat(s.total_amount), 0);
    const yearPayments = stats.reduce((sum, s) => sum + s.payment_count, 0);
    
    container.innerHTML = `
        <div class="grid grid-3 mb-2">
            <div class="stat-card">
                <div class="stat-value">${yearTotal.toFixed(2)} ₽</div>
                <div class="stat-label">Общая сумма за ${year} год</div>
            </div>
            
            <div class="stat-card" style="background: linear-gradient(135deg, #10b981, #059669);">
                <div class="stat-value">${yearPayments}</div>
                <div class="stat-label">Всего платежей</div>
            </div>
            
            <div class="stat-card" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                <div class="stat-value">${(yearTotal / 12).toFixed(2)} ₽</div>
                <div class="stat-label">Средняя сумма в месяц</div>
            </div>
        </div>
        
        <!-- Desktop: Table view -->
        <div class="card" style="overflow-x: auto;">
            <h2 class="card-title mb-2">Помесячная статистика</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Месяц</th>
                        <th>Сумма</th>
                        <th>Кол-во платежей</th>
                        <th>Оплачено</th>
                        <th>Ожидается</th>
                        <th>Просрочено</th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.map(stat => `
                        <tr>
                            <td>${monthNames[stat.month - 1]}</td>
                            <td><strong>${parseFloat(stat.total_amount).toFixed(2)} ₽</strong></td>
                            <td>${stat.payment_count}</td>
                            <td><span class="badge badge-success">${stat.paid_count}</span></td>
                            <td><span class="badge badge-warning">${stat.pending_count}</span></td>
                            <td><span class="badge badge-danger">${stat.overdue_count}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
                <tfoot>
                    <tr style="font-weight: bold; background-color: var(--bg-color);">
                        <td>ИТОГО</td>
                        <td>${yearTotal.toFixed(2)} ₽</td>
                        <td>${yearPayments}</td>
                        <td>${stats.reduce((sum, s) => sum + s.paid_count, 0)}</td>
                        <td>${stats.reduce((sum, s) => sum + s.pending_count, 0)}</td>
                        <td>${stats.reduce((sum, s) => sum + s.overdue_count, 0)}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        
        <!-- Mobile: Card view -->
        <div class="mobile-cards">
            <h2 class="card-title mb-2" style="padding: 0 1rem;">Помесячная статистика</h2>
            ${stats.map(stat => `
                <div class="mobile-card">
                    <div class="mobile-card-header">
                        ${monthNames[stat.month - 1]}
                        <span style="font-size: 1.1rem; color: var(--primary-color);">${parseFloat(stat.total_amount).toFixed(2)} ₽</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Платежей:</span>
                        <span class="mobile-card-value">${stat.payment_count}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Оплачено:</span>
                        <span class="mobile-card-value"><span class="badge badge-success">${stat.paid_count}</span></span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Ожидается:</span>
                        <span class="mobile-card-value"><span class="badge badge-warning">${stat.pending_count}</span></span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Просрочено:</span>
                        <span class="mobile-card-value"><span class="badge badge-danger">${stat.overdue_count}</span></span>
                    </div>
                </div>
            `).join('')}
            
            <!-- Mobile Total Card -->
            <div class="mobile-card" style="border: 2px solid var(--primary-color); background: rgba(37, 99, 235, 0.05);">
                <div class="mobile-card-header" style="font-size: 1.1rem;">
                    ИТОГО
                    <span style="font-size: 1.2rem; color: var(--primary-color);">${yearTotal.toFixed(2)} ₽</span>
                </div>
                <div class="mobile-card-row">
                    <span class="mobile-card-label">Всего платежей:</span>
                    <span class="mobile-card-value"><strong>${yearPayments}</strong></span>
                </div>
                <div class="mobile-card-row">
                    <span class="mobile-card-label">Оплачено:</span>
                    <span class="mobile-card-value"><span class="badge badge-success">${stats.reduce((sum, s) => sum + s.paid_count, 0)}</span></span>
                </div>
                <div class="mobile-card-row">
                    <span class="mobile-card-label">Ожидается:</span>
                    <span class="mobile-card-value"><span class="badge badge-warning">${stats.reduce((sum, s) => sum + s.pending_count, 0)}</span></span>
                </div>
                <div class="mobile-card-row">
                    <span class="mobile-card-label">Просрочено:</span>
                    <span class="mobile-card-value"><span class="badge badge-danger">${stats.reduce((sum, s) => sum + s.overdue_count, 0)}</span></span>
                </div>
            </div>
        </div>
    `;
}

function renderUnpaidStudents(data) {
    console.log('Rendering unpaid students:', data);
    const container = document.getElementById('unpaidContent');
    const monthName = monthNames[data.month - 1];
    
    console.log('Container:', container, 'Month:', monthName);
    
    container.innerHTML = `
        <!-- Summary -->
        <div class="grid grid-3 mb-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                <div class="stat-value">${data.total_unpaid}</div>
                <div class="stat-label">Не оплатили за ${monthName}</div>
            </div>
        </div>
        
        <!-- Desktop: Students List Table -->
        <div class="card">
            <h2 class="card-title mb-2">Список неоплативших учеников</h2>
            ${data.students.length === 0 ? 
                '<p class="text-success">✅ Все ученики оплатили абонемент за выбранный месяц!</p>' 
                : `
                <table class="table">
                    <thead>
                        <tr>
                            <th>№</th>
                            <th>ФИО</th>
                            <th>Группа</th>
                            <th>Телефон</th>
                            <th>Email</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.students.map((student, index) => `
                            <tr>
                                <td>${index + 1}</td>
                                <td><strong>${student.full_name}</strong></td>
                                <td>${student.group_name}</td>
                                <td>${student.phone || '-'}</td>
                                <td>${student.email || '-'}</td>
                                <td>
                                    ${student.phone ? `<a href="tel:${student.phone}" class="btn btn-sm btn-outline">📞 Позвонить</a>` : ''}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `}
        </div>
        
        <!-- Mobile: Students List Cards -->
        ${data.students.length > 0 ? `
        <div class="mobile-cards">
            <h2 class="card-title mb-2" style="padding: 0 1rem;">Список неоплативших учеников</h2>
            ${data.students.map((student, index) => `
                <div class="mobile-card" style="border-left: 3px solid #dc2626;">
                    <div class="mobile-card-header">
                        ${index + 1}. ${student.full_name}
                        <span class="badge badge-danger">Не оплатил</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Группа:</span>
                        <span class="mobile-card-value">${student.group_name}</span>
                    </div>
                    ${student.phone ? `
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Телефон:</span>
                        <span class="mobile-card-value"><a href="tel:${student.phone}">${student.phone}</a></span>
                    </div>
                    ` : ''}
                    ${student.email ? `
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Email:</span>
                        <span class="mobile-card-value">${student.email}</span>
                    </div>
                    ` : ''}
                    ${student.phone ? `
                    <div class="mobile-card-actions">
                        <a href="tel:${student.phone}" class="btn btn-sm btn-outline">📞 Позвонить</a>
                    </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
        ` : ''}
    `;
}

loadData();

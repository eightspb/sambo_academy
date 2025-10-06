/**
 * Students Page Script
 */

let students = [];
let groups = [];
let selectedGroupId = '';

async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        ui.setUserName(user.full_name);
        
        groups = await api.get('/groups');
        populateGroupFilters();
    } catch (error) {
        ui.showError(error.message);
    }
}

function populateGroupFilters() {
    const groupChips = document.getElementById('groupChips');
    const groupSelect = document.getElementById('groupSelect');
    const editGroupSelect = document.getElementById('editGroupId');
    const editAdditionalGroupsSelect = document.getElementById('editAdditionalGroups');
    
    const groupOptions = groups.map(g => 
        `<option value="${g.id}">${g.name}</option>`
    ).join('');
    
    groupSelect.innerHTML = groupOptions;
    if (editGroupSelect) {
        editGroupSelect.innerHTML = groupOptions;
    }
    if (editAdditionalGroupsSelect) {
        editAdditionalGroupsSelect.innerHTML = groupOptions;
    }
    
    // Create chips for groups
    const allChip = document.createElement('div');
    allChip.className = 'chip active';
    allChip.textContent = 'Все группы';
    allChip.onclick = () => selectGroup('');
    groupChips.appendChild(allChip);
    
    groups.forEach(group => {
        const chip = document.createElement('div');
        chip.className = 'chip';
        chip.textContent = group.name;
        chip.dataset.groupId = group.id;
        chip.onclick = () => selectGroup(group.id);
        groupChips.appendChild(chip);
    });
    
    // Check URL parameters for filters
    const urlParams = new URLSearchParams(window.location.search);
    const groupIdFromUrl = urlParams.get('group');
    
    if (groupIdFromUrl) {
        selectGroup(groupIdFromUrl);
    } else {
        // Загружаем всех учеников при первом открытии
        loadStudents();
    }
}

function selectGroup(groupId) {
    selectedGroupId = groupId;
    
    // Update chips UI
    document.querySelectorAll('#groupChips .chip').forEach(chip => {
        chip.classList.remove('active');
    });
    
    if (groupId) {
        const activeChip = document.querySelector(`#groupChips .chip[data-group-id="${groupId}"]`);
        if (activeChip) activeChip.classList.add('active');
    } else {
        document.querySelector('#groupChips .chip').classList.add('active');
    }
    
    loadStudents();
}

async function loadStudents() {
    const groupId = selectedGroupId;
    const isActive = 'true'; // Всегда показываем только активных
    
    // Update URL with current filters
    const params = new URLSearchParams();
    if (groupId) params.set('group', groupId);
    
    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.history.replaceState({}, '', newUrl);
    
    // Build API URL
    let apiUrl = '/students?';
    if (groupId) apiUrl += `group_id=${groupId}&`;
    apiUrl += `is_active=${isActive}`;
    
    try {
        students = await api.get(apiUrl);
        renderStudents();
    } catch (error) {
        ui.showError(error.message);
    }
}

function renderStudents() {
    const container = document.getElementById('studentsList');
    
    // Update page title if filtered by group
    const groupId = selectedGroupId;
    const pageTitle = document.querySelector('h1');
    if (groupId && groups.length > 0) {
        const selectedGroup = groups.find(g => g.id === groupId);
        if (selectedGroup) {
            pageTitle.textContent = `Ученики - ${selectedGroup.name}`;
        }
    } else {
        pageTitle.textContent = 'Ученики';
    }
    
    if (students.length === 0) {
        container.innerHTML = '<div class="card"><p class="text-secondary">Учеников не найдено</p></div>';
        return;
    }
    
    // Desktop: Table view
    const tableView = `
        <div class="card" style="overflow-x: auto;">
            <table class="table">
                <thead>
                    <tr>
                        <th style="width: 50px;">№</th>
                        <th>ФИО</th>
                        <th>Дата рождения</th>
                        <th>Телефон</th>
                        <th>Группа</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${students.map((student, index) => {
                        const group = groups.find(g => g.id === student.group_id);
                        
                        // Get additional groups
                        let additionalGroupsHtml = '';
                        if (student.additional_group_ids && student.additional_group_ids.length > 0) {
                            const additionalGroupNames = student.additional_group_ids
                                .map(id => {
                                    const g = groups.find(gr => gr.id === id);
                                    return g ? g.name : null;
                                })
                                .filter(name => name);
                            
                            if (additionalGroupNames.length > 0) {
                                additionalGroupsHtml = `<br><small style="color: #ff6b6b; font-weight: 500;">
                                    🎁 Бонус: ${additionalGroupNames.join(', ')}
                                </small>`;
                            }
                        }
                        
                        return `
                            <tr>
                                <td style="text-align: center; font-weight: 500;">${index + 1}</td>
                                <td>${student.full_name}</td>
                                <td>${dateUtils.formatDate(student.birth_date)}</td>
                                <td>${student.phone}</td>
                                <td>${group ? group.name : '-'}${additionalGroupsHtml}</td>
                                <td>
                                    <span class="badge ${student.is_active ? 'badge-success' : 'badge-danger'}">
                                        ${student.is_active ? 'Активен' : 'Неактивен'}
                                    </span>
                                </td>
                                <td>
                                    <div class="flex gap-1">
                                        <button class="btn btn-primary btn-sm" onclick="openEditStudentModal('${student.id}')">
                                            Редактировать
                                        </button>
                                        <button class="btn btn-danger btn-sm" onclick="deleteStudent('${student.id}')">
                                            Удалить
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    // Mobile: Card view
    const mobileView = `
        <div class="mobile-cards">
            ${students.map((student, index) => {
                const group = groups.find(g => g.id === student.group_id);
                
                // Get additional groups
                let additionalGroupsText = '';
                if (student.additional_group_ids && student.additional_group_ids.length > 0) {
                    const additionalGroupNames = student.additional_group_ids
                        .map(id => {
                            const g = groups.find(gr => gr.id === id);
                            return g ? g.name : null;
                        })
                        .filter(name => name);
                    
                    if (additionalGroupNames.length > 0) {
                        additionalGroupsText = `<br><small style="color: #ff6b6b; font-weight: 500;">
                            🎁 Бонус: ${additionalGroupNames.join(', ')}
                        </small>`;
                    }
                }
                
                return `
                    <div class="mobile-card">
                        <div class="mobile-card-header">
                            ${index + 1}. ${student.full_name}
                            <span class="badge ${student.is_active ? 'badge-success' : 'badge-danger'}" style="margin-left: 0.5rem; font-size: 0.75rem;">
                                ${student.is_active ? 'Активен' : 'Неактивен'}
                            </span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Дата рождения:</span>
                            <span class="mobile-card-value">${dateUtils.formatDate(student.birth_date)}</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Телефон:</span>
                            <span class="mobile-card-value">${student.phone}</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Группа:</span>
                            <span class="mobile-card-value">${group ? group.name : '-'}${additionalGroupsText}</span>
                        </div>
                        <div class="mobile-card-actions">
                            <button class="btn btn-primary btn-sm" onclick="openEditStudentModal('${student.id}')">
                                Редактировать
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="deleteStudent('${student.id}')">
                                Удалить
                            </button>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    // Render both views (CSS will show/hide based on screen size)
    container.innerHTML = tableView + mobileView;
}

function openCreateStudentModal() {
    modal.open('createStudentModal');
}

function openEditStudentModal(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) {
        ui.showError('Ученик не найден');
        return;
    }
    
    // Fill form fields
    document.getElementById('editStudentId').value = student.id;
    document.getElementById('editFullName').value = student.full_name;
    document.getElementById('editBirthDate').value = student.birth_date;
    document.getElementById('editPhone').value = student.phone;
    document.getElementById('editEmail').value = student.email || '';
    document.getElementById('editGroupId').value = student.group_id;
    document.getElementById('editSubscriptionType').value = student.subscription_type || '8_sessions';
    document.getElementById('editIsActive').value = student.is_active.toString();
    document.getElementById('editNotes').value = student.notes || '';
    
    // Disable primary group in additional groups list
    updateAdditionalGroupsList();
    
    // Set additional groups (deselect all first, then select the ones student has)
    const additionalGroupsSelect = document.getElementById('editAdditionalGroups');
    Array.from(additionalGroupsSelect.options).forEach(option => option.selected = false);
    
    if (student.additional_group_ids && student.additional_group_ids.length > 0) {
        student.additional_group_ids.forEach(groupId => {
            const option = Array.from(additionalGroupsSelect.options).find(opt => opt.value === groupId);
            if (option && !option.disabled) option.selected = true;
        });
    }
    
    modal.open('editStudentModal');
}

// Update additional groups list when primary group changes
function updateAdditionalGroupsList() {
    const primaryGroupId = document.getElementById('editGroupId').value;
    const additionalGroupsSelect = document.getElementById('editAdditionalGroups');
    
    Array.from(additionalGroupsSelect.options).forEach(option => {
        if (option.value === primaryGroupId) {
            option.disabled = true;
            option.selected = false;
            option.textContent = option.textContent.replace(' (основная группа)', '') + ' (основная группа)';
        } else {
            option.disabled = false;
            option.textContent = option.textContent.replace(' (основная группа)', '');
        }
    });
}

// Clear all additional groups selection
function clearAdditionalGroups() {
    const additionalGroupsSelect = document.getElementById('editAdditionalGroups');
    Array.from(additionalGroupsSelect.options).forEach(option => {
        option.selected = false;
    });
}

// Listen for primary group changes
document.addEventListener('DOMContentLoaded', () => {
    const editGroupSelect = document.getElementById('editGroupId');
    if (editGroupSelect) {
        editGroupSelect.addEventListener('change', updateAdditionalGroupsList);
    }
});

document.getElementById('createStudentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        full_name: formData.get('full_name'),
        birth_date: formData.get('birth_date'),
        phone: formData.get('phone'),
        email: formData.get('email') || null,
        group_id: formData.get('group_id'),
        notes: formData.get('notes') || null
    };
    
    try {
        ui.showLoading();
        await api.post('/students', data);
        ui.hideLoading();
        
        modal.close('createStudentModal');
        e.target.reset();
        loadStudents();
        ui.showSuccess('Ученик добавлен');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

document.getElementById('editStudentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const studentId = document.getElementById('editStudentId').value;
    
    // Get selected additional groups
    const additionalGroupsSelect = document.getElementById('editAdditionalGroups');
    const additionalGroupIds = Array.from(additionalGroupsSelect.selectedOptions)
        .map(option => option.value)
        .filter(id => id); // Remove empty values
    
    const data = {
        full_name: formData.get('full_name'),
        birth_date: formData.get('birth_date'),
        phone: formData.get('phone'),
        email: formData.get('email') || null,
        group_id: formData.get('group_id'),
        additional_group_ids: additionalGroupIds,
        is_active: formData.get('is_active') === 'true',
        notes: formData.get('notes') || null
    };
    
    try {
        ui.showLoading();
        await api.put(`/students/${studentId}`, data);
        ui.hideLoading();
        
        modal.close('editStudentModal');
        loadStudents();
        ui.showSuccess('Данные ученика обновлены');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

async function deleteStudent(studentId) {
    if (!ui.confirm('Вы уверены, что хотите удалить этого ученика?')) {
        return;
    }
    
    try {
        ui.showLoading();
        await api.delete(`/students/${studentId}`);
        ui.hideLoading();
        
        loadStudents();
        ui.showSuccess('Ученик удален');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

// Initialize page
loadData();

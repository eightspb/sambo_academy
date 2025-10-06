/**
 * Groups Page Script
 */

let groups = [];

async function loadGroups() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        document.getElementById('userName').textContent = user.full_name;
        
        groups = await api.get('/groups');
        renderGroups();
    } catch (error) {
        ui.showError(error.message);
    }
}

function renderGroups() {
    const container = document.getElementById('groupsList');
    
    // Фильтруем только активные группы
    const activeGroups = groups.filter(g => g.is_active);
    
    if (activeGroups.length === 0) {
        container.innerHTML = '<div class="card"><p class="text-secondary">У вас пока нет активных групп</p></div>';
        return;
    }
    
    container.innerHTML = `
        <div class="grid grid-2">
            ${activeGroups.map(group => `
                <div class="card" style="margin: 0;">
                    <h3 class="mb-1">${group.name}</h3>
                    <p class="text-secondary mb-1">
                        ${group.age_group === 'senior' ? '👨 Старшие' : '👶 Младшие'} • 
                        ${group.schedule_type === 'mon_wed_fri' ? '📅 ПН-СР-ПТ' : '📅 ВТ-ЧТ'} • 
                        ${group.skill_level === 'experienced' ? '⭐ Опытные' : '🌱 Новички'}
                    </p>
                    <p class="mb-1">Учеников: ${group.student_count || 0}</p>
                    <div class="flex gap-1" style="flex-wrap: wrap;">
                        <a href="/attendance?group=${group.id}" class="btn btn-primary btn-sm">
                            Посещаемость
                        </a>
                        <a href="/students?group=${group.id}" class="btn btn-outline btn-sm">
                            Ученики
                        </a>
                        <button class="btn btn-secondary btn-sm" onclick="openEditGroupModal('${group.id}')">
                            Редактировать
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function openCreateGroupModal() {
    modal.open('createGroupModal');
}

function openEditGroupModal(groupId) {
    const group = groups.find(g => g.id === groupId);
    if (!group) {
        ui.showError('Группа не найдена');
        return;
    }
    
    // Fill form fields
    document.getElementById('editGroupId').value = group.id;
    document.getElementById('editGroupName').value = group.name;
    document.getElementById('editAgeGroup').value = group.age_group;
    document.getElementById('editScheduleType').value = group.schedule_type;
    document.getElementById('editSkillLevel').value = group.skill_level;
    document.getElementById('editDefaultSubscriptionType').value = group.default_subscription_type || '';
    document.getElementById('editIsActive').value = group.is_active.toString();
    
    modal.open('editGroupModal');
}

document.getElementById('createGroupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        age_group: formData.get('age_group'),
        schedule_type: formData.get('schedule_type'),
        skill_level: formData.get('skill_level'),
        schedule: {}
    };
    
    const subscriptionType = formData.get('default_subscription_type');
    // Всегда включаем поле, чтобы оно попало в update_data
    data.default_subscription_type = subscriptionType || null;
    
    try {
        ui.showLoading();
        await api.post('/groups', data);
        ui.hideLoading();
        
        modal.close('createGroupModal');
        e.target.reset();
        loadGroups();
        ui.showSuccess('Группа создана');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

document.getElementById('editGroupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const groupId = document.getElementById('editGroupId').value;
    
    const data = {
        name: document.getElementById('editGroupName').value,
        age_group: document.getElementById('editAgeGroup').value,
        schedule_type: document.getElementById('editScheduleType').value,
        skill_level: document.getElementById('editSkillLevel').value,
        is_active: document.getElementById('editIsActive').value === 'true',
        schedule: {}
    };
    
    const subscriptionType = document.getElementById('editDefaultSubscriptionType').value;
    if (subscriptionType) {
        data.default_subscription_type = subscriptionType;
    }
    
    console.log('Updating group with data:', data);
    
    try {
        ui.showLoading();
        await api.put(`/groups/${groupId}`, data);
        ui.hideLoading();
        
        modal.close('editGroupModal');
        loadGroups();
        ui.showSuccess('Группа обновлена');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

async function deleteGroup(groupId) {
    if (!ui.confirm('Вы уверены, что хотите удалить эту группу?')) {
        return;
    }
    
    try {
        ui.showLoading();
        await api.delete(`/groups/${groupId}`);
        ui.hideLoading();
        
        loadGroups();
        ui.showSuccess('Группа удалена');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

// Initialize page
loadGroups();

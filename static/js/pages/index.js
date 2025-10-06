/**
 * Dashboard/Index Page Script
 */

async function loadDashboard() {
    await auth.checkAuth();
    
    try {
        // Load user info
        const user = await api.get('/auth/me');
        document.getElementById('userName').textContent = user.full_name;
        
        // Load groups
        const groups = await api.get('/groups');
        document.getElementById('totalGroups').textContent = groups.length;
        
        // Load students
        const students = await api.get('/students');
        document.getElementById('totalStudents').textContent = students.length;
        document.getElementById('activeStudents').textContent = 
            students.filter(s => s.is_active).length;
        
        // Display groups
        const groupsList = document.getElementById('groupsList');
        if (groups.length === 0) {
            groupsList.innerHTML = '<p class="text-secondary">У вас пока нет групп</p>';
        } else {
            groupsList.innerHTML = `
                <div class="grid grid-2">
                    ${groups.map(group => `
                        <div class="card" style="margin: 0;">
                            <h3>${group.name}</h3>
                            <p class="text-secondary">
                                ${group.age_group === 'senior' ? '👨 Старшие' : '👶 Младшие'} • 
                                ${group.schedule_type === 'mon_wed_fri' ? '📅 ПН-СР-ПТ' : '📅 ВТ-ЧТ'} • 
                                ${group.skill_level === 'experienced' ? '⭐ Опытные' : '🌱 Новички'}
                            </p>
                            <p>Учеников: ${group.student_count || 0}</p>
                            <a href="/attendance?group=${group.id}" class="btn btn-primary btn-sm mt-1">
                                Отметить посещаемость
                            </a>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        ui.showError(error.message);
    }
}

// Initialize page
loadDashboard();

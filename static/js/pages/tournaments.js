/**
 * Tournaments Page Script
 */
let tournaments = [];
let students = [];
let currentTournamentResults = {};

async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        document.getElementById('userName').textContent = user.full_name;
        
        students = await api.get('/students?is_active=true');
        populateStudentSelect();
        
        await loadTournaments();
    } catch (error) {
        ui.showError(error.message);
    }
}

function populateStudentSelect() {
    const select = document.getElementById('studentSelect');
    select.innerHTML = students.map(s => 
        `<option value="${s.id}">${s.full_name}</option>`
    ).join('');
}

async function loadTournaments() {
    try {
        tournaments = await api.get('/tournaments');
        renderTournaments();
    } catch (error) {
        ui.showError(error.message);
    }
}

function renderTournaments() {
    const container = document.getElementById('tournamentsList');
    
    if (tournaments.length === 0) {
        container.innerHTML = '<div class="card"><p class="text-secondary">Турниров пока нет</p></div>';
        return;
    }
    
    container.innerHTML = tournaments.map(tournament => `
        <div class="card">
            <div class="card-header">
                <div>
                    <h2 class="card-title">${tournament.name}</h2>
                    <p class="text-secondary">
                        📍 ${tournament.location} • 📅 ${dateUtils.formatDate(tournament.tournament_date)}
                    </p>
                </div>
                <div class="flex gap-1">
                    <button class="btn btn-primary btn-sm" onclick="openAddParticipantModal('${tournament.id}')">
                        + Участник
                    </button>
                    <button class="btn btn-outline btn-sm" onclick="openEditTournamentModal('${tournament.id}')">
                        ✏️ Редактировать
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteTournament('${tournament.id}')">
                        🗑️ Удалить
                    </button>
                </div>
            </div>
            ${tournament.description ? `<p>${tournament.description}</p>` : ''}
            <div id="results_${tournament.id}">
                <button class="btn btn-outline btn-sm mt-1" onclick="loadTournamentResults('${tournament.id}')">
                    Показать результаты
                </button>
            </div>
        </div>
    `).join('');
}

async function loadTournamentResults(tournamentId) {
    try {
        const results = await api.get(`/tournaments/${tournamentId}/results`);
        const container = document.getElementById(`results_${tournamentId}`);
        
        // Store results for editing
        currentTournamentResults[tournamentId] = results;
        if (results.length === 0) {
            container.innerHTML = '<p class="text-secondary mt-1">Результатов пока нет</p>';
            return;
        }
        
        // Desktop: Table view
        const tableView = `
            <table class="table mt-1">
                <thead>
                    <tr>
                        <th>Место</th>
                        <th>Ученик</th>
                        <th>Схваток</th>
                        <th>Побед</th>
                        <th>Поражений</th>
                        <th>Весовая категория</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map((result, index) => `
                        <tr>
                            <td><strong>${result.place || '-'}</strong></td>
                            <td>${result.student_name}</td>
                            <td>${result.total_fights}</td>
                            <td><span class="badge badge-success">${result.wins}</span></td>
                            <td><span class="badge badge-danger">${result.losses}</span></td>
                            <td>${result.weight_category || '-'}</td>
                            <td>
                                <div class="flex gap-1">
                                    <button class="btn btn-sm btn-outline" onclick="openEditParticipantModal('${tournamentId}', '${result.id}', ${index})">
                                        Редактировать
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteParticipant('${tournamentId}', '${result.id}')">
                                        Удалить
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        // Mobile: Card view
        const mobileView = `
            <div class="mobile-cards mt-1">
                ${results.map((result, index) => {
                    const medal = result.place === 1 ? '🥇' : result.place === 2 ? '🥈' : result.place === 3 ? '🥉' : '';
                    return `
                        <div class="mobile-card">
                            <div class="mobile-card-header">
                                ${medal} ${result.student_name}
                                ${result.place ? `<span style="font-size: 1.2rem; font-weight: bold;">${result.place} место</span>` : ''}
                            </div>
                            <div class="mobile-card-row">
                                <span class="mobile-card-label">Схваток:</span>
                                <span class="mobile-card-value">${result.total_fights}</span>
                            </div>
                            <div class="mobile-card-row">
                                <span class="mobile-card-label">Побед:</span>
                                <span class="mobile-card-value"><span class="badge badge-success">${result.wins}</span></span>
                            </div>
                            <div class="mobile-card-row">
                                <span class="mobile-card-label">Поражений:</span>
                                <span class="mobile-card-value"><span class="badge badge-danger">${result.losses}</span></span>
                            </div>
                            ${result.weight_category ? `
                            <div class="mobile-card-row">
                                <span class="mobile-card-label">Вес. категория:</span>
                                <span class="mobile-card-value">${result.weight_category}</span>
                            </div>
                            ` : ''}
                            <div class="mobile-card-actions">
                                <button class="btn btn-sm btn-outline" onclick="openEditParticipantModal('${tournamentId}', '${result.id}', ${index})">
                                    Редактировать
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteParticipant('${tournamentId}', '${result.id}')">
                                    Удалить
                                </button>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        
        container.innerHTML = tableView + mobileView;
    } catch (error) {
        ui.showError(error.message);
    }
}

function openCreateTournamentModal() {
    modal.open('createTournamentModal');
}

async function openAddParticipantModal(tournamentId) {
    document.getElementById('selectedTournamentId').value = tournamentId;
    
    // Get already added participants
    try {
        const results = await api.get(`/tournaments/${tournamentId}/results`);
        const addedStudentIds = new Set(results.map(r => r.student_id));
        
        // Filter out already added students
        const select = document.getElementById('studentSelect');
        select.innerHTML = students
            .filter(s => !addedStudentIds.has(s.id))
            .map(s => `<option value="${s.id}">${s.full_name}</option>`)
            .join('');
        
        if (select.options.length === 0) {
            select.innerHTML = '<option value="">Все ученики уже добавлены</option>';
            ui.showError('Все активные ученики уже участвуют в этом турнире');
            return;
        }
    } catch (error) {
        console.error('Error loading participants:', error);
        // If error, show all students
        populateStudentSelect();
    }
    
    modal.open('addParticipantModal');
}

document.getElementById('createTournamentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        tournament_date: formData.get('tournament_date'),
        location: formData.get('location'),
        description: formData.get('description') || null
    };
    
    try {
        ui.showLoading();
        await api.post('/tournaments', data);
        ui.hideLoading();
        
        modal.close('createTournamentModal');
        e.target.reset();
        loadTournaments();
        ui.showSuccess('Турнир создан');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

document.getElementById('addParticipantForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const tournamentId = document.getElementById('selectedTournamentId').value;
    
    const data = {
        student_id: formData.get('student_id'),
        place: formData.get('place') ? parseInt(formData.get('place')) : null,
        total_fights: parseInt(formData.get('total_fights')),
        wins: parseInt(formData.get('wins')),
        losses: parseInt(formData.get('losses')),
        weight_category: formData.get('weight_category') || null,
        notes: formData.get('notes') || null
    };
    
    try {
        ui.showLoading();
        await api.post(`/tournaments/${tournamentId}/participants`, data);
        ui.hideLoading();
        
        modal.close('addParticipantModal');
        e.target.reset();
        loadTournamentResults(tournamentId);
        ui.showSuccess('Участник добавлен');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

function openEditParticipantModal(tournamentId, participationId, resultIndex) {
    const result = currentTournamentResults[tournamentId][resultIndex];
    
    document.getElementById('editTournamentId').value = tournamentId;
    document.getElementById('editParticipationId').value = participationId;
    document.getElementById('editStudentName').value = result.student_name;
    document.getElementById('editPlace').value = result.place || '';
    document.getElementById('editTotalFights').value = result.total_fights;
    document.getElementById('editWins').value = result.wins;
    document.getElementById('editLosses').value = result.losses;
    document.getElementById('editWeightCategory').value = result.weight_category || '';
    document.getElementById('editNotes').value = result.notes || '';
    
    modal.open('editParticipantModal');
}

document.getElementById('editParticipantForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const tournamentId = document.getElementById('editTournamentId').value;
    const participationId = document.getElementById('editParticipationId').value;
    
    const formData = new FormData(e.target);
    const data = {
        place: formData.get('place') ? parseInt(formData.get('place')) : null,
        total_fights: parseInt(formData.get('total_fights')),
        wins: parseInt(formData.get('wins')),
        losses: parseInt(formData.get('losses')),
        weight_category: formData.get('weight_category') || null,
        notes: formData.get('notes') || null
    };
    
    try {
        ui.showLoading();
        await api.put(`/tournaments/${tournamentId}/participants/${participationId}`, data);
        ui.hideLoading();
        
        modal.close('editParticipantModal');
        loadTournamentResults(tournamentId);
        ui.showSuccess('Участник обновлен');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

async function deleteParticipant(tournamentId, participationId) {
    if (!ui.confirm('Вы уверены, что хотите удалить этого участника?')) {
        return;
    }
    
    try {
        ui.showLoading();
        await api.delete(`/tournaments/${tournamentId}/participants/${participationId}`);
        ui.hideLoading();
        
        loadTournamentResults(tournamentId);
        ui.showSuccess('Участник удален');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

function openEditTournamentModal(tournamentId) {
    const tournament = tournaments.find(t => t.id === tournamentId);
    if (!tournament) return;
    
    document.getElementById('editTournamentIdInput').value = tournament.id;
    document.getElementById('editTournamentName').value = tournament.name;
    document.getElementById('editTournamentDate').value = tournament.tournament_date;
    document.getElementById('editTournamentLocation').value = tournament.location;
    document.getElementById('editTournamentDescription').value = tournament.description || '';
    
    modal.open('editTournamentModal');
}

document.getElementById('editTournamentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const tournamentId = document.getElementById('editTournamentIdInput').value;
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        tournament_date: formData.get('tournament_date'),
        location: formData.get('location'),
        description: formData.get('description') || null
    };
    
    try {
        ui.showLoading();
        await api.put(`/tournaments/${tournamentId}`, data);
        ui.hideLoading();
        
        modal.close('editTournamentModal');
        await loadTournaments();
        ui.showSuccess('Турнир обновлен');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
});

async function deleteTournament(tournamentId) {
    const tournament = tournaments.find(t => t.id === tournamentId);
    if (!ui.confirm(`Вы уверены, что хотите удалить турнир "${tournament.name}"? Это также удалит всех участников.`)) {
        return;
    }
    
    try {
        ui.showLoading();
        await api.delete(`/tournaments/${tournamentId}`);
        ui.hideLoading();
        
        await loadTournaments();
        ui.showSuccess('Турнир удален');
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

loadData();

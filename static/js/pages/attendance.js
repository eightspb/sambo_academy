/**
 * Attendance Page Script
 */

let groups = [];
let selectedGroup = null;
let selectedYear = new Date().getFullYear();
let selectedMonth = new Date().getMonth();
let selectedDate = null;
let attendanceData = [];
let datesWithAttendance = new Set();

async function loadData() {
    await auth.checkAuth();
    
    try {
        const user = await api.get('/auth/me');
        document.getElementById('userName').textContent = user.full_name;
        
        groups = await api.get('/groups');
        populateGroups();
        initMonthPicker();
        
        // Check if group is passed in URL
        const urlParams = new URLSearchParams(window.location.search);
        const groupId = urlParams.get('group');
        if (groupId) {
            selectGroup(groupId);
        }
        
    } catch (error) {
        ui.showError(error.message);
    }
}

function populateGroups() {
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
    selectedGroup = groups.find(g => g.id === groupId);
    
    // Update chips UI
    document.querySelectorAll('#groupChips .chip').forEach(chip => {
        chip.classList.remove('active');
    });
    
    const activeChip = document.querySelector(`#groupChips .chip[data-group-id="${groupId}"]`);
    if (activeChip) activeChip.classList.add('active');
    
    onGroupChange();
}

function initMonthPicker() {
    const picker = document.getElementById('monthYearPicker');
    const now = new Date();
    const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    picker.value = currentMonth;
}

function onMonthChange() {
    const picker = document.getElementById('monthYearPicker');
    const [year, month] = picker.value.split('-');
    selectedYear = parseInt(year);
    selectedMonth = parseInt(month) - 1;
    renderCalendar();
}

async function onGroupChange() {
    if (!selectedGroup) {
        document.getElementById('calendarSection').classList.add('hidden');
        document.getElementById('attendanceSection').classList.add('hidden');
        return;
    }
    
    selectedDate = null; // Reset selected date when changing group
    document.getElementById('calendarSection').classList.remove('hidden');
    
    await renderCalendar();
}

async function renderCalendar() {
    if (!selectedGroup) return;
    
    // Reset selected date when month/year changes
    selectedDate = null;
    
    // Load dates with attendance for this month
    await loadAttendanceDates();
    
    const lastDay = new Date(selectedYear, selectedMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    const container = document.getElementById('calendarDays');
    container.innerHTML = '';
    
    // Get allowed weekdays based on group schedule
    const allowedWeekdays = getAllowedWeekdays();
    
    // Days of month
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayStr = formatDate(today);
    
    const weekdayNames = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    
    const validDates = [];
    
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(selectedYear, selectedMonth, day);
        const weekday = date.getDay(); // 0=Sunday, 1=Monday, ...
        
        // Filter by schedule
        if (!allowedWeekdays.includes(weekday)) {
            continue;
        }
        
        validDates.push(date);
        
        const dateStr = formatDate(date);
        
        const dayEl = document.createElement('div');
        dayEl.className = 'day-button';
        dayEl.onclick = () => selectDate(date);
        
        // Weekday label (2 letters)
        const weekdayLabel = document.createElement('div');
        weekdayLabel.className = 'day-weekday';
        weekdayLabel.textContent = weekdayNames[weekday];
        
        // Date number
        const dateLabel = document.createElement('div');
        dateLabel.className = 'day-date';
        dateLabel.textContent = day;
        
        dayEl.appendChild(weekdayLabel);
        dayEl.appendChild(dateLabel);
        
        // Highlight today
        if (dateStr === todayStr) {
            dayEl.classList.add('day-button-today');
        }
        
        // Mark days with attendance
        if (datesWithAttendance.has(dateStr)) {
            dayEl.classList.add('day-button-has-attendance');
        }
        
        container.appendChild(dayEl);
    }
    
    // Auto-select nearest date in the past or today
    if (!selectedDate && validDates.length > 0) {
        let nearestDate = validDates[0];
        
        // Find nearest date that is today or in the past
        for (let i = validDates.length - 1; i >= 0; i--) {
            const date = validDates[i];
            date.setHours(0, 0, 0, 0);
            
            if (date <= today) {
                nearestDate = date;
                break;
            }
        }
        
        selectedDate = nearestDate;
        
        // Find and highlight the selected button
        const buttons = container.querySelectorAll('.day-button');
        const selectedIndex = validDates.findIndex(d => formatDate(d) === formatDate(nearestDate));
        if (selectedIndex >= 0 && buttons[selectedIndex]) {
            buttons[selectedIndex].classList.add('day-button-selected');
        }
        
        loadAttendanceForDate(nearestDate);
    }
}

function getAllowedWeekdays() {
    if (!selectedGroup) return [];
    
    const scheduleType = selectedGroup.schedule_type;
    
    // mon_wed_fri = Monday(1), Wednesday(3), Friday(5)
    if (scheduleType === 'mon_wed_fri') {
        return [1, 3, 5];
    }
    
    // tue_thu = Tuesday(2), Thursday(4)
    if (scheduleType === 'tue_thu') {
        return [2, 4];
    }
    
    // Default: all days
    return [0, 1, 2, 3, 4, 5, 6];
}

async function loadAttendanceDates() {
    // This is a placeholder - you might want to create an endpoint
    // that returns all dates with attendance for the month
    datesWithAttendance.clear();
}

async function selectDate(date) {
    selectedDate = date;
    
    // Update UI
    document.querySelectorAll('.day-button').forEach(el => {
        el.classList.remove('day-button-selected');
    });
    event.target.closest('.day-button').classList.add('day-button-selected');
    
    await loadAttendanceForDate(date);
}

async function loadAttendanceForDate(date) {
    if (!selectedGroup) return;
    const groupId = selectedGroup.id;
    
    try {
        ui.showLoading();
        const dateStr = formatDate(date);
        attendanceData = await api.get(`/attendance/date/${groupId}/${dateStr}`);
        
        renderAttendanceList();
        document.getElementById('attendanceSection').classList.remove('hidden');
        
        const monthNames = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ];
        
        document.getElementById('attendanceTitle').textContent = 
            `Посещаемость за ${date.getDate()} ${monthNames[date.getMonth()]} ${date.getFullYear()}`;
        
        ui.hideLoading();
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

function renderAttendanceList() {
    const container = document.getElementById('attendanceList');
    
    if (attendanceData.length === 0) {
        container.innerHTML = '<p class="text-secondary" style="padding: 1rem;">В этой группе нет активных учеников</p>';
        return;
    }
    
    container.innerHTML = attendanceData.map((student, index) => {
        const bonusBadge = student.is_bonus_group ? '<span style="color: #ff6b6b; font-weight: bold; margin-left: 0.5rem;">🎁 Бонус</span>' : '';
        return `
        <div class="attendance-row">
            <div>
                <strong>${student.full_name}</strong>${bonusBadge}
            </div>
            <div class="status-buttons">
                <button 
                    class="status-btn btn-present ${student.status === 'present' ? 'active-present' : ''}"
                    onclick="setStatus(${index}, 'present')"
                >
                    ✓ Присутствовал
                </button>
                <button 
                    class="status-btn btn-absent ${student.status === 'absent' ? 'active-absent' : ''}"
                    onclick="setStatus(${index}, 'absent')"
                >
                    ✗ Отсутствовал
                </button>
                <button 
                    class="status-btn btn-transferred ${student.status === 'transferred' ? 'active-transferred' : ''}"
                    onclick="setStatus(${index}, 'transferred')"
                >
                    → Перенос
                </button>
            </div>
        </div>
        `;
    }).join('');
}

function setStatus(index, status) {
    // Toggle: если тот же статус уже выбран - убираем его (null)
    if (attendanceData[index].status === status) {
        attendanceData[index].status = null;
    } else {
        attendanceData[index].status = status;
    }
    renderAttendanceList();
}

async function saveAttendance() {
    if (!selectedGroup || !selectedDate) {
        ui.showError('Выберите группу и дату');
        return;
    }
    const groupId = selectedGroup.id;
    
    // Отправляем ВСЕХ учеников, включая тех у кого status = null
    // Backend удалит записи для учеников с null статусом
    const attendances = attendanceData.map(s => ({
        student_id: s.student_id,
        status: s.status, // Может быть null
        notes: s.notes || null
    }));
    
    const data = {
        group_id: groupId,
        session_date: formatDate(selectedDate),
        attendances: attendances
    };
    
    try {
        ui.showLoading();
        await api.post('/attendance/mark', data);
        ui.hideLoading();
        
        ui.showSuccess('Посещаемость сохранена');
        
        // Mark this date as having attendance
        datesWithAttendance.add(formatDate(selectedDate));
        renderCalendar();
        
    } catch (error) {
        ui.hideLoading();
        ui.showError(error.message);
    }
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Initialize page
loadData();

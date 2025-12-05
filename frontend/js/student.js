// Student Module

// Load student dashboard
async function loadStudentDashboard() {
    try {
        // Get student profile data
        // Get student profile data
        const profile = await getStudentProfile();

        // Update profile header
        const nameEl = document.getElementById('student-name');
        const idEl = document.getElementById('student-id-display');
        const avatarEl = document.getElementById('student-avatar-initials');

        if (nameEl) nameEl.textContent = profile.name || 'Student';
        if (idEl) idEl.textContent = `ID: ${profile.student_id || 'N/A'}`;
        if (avatarEl) avatarEl.textContent = getInitials(profile.name || 'S');

        // Update profile stats
        document.getElementById('student-grade').textContent = profile.final_grade || '--';
        document.getElementById('student-study-time').textContent = profile.study_time || '--';
        document.getElementById('student-absences').textContent = profile.absences || '--';

        // Load performance prediction
        loadStudentPrediction();

        // Load academic details
        loadStudentDetails(profile);

    } catch (error) {
        console.error('Error loading student dashboard:', error);
        showToast('Failed to load profile data', 'error');
    }
}

// Load student prediction
async function loadStudentPrediction() {
    try {
        const data = await getStudentPrediction();
        const prediction = data.prediction || {};

        const iconEl = document.getElementById('prediction-icon');
        const statusEl = document.getElementById('prediction-status');
        const detailsEl = document.getElementById('prediction-details');

        if (prediction.prediction === 'pass') {
            iconEl.className = 'prediction-icon success';
            iconEl.innerHTML = '<i class="fas fa-check-circle"></i>';
            statusEl.textContent = 'On Track to Pass';
            statusEl.style.color = 'var(--success)';
            detailsEl.textContent = `You're doing great! Keep up the good work. Current grade: ${prediction.final_grade}`;
        } else {
            iconEl.className = 'prediction-icon danger';
            iconEl.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
            statusEl.textContent = 'Needs Improvement';
            statusEl.style.color = 'var(--danger)';
            detailsEl.textContent = `You may need extra support. Current grade: ${prediction.final_grade}. Consider increasing study time.`;
        }

    } catch (error) {
        console.error('Error loading prediction:', error);
        const detailsEl = document.getElementById('prediction-details');
        if (detailsEl) {
            detailsEl.textContent = 'Unable to load prediction';
        }
    }
}

// Load student details
function loadStudentDetails(profile) {
    const detailsContainer = document.getElementById('student-details');

    if (!profile || Object.keys(profile).length === 0) {
        detailsContainer.innerHTML = '<p style="color: var(--text-secondary);">No data available</p>';
        return;
    }

    const details = [
        { label: 'Age', value: profile.age || 'N/A' },
        { label: 'Gender', value: profile.gender || 'N/A' },
        { label: 'Study Time (hrs/week)', value: profile.study_time || 'N/A' },
        { label: 'Absences', value: profile.absences || 'N/A' },
        { label: 'Parental Support', value: capitalize(profile.parental_support || 'N/A') },
        { label: 'Internet Access', value: profile.internet_access ? 'Yes' : 'No' },
        { label: 'Final Grade', value: profile.final_grade || 'N/A' },
        { label: 'Status', value: getRiskLevel(profile.final_grade || 0) + ' Risk' }
    ];

    detailsContainer.innerHTML = details.map(detail => `
        <div class="detail-item">
            <span class="detail-label">${detail.label}</span>
            <span class="detail-value">${detail.value}</span>
        </div>
    `).join('');
}

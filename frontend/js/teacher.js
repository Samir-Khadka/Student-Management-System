// Teacher Module

// Load teacher dashboard
async function loadTeacherDashboard() {
    try {
        const [studentsData, classSummary] = await Promise.all([
            getAllStudents(),
            getClassSummary()
        ]);

        const students = studentsData.students || [];
        const summary = classSummary.class_summary || {};

        // Update stats
        document.getElementById('teacher-total-students').textContent = summary.total_students || 0;
        document.getElementById('teacher-average-grade').textContent =
            (summary.average_grade || 0).toFixed(1);
        document.getElementById('teacher-at-risk').textContent =
            summary.students_below_threshold || 0;
        document.getElementById('teacher-top-performers').textContent =
            students.filter(s => s.final_grade >= 80).length;

        // Create performance chart
        createTeacherPerformanceChart(students);

        // Load at-risk students
        loadTeacherAtRiskStudents();

    } catch (error) {
        console.error('Error loading teacher dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

// Load at-risk students for teacher
async function loadTeacherAtRiskStudents() {
    try {
        const data = await getAtRiskStudents();
        const atRiskStudents = data.at_risk_students || [];

        const container = document.getElementById('teacher-at-risk-list');

        if (atRiskStudents.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); padding: 1rem;">No students need attention</p>';
            return;
        }

        container.innerHTML = atRiskStudents.slice(0, 5).map(student => `
            <div class="detail-item">
                <div>
                    <strong>${student.name}</strong><br>
                    <small style="color: var(--text-secondary);">${student.student_id} - Grade: ${student.final_grade}</small>
                </div>
                <span class="status-badge danger">At Risk</span>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading at-risk students:', error);
    }
}

// Load teacher students view (read-only)
async function loadTeacherStudents() {
    try {
        const data = await getAllStudents();
        const students = data.students || [];

        renderTeacherStudentsTable(students);
        initializeTeacherFilters();

    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Failed to load students', 'error');
    }
}

// Render teacher students table (read-only)
function renderTeacherStudentsTable(students) {
    const tbody = document.getElementById('students-table-body');

    if (students.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No students found
                </td>
            </tr>
        `;
        return;
    }

    // Teacher view - no action buttons (read-only)
    tbody.innerHTML = students.map(student => `
        <tr>
            <td>${student.student_id}</td>
            <td>${student.name}</td>
            <td>${student.age}</td>
            <td>${student.gender}</td>
            <td><strong>${student.final_grade}</strong></td>
            <td>${getStatusBadge(student.final_grade)}</td>
            <td>
                <div class="action-buttons">
                    <button onclick="viewStudentDetails('${student.student_id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="openGradeModal('${student.student_id}', ${student.final_grade}, '${student.name}')" title="Edit Grade" style="background: var(--warning);">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Initialize teacher filters
function initializeTeacherFilters() {
    const searchInput = document.getElementById('student-search');
    const genderFilter = document.getElementById('gender-filter');
    const supportFilter = document.getElementById('support-filter');

    if (!searchInput) return;

    const debouncedSearch = debounce(async () => {
        await loadTeacherStudents();
    }, APP_SETTINGS.DEBOUNCE_DELAY);

    searchInput.addEventListener('input', debouncedSearch);

    if (genderFilter) genderFilter.addEventListener('change', loadTeacherStudents);
    if (supportFilter) supportFilter.addEventListener('change', loadTeacherStudents);
}

// View student details (read-only modal)
async function viewStudentDetails(studentId) {
    try {
        const data = await getStudentById(studentId);
        const student = data.student;

        // Show details in a simple alert or toast for now
        // In a real implementation, you'd create a read-only modal
        const details = `
Student ID: ${student.student_id}
Name: ${student.name}
Age: ${student.age}
Gender: ${student.gender}
Study Time: ${student.study_time} hrs/week
Absences: ${student.absences}
Parental Support: ${capitalize(student.parental_support)}
Internet Access: ${student.internet_access ? 'Yes' : 'No'}
Final Grade: ${student.final_grade}
        `;

        alert(details);

    } catch (error) {
        showToast('Failed to load student details', 'error');
    }
}

// ===============================================
// Grade Management
// ===============================================

let editingGradeStudentId = null;

// Open grade modal
function openGradeModal(studentId, currentGrade, studentName) {
    editingGradeStudentId = studentId;
    document.getElementById('grade-student-name').value = studentName;
    document.getElementById('grade-input').value = currentGrade;
    document.getElementById('teacher-grade-modal').classList.add('active');
}

// Close grade modal
function closeGradeModal() {
    document.getElementById('teacher-grade-modal').classList.remove('active');
    editingGradeStudentId = null;
    document.getElementById('teacher-grade-form').reset();
}

// Initialize teacher grade form
function initTeacherGradeForm() {
    const form = document.getElementById('teacher-grade-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!editingGradeStudentId) return;

        const newGrade = parseInt(document.getElementById('grade-input').value);
        const submitBtn = form.querySelector('button[type="submit"]');
        setLoading(submitBtn, true);

        try {
            // We only update the grade, keeping other fields as is
            // Since the update endpoint requires a full object or partial, 
            // we'll send just the final_grade. The backend supports partial updates.
            await updateStudent(editingGradeStudentId, { final_grade: newGrade });

            showToast('Grade updated successfully');
            closeGradeModal();
            loadTeacherStudents(); // Refresh table

            // Also refresh stats if needed
            loadTeacherDashboard();

        } catch (error) {
            console.error('Error updating grade:', error);
            showToast(error.message || 'Failed to update grade', 'error');
        } finally {
            setLoading(submitBtn, false);
        }
    });
}

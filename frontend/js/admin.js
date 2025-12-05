// Admin Module

let allStudents = [];
let filteredStudents = [];
let editingStudentId = null;

// Load admin dashboard
async function loadAdminDashboard() {
    console.log('Loading admin dashboard...');

    try {
        // Load statistics with individual error handling
        console.log('Fetching dashboard data from API...');

        let students = [];
        let avgGrade = 0;
        let atRiskStudents = [];
        let total = 0;

        try {
            const studentsData = await getAllStudents();
            console.log('Students data received:', studentsData);
            students = studentsData.students || [];
            total = studentsData.total || 0;
        } catch (error) {
            console.error('Error fetching students:', error);
            showToast('Failed to load students data', 'error');
        }

        try {
            const avgGradeData = await getAverageGrade();
            console.log('Average grade data received:', avgGradeData);
            avgGrade = avgGradeData.average_grade || 0;
        } catch (error) {
            console.error('Error fetching average grade:', error);
            showToast('Failed to load average grade', 'error');
        }

        try {
            const atRiskData = await getAtRiskStudents();
            console.log('At-risk students data received:', atRiskData);
            atRiskStudents = atRiskData.at_risk_students || [];
        } catch (error) {
            console.error('Error fetching at-risk students:', error);
            showToast('Failed to load at-risk students', 'error');
        }

        // Update stats
        console.log('Updating dashboard stats...');
        document.getElementById('total-students').textContent = total;

        try {
            const teachersData = await getAllTeachers();
            const teacherCount = teachersData.count || (teachersData.teachers ? teachersData.teachers.length : 0);
            document.getElementById('total-teachers').textContent = teacherCount;
        } catch (error) {
            console.error('Error fetching teachers count:', error);
            document.getElementById('total-teachers').textContent = '0';
        }

        document.getElementById('at-risk-students').textContent = atRiskStudents.length;
        document.getElementById('average-grade').textContent = avgGrade.toFixed(1);

        // Load recent students
        console.log('Loading recent students...');
        loadRecentStudents(students.slice(0, 5));

        // Create performance distribution chart
        console.log('Creating performance chart...');
        const excellent = students.filter(s => s.final_grade >= 70).length;
        const average = students.filter(s => s.final_grade >= 40 && s.final_grade < 70).length;
        const atRisk = students.filter(s => s.final_grade < 40).length;

        createPerformanceChart({ excellent, average, atRisk });

        console.log('Admin dashboard loaded successfully');

    } catch (error) {
        console.error('Critical error loading admin dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

// Load recent students
function loadRecentStudents(students) {
    const container = document.getElementById('recent-students-list');

    if (!students || students.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 1rem;">No students found</p>';
        return;
    }

    container.innerHTML = students.map(student => `
        <div class="detail-item">
            <span>${student.name}</span>
            <span class="stat-value" style="font-size: 1rem;">${student.final_grade}</span>
        </div>
    `).join('');
}

// Load admin students table
async function loadAdminStudents() {
    try {
        const data = await getAllStudents();
        allStudents = data.students || [];
        filteredStudents = [...allStudents];

        renderStudentsTable();
        initializeStudentFilters();

    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Failed to load students', 'error');
    }
}

// Render students table
function renderStudentsTable() {
    const tbody = document.getElementById('students-table-body');

    if (filteredStudents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No students found
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filteredStudents.map(student => `
        <tr>
            <td>${student.student_id}</td>
            <td>${student.name}</td>
            <td>${student.age}</td>
            <td>${student.gender}</td>
            <td><strong>${student.final_grade}</strong></td>
            <td>${getStatusBadge(student.final_grade)}</td>
            <td>
                <div class="action-buttons">
                    <button onclick="editStudent('${student.student_id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="danger" onclick="confirmDeleteStudent('${student.student_id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Initialize student filters
function initializeStudentFilters() {
    const searchInput = document.getElementById('student-search');
    const genderFilter = document.getElementById('gender-filter');
    const supportFilter = document.getElementById('support-filter');

    // Search
    const debouncedSearch = debounce(() => {
        filterStudents();
    }, APP_SETTINGS.DEBOUNCE_DELAY);

    searchInput.addEventListener('input', debouncedSearch);

    // Filters
    genderFilter.addEventListener('change', filterStudents);
    supportFilter.addEventListener('change', filterStudents);
}

// Filter students
function filterStudents() {
    const searchTerm = document.getElementById('student-search').value.toLowerCase();
    const genderFilter = document.getElementById('gender-filter').value;
    const supportFilter = document.getElementById('support-filter').value;

    filteredStudents = allStudents.filter(student => {
        const matchesSearch = !searchTerm ||
            student.name.toLowerCase().includes(searchTerm) ||
            student.student_id.toLowerCase().includes(searchTerm);

        const matchesGender = !genderFilter || student.gender === genderFilter;
        const matchesSupport = !supportFilter || student.parental_support === supportFilter;

        return matchesSearch && matchesGender && matchesSupport;
    });

    renderStudentsTable();
}

// Open add student modal
function openAddStudentModal() {
    editingStudentId = null;
    document.getElementById('modal-title').textContent = 'Add Student';
    clearForm('student-form');
    document.getElementById('student-modal').classList.add('active');
}

// Edit student
async function editStudent(studentId) {
    try {
        const data = await getStudentById(studentId);
        const student = data.student;

        editingStudentId = studentId;
        document.getElementById('modal-title').textContent = 'Edit Student';

        // Populate form
        document.getElementById('student-id-input').value = student.student_id;
        document.getElementById('student-id-input').disabled = true;
        document.getElementById('student-name-input').value = student.name;
        document.getElementById('student-age-input').value = student.age;
        document.getElementById('student-gender-input').value = student.gender;
        document.getElementById('student-study-time-input').value = student.study_time;
        document.getElementById('student-absences-input').value = student.absences;
        document.getElementById('student-support-input').value = student.parental_support;
        document.getElementById('student-internet-input').value = student.internet_access.toString();
        document.getElementById('student-grade-input').value = student.final_grade;

        document.getElementById('student-modal').classList.add('active');

    } catch (error) {
        showToast('Failed to load student data', 'error');
    }
}

// Close student modal
function closeStudentModal() {
    document.getElementById('student-modal').classList.remove('active');
    document.getElementById('student-id-input').disabled = false;
    clearForm('student-form');
    editingStudentId = null;
}

// Initialize student form
function initStudentForm() {
    const form = document.getElementById('student-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const studentData = {
            student_id: document.getElementById('student-id-input').value.trim(),
            name: document.getElementById('student-name-input').value.trim(),
            age: parseInt(document.getElementById('student-age-input').value),
            gender: document.getElementById('student-gender-input').value,
            study_time: parseInt(document.getElementById('student-study-time-input').value),
            absences: parseInt(document.getElementById('student-absences-input').value),
            parental_support: document.getElementById('student-support-input').value,
            internet_access: document.getElementById('student-internet-input').value === 'true',
            final_grade: parseInt(document.getElementById('student-grade-input').value)
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        setLoading(submitBtn, true);

        try {
            if (editingStudentId) {
                await updateStudent(editingStudentId, studentData);
                showToast('Student updated successfully');
            } else {
                await createStudent(studentData);
                showToast('Student added successfully');
            }

            closeStudentModal();
            loadAdminStudents();

            // Reload dashboard if on dashboard
            if (currentSection === 'admin-dashboard') {
                loadAdminDashboard();
            }

        } catch (error) {
            showToast(error.message || 'Failed to save student', 'error');
        } finally {
            setLoading(submitBtn, false);
        }
    });
}

// Confirm delete student
function confirmDeleteStudent(studentId) {
    if (confirm('Are you sure you want to delete this student? This action cannot be undone.')) {
        deleteStudentById(studentId);
    }
}

// Delete student
async function deleteStudentById(studentId) {
    try {
        await deleteStudent(studentId);
        showToast('Student deleted successfully');
        loadAdminStudents();

        // Reload dashboard if on dashboard
        if (currentSection === 'admin-dashboard') {
            loadAdminDashboard();
        }

    } catch (error) {
        showToast(error.message || 'Failed to delete student', 'error');
    }
}

// Load analytics
async function loadAnalytics() {
    try {
        const [genderData, supportData, internetData, atRiskData] = await Promise.all([
            getGenderDistribution(),
            getPerformanceBySupport(),
            getInternetAccessImpact(),
            getAtRiskStudents()
        ]);

        // Create charts
        createGenderChart(genderData);
        createSupportChart(supportData);
        createInternetChart(internetData);

        // Display at-risk students
        const atRiskList = document.getElementById('at-risk-list');
        const atRiskStudents = atRiskData.at_risk_students || [];

        if (atRiskStudents.length === 0) {
            atRiskList.innerHTML = '<p style="color: var(--text-secondary);">No at-risk students</p>';
        } else {
            atRiskList.innerHTML = atRiskStudents.map(student => `
                <div class="detail-item">
                    <div>
                        <strong>${student.name}</strong><br>
                        <small style="color: var(--text-secondary);">${student.student_id}</small>
                    </div>
                    <span class="status-badge danger">${student.final_grade}</span>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Failed to load analytics', 'error');
    }
}

// ===============================================
// Teachers Management
// ===============================================

let allTeachers = [];
let editingTeacherId = null;

// Load admin teachers table
async function loadAdminTeachers() {
    try {
        const data = await getAllTeachers();
        allTeachers = data.teachers || [];
        renderTeachersTable(allTeachers);

        // Initialize search
        const searchInput = document.getElementById('teacher-search');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => {
                const term = searchInput.value.toLowerCase();
                const filtered = allTeachers.filter(t =>
                    t.name.toLowerCase().includes(term) ||
                    t.teacher_id.toLowerCase().includes(term) ||
                    t.subject.toLowerCase().includes(term)
                );
                renderTeachersTable(filtered);
            }, APP_SETTINGS.DEBOUNCE_DELAY));
        }

    } catch (error) {
        console.error('Error loading teachers:', error);
        showToast('Failed to load teachers', 'error');
    }
}

// Render teachers table
function renderTeachersTable(teachers) {
    const tbody = document.getElementById('teachers-table-body');
    if (!tbody) return;

    if (teachers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No teachers found
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = teachers.map(teacher => `
        <tr>
            <td>${teacher.teacher_id}</td>
            <td>${teacher.name}</td>
            <td>${teacher.email}</td>
            <td>${teacher.subject}</td>
            <td>${teacher.phone || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button onclick="editTeacher('${teacher.teacher_id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="danger" onclick="confirmDeleteTeacher('${teacher.teacher_id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Open add teacher modal
function openAddTeacherModal() {
    editingTeacherId = null;
    document.getElementById('teacher-modal-title').textContent = 'Add Teacher';
    clearForm('teacher-form');
    document.getElementById('teacher-modal').classList.add('active');
}

// Close teacher modal
function closeTeacherModal() {
    document.getElementById('teacher-modal').classList.remove('active');
    document.getElementById('teacher-id-input').disabled = false;
    clearForm('teacher-form');
    editingTeacherId = null;
}

// Edit teacher
async function editTeacher(teacherId) {
    const teacher = allTeachers.find(t => t.teacher_id === teacherId);
    if (!teacher) return;

    editingTeacherId = teacherId;
    document.getElementById('teacher-modal-title').textContent = 'Edit Teacher';

    document.getElementById('teacher-id-input').value = teacher.teacher_id;
    document.getElementById('teacher-id-input').disabled = true;
    document.getElementById('teacher-name-input').value = teacher.name;
    document.getElementById('teacher-email-input').value = teacher.email;
    document.getElementById('teacher-subject-input').value = teacher.subject;
    document.getElementById('teacher-phone-input').value = teacher.phone || '';
    document.getElementById('teacher-qualification-input').value = teacher.qualification || '';

    document.getElementById('teacher-modal').classList.add('active');
}

// Initialize teacher form
function initTeacherForm() {
    const form = document.getElementById('teacher-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const teacherData = {
            teacher_id: document.getElementById('teacher-id-input').value.trim(),
            name: document.getElementById('teacher-name-input').value.trim(),
            email: document.getElementById('teacher-email-input').value.trim(),
            subject: document.getElementById('teacher-subject-input').value.trim(),
            phone: document.getElementById('teacher-phone-input').value.trim(),
            qualification: document.getElementById('teacher-qualification-input').value.trim()
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        setLoading(submitBtn, true);

        try {
            if (editingTeacherId) {
                await updateTeacher(editingTeacherId, teacherData);
                showToast('Teacher updated successfully');
            } else {
                await createTeacher(teacherData);
                showToast('Teacher added successfully');
            }

            closeTeacherModal();
            loadAdminTeachers();

        } catch (error) {
            showToast(error.message || 'Failed to save teacher', 'error');
        } finally {
            setLoading(submitBtn, false);
        }
    });
}

// Confirm delete teacher
function confirmDeleteTeacher(teacherId) {
    if (confirm('Are you sure you want to delete this teacher? This will also delete their user account.')) {
        deleteTeacherById(teacherId);
    }
}

// Delete teacher
async function deleteTeacherById(teacherId) {
    try {
        await deleteTeacher(teacherId);
        showToast('Teacher deleted successfully');
        loadAdminTeachers();
    } catch (error) {
        showToast(error.message || 'Failed to delete teacher', 'error');
    }
}

// Dashboard Module

let currentSection = null;

// Initialize dashboard
async function initDashboard() {
    try {
        const user = getCurrentUserData();

        if (!user || !user.role) {
            console.error('Invalid user data:', user);
            logout();
            return;
        }

        // Show dashboard screen
        showDashboardScreen();

        // Update user info in nav
        updateUserInfo(user);

        // Build sidebar menu based on role
        buildSidebarMenu(user.role);

        // Load appropriate dashboard for role
        switch (user.role) {
            case 'admin':
                showSection('admin-dashboard');
                loadAdminDashboard();
                break;
            case 'teacher':
                showSection('teacher-dashboard');
                loadTeacherDashboard();
                break;
            case 'student':
                showSection('student-dashboard');
                loadStudentDashboard();
                break;
            default:
                showToast('Unknown user role', 'error');
                logout();
        }
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showToast('Error loading dashboard', 'error');
        logout();
    }
}

// Update user info in navigation
function updateUserInfo(user) {
    const userNameEl = document.getElementById('user-name');
    const userRoleEl = document.getElementById('user-role');
    const userInitialsEl = document.getElementById('user-initials');

    if (userNameEl) userNameEl.textContent = user.full_name || user.username || 'User';
    if (userRoleEl) userRoleEl.textContent = capitalize(user.role || 'guest');
    if (userInitialsEl) userInitialsEl.textContent = getInitials(user.full_name || user.username || 'U');
}

// Build sidebar menu
function buildSidebarMenu(role) {
    const sidebarMenu = document.getElementById('sidebar-menu');
    const menuItems = MENU_ITEMS[role] || [];

    sidebarMenu.innerHTML = '';

    menuItems.forEach(item => {
        const li = document.createElement('li');
        const a = document.createElement('a');

        a.href = '#';
        a.dataset.section = item.id;
        a.innerHTML = `<i class="fas ${item.icon}"></i><span>${item.label}</span>`;

        a.addEventListener('click', (e) => {
            e.preventDefault();
            showSection(item.id);
        });

        li.appendChild(a);
        sidebarMenu.appendChild(li);
    });
}

// Show section
function showSection(sectionId) {
    // Update active state in sidebar
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    menuLinks.forEach(link => {
        if (link.dataset.section === sectionId) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;

        // Load section-specific data
        loadSectionData(sectionId);
    }
}

// Load section-specific data
function loadSectionData(sectionId) {
    const user = getCurrentUserData();

    switch (sectionId) {
        case 'admin-dashboard':
            loadAdminDashboard();
            break;
        case 'students-section':
            if (user.role === 'admin') {
                loadAdminStudents();
            } else {
                loadTeacherStudents();
            }
            break;
        case 'analytics-section':
            loadAnalytics();
            break;
        case 'teacher-dashboard':
            loadTeacherDashboard();
            break;
        case 'student-dashboard':
            loadStudentDashboard();
            break;
    }
}

// Toggle sidebar (mobile)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside (mobile)
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.querySelector('.menu-toggle');

    if (sidebar && !sidebar.contains(e.target) && e.target !== menuToggle && !menuToggle.contains(e.target)) {
        sidebar.classList.remove('open');
    }
});

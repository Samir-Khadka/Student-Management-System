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
    // Navbar elements
    const userNameEl = document.getElementById('user-name');
    const userRoleEl = document.getElementById('user-role');
    const userAvatarEl = document.getElementById('user-avatar');
    const userInitialsEl = document.getElementById('user-initials');

    // Dropdown elements
    const dropdownNameEl = document.getElementById('dropdown-name');
    const dropdownEmailEl = document.getElementById('dropdown-email');
    const dropdownAvatarEl = document.getElementById('dropdown-avatar-menu');
    const dropdownInitialsEl = document.getElementById('dropdown-initials');

    // Update text content
    const fullName = user.full_name || user.username || 'User';
    const role = capitalize(user.role || 'guest');
    const initials = getInitials(fullName);

    if (userNameEl) userNameEl.textContent = fullName;
    if (userRoleEl) userRoleEl.textContent = role;
    if (userInitialsEl) userInitialsEl.textContent = initials;

    if (dropdownNameEl) dropdownNameEl.textContent = fullName;
    if (dropdownEmailEl) dropdownEmailEl.textContent = user.email || '';
    if (dropdownInitialsEl) dropdownInitialsEl.textContent = initials;

    // Helper to update avatar container
    const updateAvatarContainer = (container, initialsSpanId) => {
        if (!container) return;

        if (user.profile_picture) {
            const apiUrl = API_CONFIG.BASE_URL.replace('/api', '');
            const profilePictureUrl = `${apiUrl}${user.profile_picture}?t=${new Date().getTime()}`;

            container.innerHTML = `<img src="${profilePictureUrl}" alt="${fullName}" 
                style="width: 100%; height: 100%; object-fit: cover;"
                onerror="this.style.display='none'; document.getElementById('${initialsSpanId}').style.display='block';">
                <span id="${initialsSpanId}" style="display:none">${initials}</span>`;
        } else {
            container.innerHTML = `<span id="${initialsSpanId}">${initials}</span>`;
        }
    };

    // Update avatars
    updateAvatarContainer(userAvatarEl, 'user-initials');
    updateAvatarContainer(dropdownAvatarEl, 'dropdown-initials');
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

// Dropdown Management
function toggleUserDropdown(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', (event) => {
    const dropdown = document.getElementById('user-dropdown');
    const userInfo = document.querySelector('.user-info');

    if (dropdown && dropdown.classList.contains('active')) {
        if (!userInfo.contains(event.target)) {
            dropdown.classList.remove('active');
        }
    }
});

// Profile Modal Management
function openProfileModal() {
    const modal = document.getElementById('profile-modal');
    if (modal) {
        modal.classList.add('active');
        loadProfileSection(); // Load data when opening
    }
    // Close dropdown
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) dropdown.classList.remove('active');
}

function closeProfileModal() {
    const modal = document.getElementById('profile-modal');
    if (modal) {
        modal.classList.remove('active');
        // Reset edit mode if active
        if (typeof isEditMode !== 'undefined' && isEditMode) {
            toggleEditMode();
        }
    }
}

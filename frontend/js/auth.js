// Authentication Module

// Check if user is authenticated
function isAuthenticated() {
    const token = localStorage.getItem(APP_SETTINGS.TOKEN_KEY);
    return token !== null;
}

// Get current user from localStorage
function getCurrentUserData() {
    const userData = localStorage.getItem(APP_SETTINGS.USER_KEY);
    return userData ? JSON.parse(userData) : null;
}

// Save user data
function saveUserData(user, token) {
    localStorage.setItem(APP_SETTINGS.TOKEN_KEY, token);
    localStorage.setItem(APP_SETTINGS.USER_KEY, JSON.stringify(user));
}

// Clear user data
function clearUserData() {
    localStorage.removeItem(APP_SETTINGS.TOKEN_KEY);
    localStorage.removeItem(APP_SETTINGS.USER_KEY);
}

// Switch auth tab
function switchAuthTab(tabName) {
    const tab = document.querySelector(`.auth-tab[data-tab="${tabName}"]`);
    if (tab) {
        tab.click();
    }
}

// Initialize auth screen
function initAuthScreen() {
    // Tab switching
    const authTabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Update active tab
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show corresponding form
            if (tabName === 'login') {
                loginForm.classList.add('active');
                registerForm.classList.remove('active');
            } else {
                registerForm.classList.add('active');
                loginForm.classList.remove('active');
            }
        });
    });

    // Show student ID field when student role is selected
    const roleSelect = document.getElementById('register-role');
    const studentIdGroup = document.getElementById('student-id-group');

    roleSelect.addEventListener('change', () => {
        if (roleSelect.value === 'student') {
            studentIdGroup.style.display = 'block';
            document.getElementById('register-student-id').required = true;
        } else {
            studentIdGroup.style.display = 'none';
            document.getElementById('register-student-id').required = false;
        }
    });

    // Login form submission
    loginForm.addEventListener('submit', handleLogin);

    // Register form submission
    registerForm.addEventListener('submit', handleRegister);
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');

    if (!username || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    setLoading(submitBtn, true);

    try {
        const response = await loginUser(username, password);

        // Save user data and token
        saveUserData(response.user, response.access_token);

        showToast('Login successful!');

        // Clear form
        clearForm('login-form');

        // Redirect to dashboard
        setTimeout(() => {
            initDashboard();
        }, 500);

    } catch (error) {
        showToast(error.message || 'Login failed', 'error');
    } finally {
        setLoading(submitBtn, false);
    }
}

// Handle registration
async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const fullName = document.getElementById('register-full-name').value.trim();
    const role = document.getElementById('register-role').value;
    const studentId = document.getElementById('register-student-id').value.trim();
    const submitBtn = e.target.querySelector('button[type="submit"]');

    // Validation
    if (!username || !email || !password || !fullName || !role) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    if (!validateEmail(email)) {
        showToast('Please enter a valid email', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    if (role === 'student' && !studentId) {
        showToast('Student ID is required for student role', 'error');
        return;
    }

    setLoading(submitBtn, true);

    try {
        const userData = {
            username,
            email,
            password,
            full_name: fullName,
            role
        };

        if (role === 'student') {
            userData.student_id = studentId;
        }

        await registerUser(userData);

        showToast('Registration successful! Please login.');

        // Clear form
        clearForm('register-form');

        // Switch to login tab
        document.querySelector('.auth-tab[data-tab="login"]').click();

    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
    } finally {
        setLoading(submitBtn, false);
    }
}

// Logout function
async function logout() {
    try {
        await logoutUser();
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        clearUserData();
        showToast('Logged out successfully');
        showLandingScreen();
    }
}

// Screen navigation functions
function showLandingScreen() {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById('landing-screen').classList.add('active');
}

function showAuthScreen() {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById('auth-screen').classList.add('active');
}

function showDashboardScreen() {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById('dashboard-screen').classList.add('active');
}

function scrollToFeatures() {
    const featuresSection = document.getElementById('features');
    featuresSection.scrollIntoView({ behavior: 'smooth' });
}

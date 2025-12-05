// Main Application Entry Point

// Initialize application on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is authenticated
    if (isAuthenticated()) {
        try {
            // Verify token validity with backend and get fresh user data
            const response = await getCurrentUser();

            // Update local storage with fresh data
            const token = localStorage.getItem(APP_SETTINGS.TOKEN_KEY);
            if (response.user && token) {
                saveUserData(response.user, token);
            }

            // User is logged in and token is valid, show dashboard
            await initDashboard();
        } catch (error) {
            console.error('Session expired or invalid:', error);
            clearUserData();
            showLandingScreen();
        }
    } else {
        // User is not logged in, show landing page
        showLandingScreen();
    }

    // Initialize auth screen handlers
    initAuthScreen();

    // Initialize student form (for admin)
    initStudentForm();
    initTeacherForm();
    initTeacherGradeForm();

    // Close modal when clicking outside
    const modal = document.getElementById('student-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeStudentModal();
            }
        });
    }
});

// Handle browser back/forward buttons
window.addEventListener('popstate', () => {
    if (isAuthenticated()) {
        initDashboard();
    } else {
        showLandingScreen();
    }
});

// Prevent form submission on enter key in search fields
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.closest('.search-box')) {
        e.preventDefault();
    }
});

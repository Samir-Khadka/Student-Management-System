// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:5001/api',
    ENDPOINTS: {
        // Auth endpoints
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        LOGOUT: '/auth/logout',
        ME: '/auth/me',
        CHANGE_PASSWORD: '/auth/change-password',
        PROFILE_UPDATE: '/auth/profile',
        UPLOAD_PICTURE: '/auth/upload-picture',
        FORGOT_PASSWORD: '/auth/forgot-password',
        RESET_PASSWORD: '/auth/reset-password',

        // Student endpoints
        STUDENTS: '/students/',
        STUDENT_BY_ID: (id) => `/students/${id}`,
        STUDENT_PREDICT: (id) => `/students/predict/${id}`,

        // Teacher endpoints
        TEACHERS: '/teachers/',
        TEACHER_BY_ID: (id) => `/teachers/${id}`,

        // Student profile endpoints
        STUDENT_PROFILE: '/student/profile',
        STUDENT_PREDICTION: '/student/profile/prediction',

        // Analytics endpoints
        AVERAGE_GRADE: '/analytics/average_grade',
        AT_RISK_STUDENTS: '/analytics/at_risk_students',
        GENDER_DISTRIBUTION: '/analytics/gender_distribution',
        PERFORMANCE_BY_SUPPORT: '/analytics/performance_by_support',
        INTERNET_ACCESS_IMPACT: '/analytics/internet_access_impact',
        CLASS_SUMMARY: '/analytics/class_summary'
    }
};

// App Settings
const APP_SETTINGS = {
    TOKEN_KEY: 'auth_token',
    USER_KEY: 'user_data',
    TOAST_DURATION: 3000,
    DEBOUNCE_DELAY: 300
};

// Role-based menu items
const MENU_ITEMS = {
    admin: [
        { id: 'admin-dashboard', icon: 'fa-dashboard', label: 'Dashboard' },
        { id: 'students-section', icon: 'fa-user-graduate', label: 'Students' },
        { id: 'teachers-section', icon: 'fa-chalkboard-teacher', label: 'Teachers' },
        { id: 'analytics-section', icon: 'fa-chart-line', label: 'Analytics' }
    ],
    teacher: [
        { id: 'teacher-dashboard', icon: 'fa-dashboard', label: 'Dashboard' },
        { id: 'students-section', icon: 'fa-users', label: 'All Students' },
        { id: 'analytics-section', icon: 'fa-chart-bar', label: 'Analytics' }
    ],
    student: [
        { id: 'student-dashboard', icon: 'fa-user', label: 'My Profile' }
    ]
};

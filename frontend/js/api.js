// API Service Layer

// Generic API request function
async function apiRequest(endpoint, method = 'GET', data = null, requiresAuth = true) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json'
    };

    // Add authorization header if required
    if (requiresAuth) {
        const token = localStorage.getItem(APP_SETTINGS.TOKEN_KEY);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    const options = {
        method,
        headers
    };

    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(responseData.message || responseData.error || 'Request failed');
        }

        return responseData;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// ===============================================
// Auth API
// ===============================================

async function loginUser(username, password) {
    return await apiRequest(API_CONFIG.ENDPOINTS.LOGIN, 'POST', {
        username,
        password
    }, false);
}

async function registerUser(userData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.REGISTER, 'POST', userData, false);
}

async function logoutUser() {
    return await apiRequest(API_CONFIG.ENDPOINTS.LOGOUT, 'POST');
}

async function getCurrentUser() {
    return await apiRequest(API_CONFIG.ENDPOINTS.ME, 'GET');
}

async function changePassword(currentPassword, newPassword) {
    return await apiRequest(API_CONFIG.ENDPOINTS.CHANGE_PASSWORD, 'POST', {
        current_password: currentPassword,
    });
}

async function updateUserProfile(profileData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.PROFILE_UPDATE, 'PUT', profileData);
}

async function uploadProfilePicture(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem(APP_SETTINGS.TOKEN_KEY);

    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.UPLOAD_PICTURE}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });

    const responseData = await response.json();

    if (!response.ok) {
        throw new Error(responseData.message || responseData.error || 'Upload failed');
    }

    return responseData;
}

// ===============================================
// Students API
// ===============================================

async function getAllStudents(filters = {}) {
    let endpoint = API_CONFIG.ENDPOINTS.STUDENTS;
    const params = new URLSearchParams();

    if (filters.gender) params.append('gender', filters.gender);
    if (filters.parental_support) params.append('parental_support', filters.parental_support);
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.skip) params.append('skip', filters.skip);

    const queryString = params.toString();
    if (queryString) {
        endpoint += `?${queryString}`;
    }

    return await apiRequest(endpoint, 'GET');
}

async function getStudentById(studentId) {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_BY_ID(studentId), 'GET');
}

async function createStudent(studentData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENTS, 'POST', studentData);
}

async function updateStudent(studentId, studentData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_BY_ID(studentId), 'PUT', studentData);
}

async function deleteStudent(studentId) {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_BY_ID(studentId), 'DELETE');
}

async function predictStudentPerformance(studentId) {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_PREDICT(studentId), 'GET');
}

// ===============================================
// Teachers API
// ===============================================

async function getAllTeachers() {
    return await apiRequest(API_CONFIG.ENDPOINTS.TEACHERS, 'GET');
}

async function createTeacher(teacherData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.TEACHERS, 'POST', teacherData);
}

async function updateTeacher(teacherId, teacherData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.TEACHER_BY_ID(teacherId), 'PUT', teacherData);
}

async function deleteTeacher(teacherId) {
    return await apiRequest(API_CONFIG.ENDPOINTS.TEACHER_BY_ID(teacherId), 'DELETE');
}

// ===============================================
// Student Profile API (for logged-in students)
// ===============================================

async function getStudentProfile() {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_PROFILE, 'GET');
}

async function updateStudentProfile(profileData) {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_PROFILE, 'PUT', profileData);
}

async function getStudentPrediction() {
    return await apiRequest(API_CONFIG.ENDPOINTS.STUDENT_PREDICTION, 'GET');
}

// ===============================================
// Analytics API
// ===============================================

async function getAverageGrade(filters = {}) {
    let endpoint = API_CONFIG.ENDPOINTS.AVERAGE_GRADE;
    const params = new URLSearchParams();

    if (filters.gender) params.append('gender', filters.gender);
    if (filters.parental_support) params.append('parental_support', filters.parental_support);

    const queryString = params.toString();
    if (queryString) {
        endpoint += `?${queryString}`;
    }

    return await apiRequest(endpoint, 'GET');
}

async function getAtRiskStudents(threshold = 40) {
    return await apiRequest(`${API_CONFIG.ENDPOINTS.AT_RISK_STUDENTS}?threshold=${threshold}`, 'GET');
}

async function getGenderDistribution() {
    return await apiRequest(API_CONFIG.ENDPOINTS.GENDER_DISTRIBUTION, 'GET');
}

async function getPerformanceBySupport() {
    return await apiRequest(API_CONFIG.ENDPOINTS.PERFORMANCE_BY_SUPPORT, 'GET');
}

async function getInternetAccessImpact() {
    return await apiRequest(API_CONFIG.ENDPOINTS.INTERNET_ACCESS_IMPACT, 'GET');
}

async function getClassSummary() {
    return await apiRequest(API_CONFIG.ENDPOINTS.CLASS_SUMMARY, 'GET');
}

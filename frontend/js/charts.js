// Charts Module using Chart.js

let performanceChart = null;
let genderChart = null;
let supportChart = null;
let internetChart = null;
let teacherPerformanceChart = null;

// Chart default configuration
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            labels: {
                color: '#a0a0b0',
                font: {
                    family: 'Inter'
                }
            }
        }
    },
    scales: {
        y: {
            ticks: { color: '#a0a0b0' },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        x: {
            ticks: { color: '#a0a0b0' },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
    }
};

// Create performance distribution chart
function createPerformanceChart(data) {
    const ctx = document.getElementById('performance-chart');
    if (!ctx) return;

    if (performanceChart) {
        performanceChart.destroy();
    }

    performanceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Excellent (70+)', 'Average (40-69)', 'At Risk (<40)'],
            datasets: [{
                data: [
                    data.excellent || 0,
                    data.average || 0,
                    data.atRisk || 0
                ],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0a0b0',
                        padding: 15,
                        font: {
                            family: 'Inter',
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Create gender distribution chart
function createGenderChart(data) {
    const ctx = document.getElementById('gender-chart');
    if (!ctx) return;

    if (genderChart) {
        genderChart.destroy();
    }

    const distribution = data.gender_distribution || {};

    genderChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(distribution),
            datasets: [{
                data: Object.values(distribution),
                backgroundColor: [
                    'rgba(124, 58, 237, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(6, 182, 212, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0a0b0',
                        padding: 15,
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            }
        }
    });
}

// Create performance by support chart
function createSupportChart(data) {
    const ctx = document.getElementById('support-chart');
    if (!ctx) return;

    if (supportChart) {
        supportChart.destroy();
    }

    const supportData = data.performance_by_support || {};
    const labels = Object.keys(supportData).map(key => capitalize(key));
    const avgGrades = Object.values(supportData).map(val => val.average_grade || 0);

    supportChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Grade',
                data: avgGrades,
                backgroundColor: 'rgba(124, 58, 237, 0.8)',
                borderRadius: 8
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Create internet access impact chart
function createInternetChart(data) {
    const ctx = document.getElementById('internet-chart');
    if (!ctx) return;

    if (internetChart) {
        internetChart.destroy();
    }

    const withInternet = data.with_internet || {};
    const withoutInternet = data.without_internet || {};

    internetChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['With Internet', 'Without Internet'],
            datasets: [{
                label: 'Average Grade',
                data: [
                    withInternet.average_grade || 0,
                    withoutInternet.average_grade || 0
                ],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderRadius: 8
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Create teacher performance chart
function createTeacherPerformanceChart(students) {
    const ctx = document.getElementById('teacher-performance-chart');
    if (!ctx) return;

    if (teacherPerformanceChart) {
        teacherPerformanceChart.destroy();
    }

    // Calculate grade ranges
    const ranges = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '50-59': 0,
        '40-49': 0,
        '0-39': 0
    };

    students.forEach(student => {
        const grade = student.final_grade;
        if (grade >= 90) ranges['90-100']++;
        else if (grade >= 80) ranges['80-89']++;
        else if (grade >= 70) ranges['70-79']++;
        else if (grade >= 60) ranges['60-69']++;
        else if (grade >= 50) ranges['50-59']++;
        else if (grade >= 40) ranges['40-49']++;
        else ranges['0-39']++;
    });

    teacherPerformanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(ranges),
            datasets: [{
                label: 'Number of Students',
                data: Object.values(ranges),
                backgroundColor: 'rgba(124, 58, 237, 0.8)',
                borderRadius: 8
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Destroy all charts
function destroyAllCharts() {
    if (performanceChart) performanceChart.destroy();
    if (genderChart) genderChart.destroy();
    if (supportChart) supportChart.destroy();
    if (internetChart) internetChart.destroy();
    if (teacherPerformanceChart) teacherPerformanceChart.destroy();
}

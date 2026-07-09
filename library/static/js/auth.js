function isAuthenticated() {
    return !!sessionStorage.getItem('access_token');
}

function getUserRole() {
    return sessionStorage.getItem('user_role');
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/';
    }
}

function requireRole(role) {
    if (getUserRole() !== role) {
        // Redirect to their respective home page if trying to access unauthorized area
        if (getUserRole() === 'admin') {
            window.location.href = '/admin-dashboard/';
        } else if (getUserRole() === 'student') {
            window.location.href = '/books/';
        } else {
            window.location.href = '/';
        }
    }
}

function handleLogout() {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_role');
    window.location.href = '/';
}

// Attach logout listener when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }
});

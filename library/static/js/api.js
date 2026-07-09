const API_BASE_URL = '/api/';

// Global Loader Management
function showLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) loader.classList.add('active');
}

function hideLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) loader.classList.remove('active');
}

// Global Toast Management
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    // Add icon based on type
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = `<svg style="width:20px;height:20px;fill:var(--success);margin-right:8px;" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>`;
    } else if (type === 'error') {
        iconSvg = `<svg style="width:20px;height:20px;fill:var(--danger);margin-right:8px;" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>`;
    } else {
        iconSvg = `<svg style="width:20px;height:20px;fill:var(--warning);margin-right:8px;" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>`;
    }

    toast.innerHTML = `
        <div style="display:flex;align-items:center;">
            ${iconSvg}
            <span style="font-weight:500;">${message}</span>
        </div>
    `;

    container.appendChild(toast);

    // Auto remove after 3s
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 300);
    }, 3000);
}

// Wrapper to include Loader naturally
async function fetchAPI(endpoint, options = {}, silent = false) {
    if (!silent) showLoader();

    const token = sessionStorage.getItem('access_token');

    let headers = {
        ...options.headers
    };

    // Only set Content-Type to JSON if it's not a FormData object
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Check if we have a refresh token
            const refresh = sessionStorage.getItem('refresh_token');
            if (refresh) {
                // Try to refresh
                const refreshResp = await fetch(`${API_BASE_URL}token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh })
                });

                if (refreshResp.ok) {
                    const data = await refreshResp.json();
                    sessionStorage.setItem('access_token', data.access);
                    headers['Authorization'] = `Bearer ${data.access}`;

                    // Retry original request
                    const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
                        ...options,
                        headers
                    });
                    if (!silent) hideLoader();
                    return await handleResponse(retryResponse);
                }
            }

            // If we get here, refresh failed or doesn't exist
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('refresh_token');
            sessionStorage.removeItem('user_role');
            window.location.href = '/';
            if (!silent) hideLoader();
            throw new Error('Unauthorized');
        }

        if (!silent) hideLoader();
        return await handleResponse(response);
    } catch (error) {
        if (!silent) hideLoader();
        throw error;
    }
}

async function handleResponse(response) {
    if (response.status === 204) {
        return null;
    }
    const data = await response.json();
    if (!response.ok) {
        throw { status: response.status, data };
    }
    return data;
}

// Function to fetch and determine user role
async function checkAndStoreUserRole() {
    try {
        await fetchAPI('admin-dashboard/stats/', {}, true);
        sessionStorage.setItem('user_role', 'admin');
        return 'admin';
    } catch (error) {
        if (error.status === 403) {
            sessionStorage.setItem('user_role', 'student');
            return 'student';
        }
        throw error;
    }
}

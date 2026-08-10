/**
 * Course Registration System — API Helper
 * 
 * Centralised fetch wrapper used by every page.
 * Handles JSON requests, session checks, errors, and toasts.
 */

const API_BASE = '';  // Same origin — Flask serves both frontend and API

// ============================================================
// CORE FETCH WRAPPER
// ============================================================

/**
 * Make an API call with automatic error handling.
 * 
 * @param {string} endpoint - API path e.g. '/auth/login'
 * @param {object} options - { method, body, headers }
 * @returns {Promise<object>} - parsed JSON response
 */
async function apiRequest(endpoint, options = {}) {
    const config = {
        method: options.method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'include'  // Send session cookies
    };

    if (options.body && config.method !== 'GET') {
        config.body = JSON.stringify(options.body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);

        // --- Safely parse the response body ---
        // We MUST check Content-Type before calling .json().
        // Flask's built-in 404/405/500 error pages return HTML,
        // and calling .json() on HTML throws the cryptic
        // "Unexpected token '<'" SyntaxError.
        const contentType = response.headers.get('content-type') || '';
        let data = null;

        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            // Server returned HTML (e.g. Flask 404/500 error page,
            // or the server is not running at all).
            const text = await response.text();
            // Build a plain error — never expose raw HTML to the user.
            throw {
                status: response.status,
                message: _httpStatusMessage(response.status),
                raw: text
            };
        }

        if (!response.ok) {
            // Flask returned JSON with an error — surface the message.
            throw {
                status: response.status,
                message: data.message || _httpStatusMessage(response.status),
                data: data
            };
        }

        return data;

    } catch (error) {
        // Only redirect on 401 when we're on a protected page.
        if (error.status === 401) {
            if (!window.location.pathname.includes('login') &&
                !window.location.pathname.includes('register') &&
                !window.location.pathname.includes('forgot') &&
                window.location.pathname !== '/') {
                showToast('Session expired. Please log in again.', 'error');
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 1500);
            }
        }
        throw error;
    }
}

/**
 * Return a human-readable message for common HTTP status codes.
 * Used when the server returns a non-JSON body.
 */
function _httpStatusMessage(status) {
    const messages = {
        400: 'Bad request. Please check your input.',
        401: 'Authentication required. Please log in.',
        403: 'You do not have permission to do that.',
        404: 'The requested resource was not found.',
        405: 'Request method not allowed.',
        409: 'Conflict — this record may already exist.',
        422: 'Unprocessable data. Please check your input.',
        429: 'Too many requests. Please slow down.',
        500: 'Server error. Please try again later.',
        502: 'Server is unreachable. Is Flask running?',
        503: 'Service unavailable. Please try again later.',
    };
    return messages[status] || `Unexpected error (HTTP ${status}).`;
}

/**
 * Upload a file (multipart/form-data).
 */
async function apiUpload(endpoint, formData) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) throw { status: response.status, message: data.message, data };
        return data;
    } catch (error) {
        throw error;
    }
}

/**
 * Download a file (PDF, Excel).
 */
async function apiDownload(endpoint, filename) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            credentials: 'include'
        });
        if (!response.ok) throw new Error('Download failed');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showToast('Download failed.', 'error');
    }
}


// ============================================================
// SHORTHAND METHODS
// ============================================================
const api = {
    get: (endpoint) => apiRequest(endpoint),
    post: (endpoint, body) => apiRequest(endpoint, { method: 'POST', body }),
    put: (endpoint, body) => apiRequest(endpoint, { method: 'PUT', body }),
    delete: (endpoint) => apiRequest(endpoint, { method: 'DELETE' }),
    upload: apiUpload,
    download: apiDownload
};


// ============================================================
// SESSION MANAGEMENT
// ============================================================

/**
 * Check if user is logged in and return user data.
 */
async function checkAuth() {
    try {
        const data = await api.get('/auth/me');
        return data.logged_in ? data.user : null;
    } catch {
        return null;
    }
}

/**
 * Redirect to login if not authenticated.
 * role can be a string ('admin') or array (['admin','registrar']).
 * - 'admin' pages also allow 'registrar'
 * - 'student' pages also allow 'lecturer' (read-only portal access)
 * Call at the top of every protected page.
 */
async function requireAuth(role = null) {
    const user = await checkAuth();
    if (!user) {
        window.location.href = '/login.html';
        return null;
    }
    if (role) {
        const allowedRoles = Array.isArray(role) ? role : [role];
        // Admin pages also allow registrar
        if (allowedRoles.includes('admin') && !allowedRoles.includes('registrar')) {
            allowedRoles.push('registrar');
        }
        // Student portal also allows lecturer (same read-only views)
        if (allowedRoles.includes('student') && !allowedRoles.includes('lecturer')) {
            allowedRoles.push('lecturer');
        }
        if (!allowedRoles.includes(user.role)) {
            window.location.href = isAdminRole(user.role)
                ? '/admin/dashboard.html'
                : '/student/dashboard.html';
            return null;
        }
    }
    return user;
}

/** Check if a role belongs to the admin side */
function isAdminRole(role) {
    return role === 'admin' || role === 'registrar';
}

/**
 * Redirect away from login page if already logged in.
 */
async function redirectIfLoggedIn() {
    const user = await checkAuth();
    if (user) {
        window.location.href = isAdminRole(user.role)
            ? '/admin/dashboard.html'
            : '/student/dashboard.html';
    }
}

/**
 * Logout and redirect.
 */
async function logout() {
    try {
        await api.post('/auth/logout');
    } catch (e) { /* ignore */ }
    window.location.href = '/login.html';
}


// ============================================================
// TOAST NOTIFICATIONS
// ============================================================

/**
 * Show a toast notification.
 * @param {string} message
 * @param {'success'|'error'|'warning'|'info'} type
 * @param {number} duration - ms before auto-dismiss (default 4000)
 */
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };

    const toast = document.createElement('div');
    toast.className = `toast-custom toast-${type}`;
    toast.innerHTML = `<i class="bi ${icons[type]}"></i> ${message}`;

    toast.addEventListener('click', () => dismissToast(toast));
    container.appendChild(toast);

    setTimeout(() => dismissToast(toast), duration);
}

function dismissToast(toast) {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
}


// ============================================================
// UI HELPERS
// ============================================================

/**
 * Show a loading spinner inside a container.
 */
function showLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) {
        el.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <span>Loading...</span>
            </div>
        `;
    }
}

/**
 * Show an empty state message inside a container.
 */
function showEmpty(containerId, icon, title, message) {
    const el = document.getElementById(containerId);
    if (el) {
        el.innerHTML = `
            <div class="empty-state">
                <i class="bi ${icon}"></i>
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
        `;
    }
}

/**
 * Get initials from a name (for avatar).
 */
function getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

/**
 * Format a date string nicely.
 */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric'
    });
}

/**
 * Get status badge HTML.
 */
function statusBadge(status) {
    const map = {
        approved: '<span class="badge-status badge-approved"><i class="bi bi-check-circle"></i> Approved</span>',
        pending: '<span class="badge-status badge-pending"><i class="bi bi-clock"></i> Pending</span>',
        rejected: '<span class="badge-status badge-rejected"><i class="bi bi-x-circle"></i> Rejected</span>',
        dropped: '<span class="badge-status badge-dropped"><i class="bi bi-dash-circle"></i> Dropped</span>'
    };
    return map[status] || `<span class="badge-status badge-pending">${status}</span>`;
}


// ============================================================
// SIDEBAR TOGGLE (Mobile)
// ============================================================
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    sidebar?.classList.toggle('show');
    overlay?.classList.toggle('show');
}

// Close sidebar when overlay clicked
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('sidebar-overlay')) {
        toggleSidebar();
    }
});


// ============================================================
// POPULATE USER INFO IN NAVBAR
// ============================================================
function populateNavbar(user) {
    const nameEl  = document.getElementById('navbar-user-name');
    const roleEl  = document.getElementById('navbar-user-role');
    const avatarEl = document.getElementById('navbar-avatar');

    const name = user.student_name || user.admin_name || user.lecturer_name || user.name || 'User';

    const roleLabel = {
        student:   'Student',
        admin:     'Administrator',
        registrar: 'Registrar',
        lecturer:  'Lecturer'
    }[user.role] || 'User';

    if (nameEl)   nameEl.textContent   = name;
    if (roleEl)   roleEl.textContent   = roleLabel;
    if (avatarEl) avatarEl.textContent = getInitials(name);
}

/**
 * Populate navbar for admin/registrar pages.
 * Shared across all 10 admin HTML pages — defined once here.
 */
function populateAdminNavbar(user) {
    const name = user.admin_name || user.name || 'Admin';
    const nameEl  = document.getElementById('navbar-user-name');
    const roleEl  = document.getElementById('navbar-user-role');
    const avatarEl = document.getElementById('navbar-avatar');
    if (nameEl)   nameEl.textContent  = name;
    if (roleEl)   roleEl.textContent  = user.role === 'registrar' ? 'Registrar' : 'Administrator';
    if (avatarEl) avatarEl.textContent = getInitials(name);

    // Fetch and display pending approvals badge
    api.get('/admin/pending-approvals-count')
        .then(data => {
            const count = data.applications_count !== undefined ? data.applications_count : data.count;
            if (data && count > 0) {
                const appLink = document.querySelector('a[href="/admin/applications.html"]') || document.querySelector('a[href="/admin/registrations.html"]');
                if (appLink) {
                    const badge = document.createElement('span');
                    badge.style.cssText = 'background:var(--danger);color:white;padding:2px 8px;border-radius:12px;font-size:11px;margin-left:auto;font-weight:600;display:inline-block;';
                    badge.textContent = count;
                    appLink.style.display = 'flex';
                    appLink.style.alignItems = 'center';
                    
                    // Don't add multiple badges if called multiple times
                    if (!appLink.querySelector('span')) {
                        appLink.appendChild(badge);
                    }
                }
            }
        })
        .catch(() => {});
}


// ============================================================
// UPPERCASE API OBJECT (For backwards compatibility)
// ============================================================

/**
 * Uppercase API object with all methods needed by frontend pages.
 * This provides backwards compatibility for pages using API.method()
 */
const API = {
    // Core HTTP methods
    get: (endpoint) => api.get(endpoint),
    post: (endpoint, body) => api.post(endpoint, body),
    put: (endpoint, body) => api.put(endpoint, body),
    delete: (endpoint) => api.delete(endpoint),
    upload: (endpoint, formData) => api.upload(endpoint, formData),
    download: (endpoint, filename) => api.download(endpoint, filename),
    
    // Auth methods
    logout: logout,
    checkAuth: checkAuth,
    requireAuth: requireAuth,
    
    // UI helper methods
    showLoading: showLoading,
    showEmpty: showEmpty,
    formatDate: formatDate,
    getInitials: getInitials,
    getStatusBadge: statusBadge,
    statusBadge: statusBadge,
    
    // Toast notifications
    showSuccess: (message) => showToast(message, 'success'),
    showError: (message) => showToast(message, 'error'),
    showWarning: (message) => showToast(message, 'warning'),
    showInfo: (message) => showToast(message, 'info'),
    showToast: showToast,
    
    // Student Dashboard specific endpoint
    getStudentDashboard: async () => {
        return await api.get('/student/dashboard');
    },
    
    // Units/Courses endpoints
    getAvailableUnits: async () => {
        return await api.get('/registration/units');
    },
    
    getMyUnits: async () => {
        return await api.get('/registration/my-units');
    },
    
    registerForUnits: async (unitIds) => {
        return await api.post('/registration/register', { unit_ids: unitIds });
    },
    
    dropUnit: async (registrationId) => {
        return await api.delete(`/registration/drop/${registrationId}`);
    },
    
    // Navigation helpers
    populateNavbar: populateNavbar,
    populateAdminNavbar: populateAdminNavbar
};

/**
 * Show an error state inside a container with retry button.
 */
function showError(containerId, icon, title, message) {
    const el = document.getElementById(containerId);
    if (el) {
        el.innerHTML = `
            <div class="empty-state">
                <i class="bi ${icon}" style="color:var(--danger);"></i>
                <h4 style="color:var(--danger);">${title}</h4>
                <p>${message}</p>
            </div>
        `;
    }
}

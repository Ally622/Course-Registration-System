/**
 * layout.js — Shared Header & Footer builder
 *
 * Call buildHeader(config) and buildFooter() from any page.
 * The header auto-detects auth state and shows the right nav.
 *
 * Usage on a public page (landing / login / register):
 *   buildPublicHeader();
 *   buildFooter();
 *
 * Usage on a protected page (student / admin):
 *   Already has its own sidebar — just call buildFooter()
 *   if you want a footer inside main-content.
 */

// ============================================================
// LOGO SVG (inline — no extra HTTP request, recolored to system theme)
// ============================================================
const LOGO_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" fill="none" role="img" aria-label="Course Reg Logo">
  <!-- Open Book base -->
  <path d="M20 130 Q100 110 180 130 L180 160 Q100 140 20 160 Z" fill="#1A1A2E"/>
  <path d="M100 110 L100 165" stroke="#C2185B" stroke-width="3"/>
  <path d="M20 130 L20 100 Q60 85 100 90 L100 120 Q60 115 20 130Z" fill="#1A1A2E" opacity="0.85"/>
  <path d="M180 130 L180 100 Q140 85 100 90 L100 120 Q140 115 180 130Z" fill="#1A1A2E" opacity="0.85"/>
  <!-- Clipboard -->
  <rect x="68" y="50" width="64" height="82" rx="5" fill="white" stroke="#1A1A2E" stroke-width="3"/>
  <rect x="84" y="44" width="32" height="14" rx="7" fill="#1A1A2E"/>
  <rect x="88" y="46" width="24" height="10" rx="5" fill="#C2185B"/>
  <!-- Checklist rows -->
  <path d="M78 72 L82 76 L88 68" stroke="#C2185B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="92" y="70" width="28" height="4" rx="2" fill="#1A1A2E" opacity="0.3"/>
  <path d="M78 84 L82 88 L88 80" stroke="#C2185B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="92" y="82" width="28" height="4" rx="2" fill="#1A1A2E" opacity="0.3"/>
  <path d="M78 96 L82 100 L88 92" stroke="#C2185B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="92" y="94" width="28" height="4" rx="2" fill="#1A1A2E" opacity="0.3"/>
  <path d="M78 108 L82 112 L88 104" stroke="#C2185B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="92" y="106" width="16" height="4" rx="2" fill="#1A1A2E" opacity="0.3"/>
  <!-- Student avatar -->
  <circle cx="120" cy="116" r="12" fill="#C2185B"/>
  <circle cx="120" cy="112" r="5" fill="white"/>
  <path d="M110 124 Q120 118 130 124" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
  <!-- Graduation cap -->
  <rect x="72" y="36" width="56" height="8" rx="2" fill="#1A1A2E"/>
  <polygon points="100,18 60,36 140,36" fill="#1A1A2E"/>
  <line x1="140" y1="36" x2="148" y2="54" stroke="#C2185B" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="148" cy="56" r="3" fill="#C2185B"/>
</svg>`;

// ============================================================
// PUBLIC HEADER  (landing / login / register)
// ============================================================
function buildPublicHeader(activePage = '') {
    const links = [
        { href: '/',               label: 'Home' },
        { href: '/schools.html',   label: 'Schools' },
        { href: '/login.html',     label: 'Login' },
        { href: '/register.html',  label: 'Register' },
    ];

    const navLinks = links.map(l => `
        <a href="${l.href}" class="${activePage === l.label ? 'active' : ''}">${l.label}</a>
    `).join('');

    const html = `
    <header class="site-header" id="site-header">
        <div class="site-header-inner">
            <!-- Logo -->
            <a href="/" class="brand-logo" aria-label="Course Registration System home">
                <div class="brand-logo-img">${LOGO_SVG}</div>
                <div class="brand-logo-text">
                    <span class="brand-name">COURSE <span>REG</span></span>
                    <span class="brand-tagline">Register · Manage · Succeed</span>
                </div>
            </a>

            <!-- Desktop nav -->
            <nav class="site-nav" aria-label="Main navigation">${navLinks}</nav>

            <!-- Actions -->
            <div class="site-header-actions">
                <a href="/login.html" class="btn-primary-custom btn-sm-custom" style="text-decoration:none;">
                    <i class="bi bi-box-arrow-in-right"></i> Login
                </a>
                <!-- Hamburger -->
                <button class="hamburger" id="hamburger-btn" aria-label="Toggle menu" aria-expanded="false">
                    <span></span><span></span><span></span>
                </button>
            </div>
        </div>
        <!-- Mobile nav -->
        <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile navigation">
            ${links.map(l => `<a href="${l.href}">${l.label}</a>`).join('')}
            <a href="/login.html" style="color:var(--primary-light);font-weight:600;">
                <i class="bi bi-box-arrow-in-right"></i> Login
            </a>
        </nav>
    </header>`;

    document.body.insertAdjacentHTML('afterbegin', html);
    _initHamburger();
}

// ============================================================
// AUTHENTICATED HEADER  (shown on student / admin pages if needed)
// Typically the sidebar replaces this, but it's here for flexibility
// ============================================================
async function buildAuthHeader() {
    const user = await checkAuth();
    if (!user) return;

    const name = user.name || user.student_name || user.admin_name || 'User';
    const initials = getInitials(name);
    const roleLabel = { student: 'Student', admin: 'Administrator', registrar: 'Registrar', lecturer: 'Lecturer' }[user.role] || 'User';
    const dashboardHref = (user.role === 'admin' || user.role === 'registrar')
        ? '/admin/dashboard.html' : '/student/dashboard.html';

    const html = `
    <header class="site-header" id="site-header">
        <div class="site-header-inner">
            <a href="${dashboardHref}" class="brand-logo">
                <div class="brand-logo-img">${LOGO_SVG}</div>
                <div class="brand-logo-text">
                    <span class="brand-name">COURSE <span>REG</span></span>
                    <span class="brand-tagline">Register · Manage · Succeed</span>
                </div>
            </a>

            <div class="site-header-actions">
                <!-- Notification bell -->
                <div class="header-notif" id="header-notif-bell" title="Notifications"
                     onclick="window.location.href='/student/notifications.html'" role="button" tabindex="0">
                    <i class="bi bi-bell"></i>
                    <span class="notif-badge" id="header-notif-dot" style="display:none;"></span>
                </div>

                <!-- Profile dropdown -->
                <div class="header-profile" id="header-profile">
                    <button class="header-profile-btn" aria-haspopup="true" aria-expanded="false"
                            onclick="document.getElementById('header-profile').classList.toggle('open')">
                        <div class="header-avatar" id="header-avatar">${initials}</div>
                        <span class="header-profile-name">${name}</span>
                        <i class="bi bi-chevron-down" style="font-size:11px;opacity:0.7;"></i>
                    </button>
                    <div class="header-dropdown" role="menu">
                        <div style="padding:12px 16px 8px;border-bottom:1px solid #f0f0f0;">
                            <div style="font-weight:700;font-size:13px;">${name}</div>
                            <div style="font-size:11px;color:var(--text-muted);">${roleLabel}</div>
                        </div>
                        <a href="${dashboardHref}" role="menuitem">
                            <i class="bi bi-grid-1x2"></i> Dashboard
                        </a>
                        <a href="/student/profile.html" role="menuitem">
                            <i class="bi bi-person-circle"></i> My Profile
                        </a>
                        <div class="dropdown-divider"></div>
                        <button class="dropdown-logout" onclick="logout()" role="menuitem">
                            <i class="bi bi-box-arrow-left"></i> Logout
                        </button>
                    </div>
                </div>

                <button class="hamburger" id="hamburger-btn" aria-label="Toggle menu">
                    <span></span><span></span><span></span>
                </button>
            </div>
        </div>
    </header>`;

    document.body.insertAdjacentHTML('afterbegin', html);
    _initHamburger();
    _initClickOutsideDropdown();
}

// ============================================================
// FOOTER — Compact single-bar version
// ============================================================
function buildFooter() {
    const html = `
    <footer class="site-footer-compact" role="contentinfo">
        <div class="site-footer-compact-inner">
            <span class="footer-compact-brand">
                &copy; 2026 <strong>Course Reg System</strong>
            </span>
            <nav class="footer-compact-links" aria-label="Footer links">
                <a href="/">Home</a>
                <a href="/student/dashboard.html">Dashboard</a>
                <a href="/student/results.html">Results</a>
                <a href="/admin/dashboard.html">Admin</a>
            </nav>
            <span class="footer-compact-contact">
                <i class="bi bi-envelope"></i> registrar@university.ac.ke
            </span>
        </div>
    </footer>`;

    document.body.insertAdjacentHTML('beforeend', html);
}

// ============================================================
// SIDEBAR BRAND UPGRADE
// Replaces the emoji 🎓 brand icon with the SVG logo on
// any authenticated page that calls this after DOM load.
// ============================================================
function upgradeSidebarBrand() {
    const icon = document.querySelector('.sidebar-brand-icon');
    if (icon) {
        icon.innerHTML = LOGO_SVG;
        icon.style.background = 'none';
        icon.style.padding = '0';
        icon.style.width = '38px';
        icon.style.height = '38px';
    }
}

// ============================================================
// INTERNAL HELPERS
// ============================================================
function _initHamburger() {
    const btn = document.getElementById('hamburger-btn');
    const nav = document.getElementById('mobile-nav'); // For public pages
    const sidebar = document.querySelector('.sidebar'); // For auth pages
    const overlay = document.querySelector('.sidebar-overlay');

    if (!btn) return;
    
    btn.addEventListener('click', () => {
        const isOpen = btn.classList.toggle('open');
        btn.setAttribute('aria-expanded', isOpen);
        
        if (nav) {
            nav.classList.toggle('open', isOpen);
        }
        
        if (sidebar) {
            sidebar.classList.toggle('show', isOpen);
            if (overlay) {
                overlay.classList.toggle('show', isOpen);
            }
        }
    });
}

function _initClickOutsideDropdown() {
    document.addEventListener('click', (e) => {
        const profile = document.getElementById('header-profile');
        if (profile && !profile.contains(e.target)) {
            profile.classList.remove('open');
        }
    });
}


// ============================================================
// SIDEBAR TOGGLE
// ============================================================
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
    if (overlay) {
        overlay.classList.toggle('show');
    }
}

// Close sidebar when clicking overlay
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', () => {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.remove('show');
            }
            overlay.classList.remove('show');
        });
    }
});

// ============================================================
// NAVBAR POPULATION
// ============================================================
function populateNavbar(user) {
    if (!user) return;
    
    const name = user.name || user.student_name || user.admin_name || user.lecturer_name || 'User';
    const initials = getInitials(name);
    
    // Update navbar user name
    const nameEl = document.getElementById('navbar-user-name');
    if (nameEl) nameEl.textContent = name;
    
    // Update navbar avatar
    const avatarEl = document.getElementById('navbar-avatar');
    if (avatarEl) avatarEl.textContent = initials;
    
    // Update notification count (optional - if you have a notifications endpoint)
    // const notifCountEl = document.getElementById('notif-count');
    // if (notifCountEl) {
    //     // Fetch and display notification count
    // }
}

// Helper to get initials from name
function getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

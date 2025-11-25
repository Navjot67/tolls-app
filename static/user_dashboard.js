/**
 * User Dashboard JavaScript
 * Handles authentication and displays user account data
 */

// State management
let authToken = localStorage.getItem('authToken');
let userData = null;

// DOM Elements
const authSection = document.getElementById('authSection');
const dashboardSection = document.getElementById('dashboardSection');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const otpForm = document.getElementById('otpForm');
const loginFormElement = document.getElementById('loginFormElement');
const signupFormElement = document.getElementById('signupFormElement');
const otpFormElement = document.getElementById('otpFormElement');
const showSignupLink = document.getElementById('showSignup');
const showLoginLink = document.getElementById('showLogin');
const authMessage = document.getElementById('authMessage');
const logoutBtn = document.getElementById('logoutBtn');
const refreshBtn = document.getElementById('refreshBtn');
const accountsList = document.getElementById('accountsList');
const accountsDisplay = document.getElementById('accountsDisplay');
const loadingState = document.getElementById('loadingState');
const noAccountsMessage = document.getElementById('noAccountsMessage');
const userWelcome = document.getElementById('userWelcome');
const otpEmailDisplay = document.getElementById('otpEmailDisplay');
const resendOtpLink = document.getElementById('resendOtpLink');
const backToSignupLink = document.getElementById('backToSignup');

// Store pending email for OTP verification
let pendingEmail = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    if (authToken) {
        checkAuthAndLoadData();
    } else {
        showAuthSection();
    }

    // Form event listeners
    loginFormElement.addEventListener('submit', handleLogin);
    signupFormElement.addEventListener('submit', handleSignup);
    if (otpFormElement) {
        otpFormElement.addEventListener('submit', handleOtpVerification);
    }
    showSignupLink.addEventListener('click', (e) => {
        e.preventDefault();
        showSignup();
    });
    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        showLogin();
    });
    if (resendOtpLink) {
        resendOtpLink.addEventListener('click', (e) => {
            e.preventDefault();
            handleResendOtp();
        });
    }
    if (backToSignupLink) {
        backToSignupLink.addEventListener('click', (e) => {
            e.preventDefault();
            showSignup();
        });
    }
    logoutBtn.addEventListener('click', handleLogout);
    refreshBtn.addEventListener('click', refreshUserData);
});

// Show authentication section
function showAuthSection() {
    authSection.style.display = 'flex';
    dashboardSection.style.display = 'none';
    clearAuthMessage();
}

// Show dashboard section
function showDashboard() {
    authSection.style.display = 'none';
    dashboardSection.style.display = 'block';
}

// Toggle between login and signup
function showSignup() {
    loginForm.style.display = 'none';
    signupForm.style.display = 'block';
    if (otpForm) otpForm.style.display = 'none';
    clearAuthMessage();
}

function showLogin() {
    signupForm.style.display = 'none';
    loginForm.style.display = 'block';
    if (otpForm) otpForm.style.display = 'none';
    clearAuthMessage();
}

function showOtpForm(email) {
    loginForm.style.display = 'none';
    signupForm.style.display = 'none';
    if (otpForm) {
        otpForm.style.display = 'block';
        if (otpEmailDisplay) otpEmailDisplay.textContent = email;
    }
    pendingEmail = email;
    clearAuthMessage();
}

// Display auth message
function showAuthMessage(message, type = 'error') {
    authMessage.textContent = message;
    authMessage.className = `auth-message ${type}`;
    authMessage.style.display = 'block';
}

function clearAuthMessage() {
    authMessage.style.display = 'none';
    authMessage.textContent = '';
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoader = loginBtn.querySelector('.btn-loader');
    
    if (!email || !password) {
        showAuthMessage('Please enter both email and password', 'error');
        return;
    }
    
    // Show loading state
    loginBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    clearAuthMessage();
    
    try {
        const response = await fetch('/api/user/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Save token
            authToken = data.user.token;
            localStorage.setItem('authToken', authToken);
            userData = data.user;
            
            // Show dashboard
            showDashboard();
            loadUserData();
        } else {
            // Check if email verification is required
            if (data.requires_verification) {
                const email = document.getElementById('loginEmail').value.trim();
                showAuthMessage(data.error || 'Email not verified', 'error');
                showOtpForm(email);
            } else {
                showAuthMessage(data.error || 'Login failed', 'error');
            }
        }
    } catch (error) {
        showAuthMessage('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    } finally {
        // Reset button state
        loginBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Handle signup
async function handleSignup(e) {
    e.preventDefault();
    
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const signupBtn = document.getElementById('signupBtn');
    const btnText = signupBtn.querySelector('.btn-text');
    const btnLoader = signupBtn.querySelector('.btn-loader');
    
    if (!email || !password) {
        showAuthMessage('Please enter both email and password', 'error');
        return;
    }
    
    if (password.length < 6) {
        showAuthMessage('Password must be at least 6 characters', 'error');
        return;
    }
    
    // Show loading state
    signupBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    clearAuthMessage();
    
    try {
        const response = await fetch('/api/user/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show OTP verification form
            const email = document.getElementById('signupEmail').value.trim();
            showAuthMessage('Account created! Please check your email for the verification code.', 'success');
            showOtpForm(email);
        } else {
            showAuthMessage(data.error || 'Signup failed', 'error');
        }
    } catch (error) {
        showAuthMessage('Network error. Please try again.', 'error');
        console.error('Signup error:', error);
    } finally {
        // Reset button state
        signupBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Handle logout
function handleLogout() {
    if (confirm('Are you sure you want to sign out?')) {
        authToken = null;
        userData = null;
        localStorage.removeItem('authToken');
        showAuthSection();
        showLogin();
    }
}

// Check authentication and load data
async function checkAuthAndLoadData() {
    if (!authToken) {
        showAuthSection();
        return;
    }
    
    try {
        const response = await fetch('/api/user/data', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            userData = data.user;
            showDashboard();
            displayAccounts(data.accounts);
        } else {
            // Invalid token, show auth
            authToken = null;
            localStorage.removeItem('authToken');
            showAuthSection();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        showAuthSection();
    }
}

// Load user data
async function loadUserData() {
    if (!authToken) {
        showAuthSection();
        return;
    }
    
    loadingState.style.display = 'block';
    accountsDisplay.style.display = 'none';
    
    try {
        const response = await fetch('/api/user/data', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            userData = data.user;
            updateWelcomeMessage();
            displayAccounts(data.accounts);
        } else {
            if (data.error.includes('token')) {
                // Token expired, logout
                handleLogout();
            } else {
                showError('Failed to load data: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Load data error:', error);
        showError('Network error. Please try again.');
    } finally {
        loadingState.style.display = 'none';
        accountsDisplay.style.display = 'block';
    }
}

// Refresh user data
async function refreshUserData() {
    if (!authToken) return;
    
    const refreshBtn = document.getElementById('refreshBtn');
    const originalText = refreshBtn.querySelector('.btn-text').textContent;
    
    refreshBtn.disabled = true;
    refreshBtn.querySelector('.btn-text').textContent = '🔄 Refreshing...';
    
    try {
        const response = await fetch('/api/user/refresh', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAccounts(data.accounts);
            showSuccessMessage('Data refreshed successfully!');
        } else {
            showError('Failed to refresh: ' + data.error);
        }
    } catch (error) {
        console.error('Refresh error:', error);
        showError('Network error. Please try again.');
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.querySelector('.btn-text').textContent = originalText;
    }
}

// Update welcome message
function updateWelcomeMessage() {
    if (userData) {
        const name = userData.name || userData.email.split('@')[0];
        userWelcome.textContent = `Welcome back, ${name}!`;
    }
}

// Display accounts
function displayAccounts(accounts) {
    if (!accounts || accounts.length === 0) {
        accountsList.innerHTML = '';
        noAccountsMessage.style.display = 'block';
        return;
    }
    
    noAccountsMessage.style.display = 'none';
    
    accountsList.innerHTML = accounts.map((account, index) => {
        const hasNY = account.account_number && account.plate_number;
        const hasNJ = account.violation_number || account.nj_violation_number;
        const sources = account.sources || [];
        
        // Determine badge
        let badgeClass = 'badge-ny';
        let badgeText = 'NY';
        if (hasNY && hasNJ) {
            badgeClass = 'badge-both';
            badgeText = 'NY + NJ';
        } else if (hasNJ) {
            badgeClass = 'badge-nj';
            badgeText = 'NJ';
        }
        
        // Format balances
        const nyBalance = parseFloat(account.ny_balance_amount || 0);
        const njBalance = parseFloat(account.nj_balance_amount || 0);
        const totalBalance = parseFloat(account.balance_amount || 0);
        
        return `
            <div class="account-card">
                <div class="account-header">
                    <div class="account-title">Account #${index + 1}</div>
                    <span class="account-badge ${badgeClass}">${badgeText}</span>
                </div>
                
                <div class="account-details">
                    ${hasNY ? `
                        <div class="detail-item">
                            <span class="detail-label">NY Account Number</span>
                            <span class="detail-value">${account.account_number}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">NY Plate Number</span>
                            <span class="detail-value">${account.plate_number}</span>
                        </div>
                    ` : ''}
                    ${hasNJ ? `
                        <div class="detail-item">
                            <span class="detail-label">NJ Violation Number</span>
                            <span class="detail-value">${account.violation_number || account.nj_violation_number || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">NJ Plate Number</span>
                            <span class="detail-value">${account.nj_plate_number || account.plate_number || 'N/A'}</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="balance-section">
                    ${hasNY ? `
                        <div class="balance-item">
                            <div class="balance-label">NY Balance</div>
                            <div class="balance-amount ${nyBalance > 0 ? 'positive' : 'zero'}">
                                $${nyBalance.toFixed(2)}
                            </div>
                        </div>
                    ` : ''}
                    ${hasNJ ? `
                        <div class="balance-item">
                            <div class="balance-label">NJ Balance</div>
                            <div class="balance-amount ${njBalance > 0 ? 'positive' : 'zero'}">
                                $${njBalance.toFixed(2)}
                            </div>
                        </div>
                    ` : ''}
                    <div class="balance-item total-balance">
                        <div class="balance-label">Total Balance Due</div>
                        <div class="balance-amount ${totalBalance > 0 ? 'positive' : 'zero'}">
                            $${totalBalance.toFixed(2)}
                        </div>
                    </div>
                </div>
                
                ${account.last_updated ? `
                    <div class="last-updated">
                        Last updated: ${account.last_updated}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Show success message
function showSuccessMessage(message) {
    // Create temporary success message
    const messageEl = document.createElement('div');
    messageEl.className = 'auth-message success';
    messageEl.textContent = message;
    messageEl.style.position = 'fixed';
    messageEl.style.top = '20px';
    messageEl.style.right = '20px';
    messageEl.style.zIndex = '10000';
    messageEl.style.padding = '16px 24px';
    messageEl.style.borderRadius = '8px';
    messageEl.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// Show error message
function showError(message) {
    showSuccessMessage(message); // Reuse same function, but could style differently
}

// Handle OTP verification
async function handleOtpVerification(e) {
    e.preventDefault();
    
    const otp = document.getElementById('otpCode').value.trim();
    const verifyBtn = document.getElementById('verifyOtpBtn');
    const btnText = verifyBtn.querySelector('.btn-text');
    const btnLoader = verifyBtn.querySelector('.btn-loader');
    
    if (!otp || otp.length !== 6) {
        showAuthMessage('Please enter a valid 6-digit code', 'error');
        return;
    }
    
    if (!pendingEmail) {
        showAuthMessage('Email not found. Please sign up again.', 'error');
        showSignup();
        return;
    }
    
    // Show loading state
    verifyBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    clearAuthMessage();
    
    try {
        const response = await fetch('/api/user/verify-otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: pendingEmail, otp: otp })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Save token
            authToken = data.user.token;
            localStorage.setItem('authToken', authToken);
            userData = data.user;
            
            // Show success message
            showAuthMessage('Email verified successfully! Redirecting...', 'success');
            
            // Show dashboard
            setTimeout(() => {
                showDashboard();
                loadUserData();
            }, 1000);
        } else {
            showAuthMessage(data.error || 'Invalid verification code', 'error');
        }
    } catch (error) {
        showAuthMessage('Network error. Please try again.', 'error');
        console.error('OTP verification error:', error);
    } finally {
        // Reset button state
        verifyBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Handle resend OTP
async function handleResendOtp() {
    if (!pendingEmail) {
        showAuthMessage('Email not found. Please sign up again.', 'error');
        showSignup();
        return;
    }
    
    const resendLink = document.getElementById('resendOtpLink');
    const originalText = resendLink.textContent;
    
    resendLink.style.pointerEvents = 'none';
    resendLink.textContent = 'Sending...';
    
    try {
        const response = await fetch('/api/user/resend-otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: pendingEmail })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAuthMessage('Verification code sent! Please check your email.', 'success');
        } else {
            showAuthMessage(data.error || 'Failed to resend code', 'error');
        }
    } catch (error) {
        showAuthMessage('Network error. Please try again.', 'error');
        console.error('Resend OTP error:', error);
    } finally {
        resendLink.style.pointerEvents = 'auto';
        resendLink.textContent = originalText;
    }
}


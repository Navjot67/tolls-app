// Multi-user account management
let userAccounts = [];
let userCounter = 0;

function addUserAccount() {
    userCounter++;
    const userAccount = {
        id: userCounter,
        accountNumber: '',
        plateNumber: '',
        email: ''
    };
    userAccounts.push(userAccount);
    renderUserAccounts();
}

function removeUserAccount(userId) {
    userAccounts = userAccounts.filter(u => u.id !== userId);
    renderUserAccounts();
}

function renderUserAccounts() {
    const container = document.getElementById('usersContainer');
    if (!container) return;
    
    if (userAccounts.length === 0) {
        addUserAccount(); // Add first account automatically
        return;
    }
    
    container.innerHTML = userAccounts.map(user => `
        <div class="user-account-card" data-user-id="${user.id}">
            <button type="button" class="remove-user" onclick="removeUserAccount(${user.id})" title="Remove account">×</button>
            <div class="user-account-header">Account #${user.id}</div>
            <div class="form-group">
                <label>Account Number</label>
                <input 
                    type="text" 
                    class="user-account-input" 
                    data-field="accountNumber"
                    data-user-id="${user.id}"
                    placeholder="E-ZPass account number"
                    value="${user.accountNumber}"
                >
            </div>
            <div class="form-group">
                <label>Plate Number</label>
                <input 
                    type="text" 
                    class="user-plate-input" 
                    data-field="plateNumber"
                    data-user-id="${user.id}"
                    placeholder="License plate number"
                    value="${user.plateNumber}"
                >
            </div>
            <div class="form-group">
                <label>Email Address (Optional)</label>
                <input 
                    type="email" 
                    class="user-email-input" 
                    data-field="email"
                    data-user-id="${user.id}"
                    placeholder="Email for this account"
                    value="${user.email}"
                >
            </div>
        </div>
    `).join('');
    
    // Add event listeners
    container.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            const userId = parseInt(this.dataset.userId);
            const field = this.dataset.field;
            const user = userAccounts.find(u => u.id === userId);
            if (user) {
                user[field] = this.value.trim();
            }
        });
    });
}

function validateUserAccounts() {
    return userAccounts.filter(user => {
        return user.accountNumber && user.plateNumber;
    });
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
        alert('Error: ' + message);
    }
}

function fetchAllAccounts() {
    const validAccounts = validateUserAccounts();
    
    if (validAccounts.length === 0) {
        showError('Please add at least one account with account number and plate number');
        return;
    }
    
    // Show loading
    const loadingOverlay = document.getElementById('loadingOverlay');
    const fetchBtn = document.getElementById('fetchBtn');
    const resultsSection = document.getElementById('resultsSection');
    const errorMessage = document.getElementById('errorMessage');
    
    loadingOverlay.style.display = 'flex';
    fetchBtn.disabled = true;
    errorMessage.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Clear previous results
    const resultsContainer = document.getElementById('multiResultsContainer');
    if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="processing-message">Processing accounts...</div>';
    }
    
    // Send batch request
    fetch('/api/fetch-batch-toll-info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            accounts: validAccounts.map(acc => ({
                account_number: acc.accountNumber,
                plate_number: acc.plateNumber,
                email: acc.email || ''
            }))
        })
    })
    .then(response => response.json())
    .then(data => {
        displayMultiResults(data);
        
        // Show email summary
        if (data.results) {
            const emailsSent = data.results.filter(r => r.email_sent).length;
            if (emailsSent > 0) {
                setTimeout(() => {
                    alert(`✅ ${emailsSent} email(s) sent successfully!\n\nCheck inboxes for toll information.`);
                }, 500);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    })
    .finally(() => {
        loadingOverlay.style.display = 'none';
        fetchBtn.disabled = false;
    });
}

function displayMultiResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    let resultsContainer = document.getElementById('multiResultsContainer');
    
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'multiResultsContainer';
        resultsContainer.className = 'multi-results';
        resultsSection.innerHTML = '<h2 style="margin-bottom: 20px;">Results for All Accounts</h2>';
        resultsSection.appendChild(resultsContainer);
    }
    
    if (!data.results || data.results.length === 0) {
        resultsContainer.innerHTML = '<div class="error-message">No results received</div>';
        resultsSection.style.display = 'block';
        return;
    }
    
    resultsContainer.innerHTML = data.results.map((result, index) => {
        const account = userAccounts[index] || {};
        const accountLabel = `Account ${index + 1}`;
        const balance = result.balance_amount || 0;
        const billNumbers = result.toll_bill_numbers || [];
        const violations = result.violation_count || 0;
        
        if (!result.success) {
            return `
                <div class="user-result-card">
                    <div class="user-result-header">
                        <div class="user-result-name">${accountLabel}</div>
                        <span class="user-result-status status-error">Failed</span>
                    </div>
                    <div class="error-details">
                        <p><strong>Account:</strong> ${result.account_number || 'N/A'}</p>
                        <p><strong>Plate:</strong> ${result.plate_number || 'N/A'}</p>
                        <p><strong>Error:</strong> ${result.error || 'Unknown error'}</p>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="user-result-card">
                <div class="user-result-header">
                    <div class="user-result-name">${accountLabel}</div>
                    <span class="user-result-status status-success">Success</span>
                </div>
                <div class="user-result-content">
                    <div class="info-row">
                        <span class="info-label">Account:</span>
                        <span class="info-value">${result.account_number || 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Plate:</span>
                        <span class="info-value">${result.plate_number || 'N/A'}</span>
                    </div>
                    <div class="balance-display" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center;">
                        <div style="font-size: 14px; opacity: 0.9;">Balance Due</div>
                        <div style="font-size: 32px; font-weight: 700; margin: 8px 0;">$${balance.toFixed(2)}</div>
                        <div style="font-size: 12px; opacity: 0.9;">This is what you owe to E-ZPass</div>
                    </div>
                    ${billNumbers.length > 0 ? `
                        <div class="info-row">
                            <span class="info-label">Bill Numbers:</span>
                            <span class="info-value">${billNumbers.join(', ')}</span>
                        </div>
                    ` : ''}
                    ${violations > 0 ? `
                        <div class="info-row">
                            <span class="info-label">Violations:</span>
                            <span class="info-value">${violations}</span>
                        </div>
                    ` : ''}
                    ${result.email_sent ? `
                        <div class="info-row" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
                            <span class="info-label" style="color: #10b981;">✓ Email Sent</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add first user account
    addUserAccount();
    
    // Add user button
    const addUserBtn = document.getElementById('addUserBtn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', addUserAccount);
    }
    
    // Fetch button
    const fetchBtn = document.getElementById('fetchBtn');
    if (fetchBtn) {
        fetchBtn.addEventListener('click', fetchAllAccounts);
    }
});

// Make functions globally available
window.addUserAccount = addUserAccount;
window.removeUserAccount = removeUserAccount;


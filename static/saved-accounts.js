// Saved Accounts Management for Auto-Fetch
let savedAccounts = [];

function loadSavedAccounts() {
    fetch('/api/accounts')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                savedAccounts = data.accounts || [];
                renderSavedAccounts();
            } else {
                showError('Failed to load saved accounts: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error loading saved accounts:', error);
            showError('Error loading saved accounts. Please try again.');
        });
}

function renderSavedAccounts() {
    const container = document.getElementById('savedAccountsContainer');
    if (!container) return;
    
    if (savedAccounts.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                <p>No saved accounts yet. Add accounts to enable automatic fetching every 3 hours.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = savedAccounts.map((account, index) => {
        const balance = account.balance_amount !== undefined ? parseFloat(account.balance_amount) : null;
        const balanceDisplay = balance !== null ? `$${balance.toFixed(2)}` : '--';
        const balanceClass = balance !== null && balance > 0 ? 'balance-positive' : 'balance-zero';
        const lastUpdated = account.last_updated || 'Never';
        const isLoading = account.isLoading || false;
        const source = account.source || 'NY';
        const sources = account.sources || [source];
        
        // NY account info
        const nyAccount = account.account_number || 'N/A';
        const nyPlate = account.plate_number || 'N/A';
        
        // NJ account info
        const njViolation = account.violation_number || account.nj_violation_number || null;
        const njPlate = account.nj_plate_number || account.plate_number || 'N/A';
        
        const hasNY = sources.includes('NY') && account.account_number;
        const hasNJ = sources.includes('NJ') && njViolation;
        
        return `
        <div class="saved-account-item" data-index="${index}" id="account-${index}">
            <div class="saved-account-info">
                <div class="saved-account-row">
                    <span class="saved-account-label">Account #${index + 1}:</span>
                    <span class="saved-account-value" id="account-number-${index}">
                        ${hasNY ? `NY: ${nyAccount}` : ''}
                        ${hasNY && hasNJ ? ' | ' : ''}
                        ${hasNJ ? `NJ: ${njViolation}` : ''}
                        ${!hasNY && !hasNJ ? 'N/A' : ''}
                    </span>
                </div>
                ${hasNY ? `
                    <div class="saved-account-row">
                        <span class="saved-account-label">NY Plate:</span>
                        <span class="saved-account-value" id="ny-plate-${index}">${nyPlate}</span>
                    </div>
                ` : ''}
                ${hasNJ ? `
                    <div class="saved-account-row">
                        <span class="saved-account-label">NJ Violation:</span>
                        <span class="saved-account-value" id="nj-violation-${index}">${njViolation}</span>
                    </div>
                    <div class="saved-account-row">
                        <span class="saved-account-label">NJ Plate:</span>
                        <span class="saved-account-value" id="nj-plate-${index}">${njPlate}</span>
                    </div>
                ` : ''}
                ${account.email ? `
                    <div class="saved-account-row">
                        <span class="saved-account-label">Email:</span>
                        <span class="saved-account-value" id="email-${index}">${account.email}</span>
                    </div>
                ` : `
                    <div class="saved-account-row">
                        <span class="saved-account-label">Email:</span>
                        <span class="saved-account-value" id="email-${index}" style="color: var(--text-secondary); font-style: italic;">Not set</span>
                    </div>
                `}
                ${hasNY ? `
                    <div class="saved-account-row">
                        <span class="saved-account-label">NY Balance:</span>
                        <span class="saved-account-value ${(account.ny_balance_amount !== undefined && account.ny_balance_amount > 0) ? 'balance-positive' : 'balance-zero'}" id="ny-balance-${index}">
                            ${isLoading ? '<span class="loading-spinner">⏳</span> Loading...' : (account.ny_balance_amount !== undefined ? `$${parseFloat(account.ny_balance_amount).toFixed(2)}` : '--')}
                        </span>
                    </div>
                ` : ''}
                ${hasNJ ? `
                    <div class="saved-account-row">
                        <span class="saved-account-label">NJ Balance:</span>
                        <span class="saved-account-value ${(account.nj_balance_amount !== undefined && account.nj_balance_amount > 0) ? 'balance-positive' : 'balance-zero'}" id="nj-balance-${index}">
                            ${isLoading ? '<span class="loading-spinner">⏳</span> Loading...' : (account.nj_balance_amount !== undefined ? `$${parseFloat(account.nj_balance_amount).toFixed(2)}` : '--')}
                        </span>
                    </div>
                ` : ''}
                <div class="saved-account-row">
                    <span class="saved-account-label">Total Balance:</span>
                    <span class="saved-account-value ${balanceClass}" id="balance-${index}">
                        ${isLoading ? '<span class="loading-spinner">⏳</span> Loading...' : balanceDisplay}
                    </span>
                </div>
                <div class="saved-account-row">
                    <span class="saved-account-label">Last Updated:</span>
                    <span class="saved-account-value" id="last-updated-${index}" style="font-size: 0.85rem; color: var(--text-secondary);">${lastUpdated}</span>
                </div>
            </div>
            <div class="saved-account-actions">
                <button type="button" class="btn-refresh-saved" onclick="refreshAccountData(${index})" title="Refresh balance" id="refresh-btn-${index}">
                    ${isLoading ? '⏳' : '🔄'}
                </button>
                <button type="button" class="btn-edit-saved" onclick="editSavedAccount(${index})" title="Edit account">
                    ✏️
                </button>
                <button type="button" class="btn-remove-saved" onclick="removeSavedAccount(${index})" title="Remove account">
                    🗑️
                </button>
            </div>
        </div>
    `;
    }).join('');
}

function addSavedAccount() {
    // NY Account
    const accountNumber = prompt('Enter NY Account Number:');
    if (!accountNumber || !accountNumber.trim()) return;
    
    const plateNumber = prompt('Enter Plate Number:');
    if (!plateNumber || !plateNumber.trim()) return;
    
    const email = prompt('Enter Email Address (optional, press Cancel to skip):');
    
    const newAccount = {
        source: 'NY',
        sources: ['NY'],
        account_number: accountNumber.trim(),
        plate_number: plateNumber.trim(),
        email: email ? email.trim() : ''
    };
    
    savedAccounts.push(newAccount);
    saveAccountsToServer();
}

function addNJAccount() {
    // NJ Violation
    const violationNumber = prompt('Enter NJ Violation Number:');
    if (!violationNumber || !violationNumber.trim()) return;
    
    const plateNumber = prompt('Enter Plate Number:');
    if (!plateNumber || !plateNumber.trim()) return;
    
    const email = prompt('Enter Email Address (optional, press Cancel to skip):');
    
    const newAccount = {
        source: 'NJ',
        sources: ['NJ'],
        violation_number: violationNumber.trim(),
        plate_number: plateNumber.trim(),
        nj_plate_number: plateNumber.trim()
    };
    
    // Only add email if provided
    if (email && email.trim()) {
        newAccount.email = email.trim();
    }
    
    savedAccounts.push(newAccount);
    saveAccountsToServer();
}

function editSavedAccount(index) {
    if (index < 0 || index >= savedAccounts.length) return;
    
    const account = savedAccounts[index];
    
    // Create edit form
    const accountItem = document.getElementById(`account-${index}`);
    if (!accountItem) return;
    
    // Check if already in edit mode
    if (accountItem.querySelector('.edit-form')) {
        return; // Already editing
    }
    
    // Store original values
    const sources = account.sources || [account.source || 'NY'];
    const originalAccountNumber = account.account_number || '';
    const originalPlateNumber = account.plate_number || '';
    const originalViolationNumber = account.violation_number || account.nj_violation_number || '';
    const originalNJPlate = account.nj_plate_number || account.plate_number || '';
    const originalEmail = account.email || '';
    const hasNY = sources.includes('NY');
    const hasNJ = sources.includes('NJ');
    
    // Create edit form HTML - always show both NY and NJ sections
    let editFormHTML = `
        <div class="edit-form" style="margin-top: 15px; padding: 15px; background: var(--bg-color); border-radius: 8px; border: 2px solid var(--primary-color);">
            <div style="margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--border-color);">
                <strong style="color: var(--primary-color);">NY E-ZPass Account</strong>
            </div>
            <div style="margin-bottom: 10px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: var(--text-primary);">NY Account Number:</label>
                <input type="text" 
                       id="edit-account-number-${index}" 
                       value="${originalAccountNumber}" 
                       style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.95rem;"
                       placeholder="Enter NY account number (optional)">
            </div>
            <div style="margin-bottom: 10px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: var(--text-primary);">NY Plate Number:</label>
                <input type="text" 
                       id="edit-plate-number-${index}" 
                       value="${originalPlateNumber}" 
                       style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.95rem;"
                       placeholder="Enter NY plate number (optional)">
            </div>
            <div style="margin-bottom: 10px; padding-top: 10px; padding-bottom: 10px; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color);">
                <strong style="color: var(--secondary-color);">NJ E-ZPass Violation</strong>
            </div>
            <div style="margin-bottom: 10px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: var(--text-primary);">NJ Violation Number:</label>
                <input type="text" 
                       id="edit-violation-number-${index}" 
                       value="${originalViolationNumber}" 
                       style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.95rem;"
                       placeholder="Enter NJ violation number (optional)">
            </div>
            <div style="margin-bottom: 10px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: var(--text-primary);">NJ Plate Number:</label>
                <input type="text" 
                       id="edit-nj-plate-number-${index}" 
                       value="${originalNJPlate}" 
                       style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.95rem;"
                       placeholder="Enter NJ plate number (optional)">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: var(--text-primary);">Email (optional):</label>
                <input type="email" 
                       id="edit-email-${index}" 
                       value="${originalEmail}" 
                       style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.95rem;"
                       placeholder="Enter email address">
            </div>
            <div style="display: flex; gap: 10px;">
                <button type="button" 
                        class="btn-primary" 
                        onclick="saveEditedAccount(${index})" 
                        style="flex: 1; padding: 8px 16px; font-size: 0.9rem;">
                    💾 Save
                </button>
                <button type="button" 
                        class="btn-secondary" 
                        onclick="cancelEditAccount(${index})" 
                        style="flex: 1; padding: 8px 16px; font-size: 0.9rem;">
                    ❌ Cancel
                </button>
            </div>
        </div>
    `;
    
    // Insert edit form after account info
    const accountInfo = accountItem.querySelector('.saved-account-info');
    if (accountInfo) {
        accountInfo.insertAdjacentHTML('afterend', editFormHTML);
        
        // Focus on first non-empty input, or first input if all empty
        setTimeout(() => {
            let firstInput = document.getElementById(`edit-account-number-${index}`);
            if (!firstInput || !firstInput.value) {
                firstInput = document.getElementById(`edit-violation-number-${index}`);
            }
            if (firstInput) {
                firstInput.focus();
                firstInput.select();
            }
        }, 100);
    }
}

function saveEditedAccount(index) {
    if (index < 0 || index >= savedAccounts.length) return;
    
    const account = savedAccounts[index];
    
    // Get NY fields (always available in edit form)
    const accountNumberInput = document.getElementById(`edit-account-number-${index}`);
    const plateNumberInput = document.getElementById(`edit-plate-number-${index}`);
    if (!accountNumberInput || !plateNumberInput) {
        showError('Error: Could not find NY account fields');
        return;
    }
    const newAccountNumber = accountNumberInput.value.trim();
    const newPlateNumber = plateNumberInput.value.trim();
    
    // Get NJ fields (always available in edit form)
    const violationInput = document.getElementById(`edit-violation-number-${index}`);
    const njPlateInput = document.getElementById(`edit-nj-plate-number-${index}`);
    if (!violationInput || !njPlateInput) {
        showError('Error: Could not find NJ violation fields');
        return;
    }
    const newViolationNumber = violationInput.value.trim();
    const newNJPlate = njPlateInput.value.trim();
    
    // Get email
    const emailInput = document.getElementById(`edit-email-${index}`);
    if (!emailInput) {
        showError('Error: Could not find email field');
        return;
    }
    const newEmail = emailInput.value.trim();
    
    // Determine which sources we have
    const hasNY = newAccountNumber && newPlateNumber;
    const hasNJ = newViolationNumber && newNJPlate;
    
    // Validate at least one source is provided
    if (!hasNY && !hasNJ) {
        showError('Please provide either NY account information (account + plate) or NJ violation information (violation + plate)');
        return;
    }
    
    // Update account with NY fields
    if (hasNY) {
        savedAccounts[index].account_number = newAccountNumber;
        savedAccounts[index].plate_number = newPlateNumber;
    } else {
        // Remove NY fields if not provided
        delete savedAccounts[index].account_number;
        delete savedAccounts[index].plate_number;
    }
    
    // Update account with NJ fields
    if (hasNJ) {
        savedAccounts[index].violation_number = newViolationNumber;
        savedAccounts[index].nj_violation_number = newViolationNumber;
        savedAccounts[index].nj_plate_number = newNJPlate;
    } else {
        // Remove NJ fields if not provided
        delete savedAccounts[index].violation_number;
        delete savedAccounts[index].nj_violation_number;
        delete savedAccounts[index].nj_plate_number;
    }
    
    // Update sources array
    const sources = [];
    if (hasNY) sources.push('NY');
    if (hasNJ) sources.push('NJ');
    savedAccounts[index].sources = sources;
    savedAccounts[index].source = sources[0] || 'NY'; // Default to first source
    
    // Update email
    savedAccounts[index].email = newEmail || '';
    
    // Remove edit form
    cancelEditAccount(index);
    
    // Save to server
    saveAccountsToServer();
}

function cancelEditAccount(index) {
    const accountItem = document.getElementById(`account-${index}`);
    if (!accountItem) return;
    
    const editForm = accountItem.querySelector('.edit-form');
    if (editForm) {
        editForm.remove();
    }
}

function removeSavedAccount(index) {
    if (index < 0 || index >= savedAccounts.length) return;
    
    const account = savedAccounts[index];
    const sources = account.sources || [account.source || 'NY'];
    const hasNY = sources.includes('NY') && account.account_number;
    const hasNJ = sources.includes('NJ') && (account.violation_number || account.nj_violation_number);
    
    let accountDesc = '';
    if (hasNY && hasNJ) {
        accountDesc = `NY: ${account.account_number} / NJ: ${account.violation_number || account.nj_violation_number}`;
    } else if (hasNY) {
        accountDesc = `NY: ${account.account_number}`;
    } else if (hasNJ) {
        accountDesc = `NJ: ${account.violation_number || account.nj_violation_number}`;
    } else {
        accountDesc = `Account #${index + 1}`;
    }
    
    if (confirm(`Remove account ${accountDesc}?`)) {
        savedAccounts.splice(index, 1);
        saveAccountsToServer();
    }
}

function saveAccountsToServer(suppressMessage = false) {
    // Prepare accounts with all data including balance
    const accountsToSave = savedAccounts.map(acc => {
        const accountData = {
            email: acc.email || ''
        };
        
        // Include NY account fields if they exist
        if (acc.account_number) {
            accountData.account_number = acc.account_number;
        }
        if (acc.plate_number) {
            accountData.plate_number = acc.plate_number;
        }
        
        // Include NJ violation fields if they exist
        if (acc.violation_number || acc.nj_violation_number) {
            accountData.violation_number = acc.violation_number || acc.nj_violation_number;
            accountData.nj_violation_number = acc.violation_number || acc.nj_violation_number;
        }
        if (acc.nj_plate_number) {
            accountData.nj_plate_number = acc.nj_plate_number;
        }
        
        // Include source information
        if (acc.source) {
            accountData.source = acc.source;
        }
        if (acc.sources) {
            accountData.sources = acc.sources;
        }
        
        // Include balance data (always include, even if 0)
        accountData.balance_amount = acc.balance_amount !== undefined ? acc.balance_amount : 0;
        // Include separate NY and NJ balances (always include, even if 0)
        accountData.ny_balance_amount = acc.ny_balance_amount !== undefined ? acc.ny_balance_amount : 0;
        accountData.nj_balance_amount = acc.nj_balance_amount !== undefined ? acc.nj_balance_amount : 0;
        if (acc.violation_count !== undefined) {
            accountData.violation_count = acc.violation_count;
        }
        if (acc.toll_bill_numbers !== undefined) {
            accountData.toll_bill_numbers = acc.toll_bill_numbers;
        }
        if (acc.last_updated !== undefined) {
            accountData.last_updated = acc.last_updated;
        }
        
        return accountData;
    });
    
    fetch('/api/accounts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            accounts: accountsToSave
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update savedAccounts with server response (which includes preserved balance data)
            if (data.accounts) {
                savedAccounts = data.accounts;
            }
            renderSavedAccounts();
            if (!suppressMessage) {
                showSuccessMessage(`✅ ${data.message || 'Accounts saved successfully!'}`);
            }
        } else {
            showError('Failed to save accounts: ' + (data.error || 'Unknown error'));
            // Reload to get correct state
            loadSavedAccounts();
        }
    })
    .catch(error => {
        console.error('Error saving accounts:', error);
        showError('Error saving accounts. Please try again.');
        // Reload to get correct state
        loadSavedAccounts();
    });
}

function showSuccessMessage(message) {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.style.backgroundColor = '#d1fae5';
        errorMessage.style.color = '#065f46';
        errorMessage.style.borderColor = '#10b981';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 3000);
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.style.backgroundColor = '#fee2e2';
        errorMessage.style.color = '#991b1b';
        errorMessage.style.borderColor = '#ef4444';
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
        alert('Error: ' + message);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved accounts
    loadSavedAccounts();
    
    // Add NY account button
    const addSavedAccountBtn = document.getElementById('addSavedAccountBtn');
    if (addSavedAccountBtn) {
        addSavedAccountBtn.addEventListener('click', addSavedAccount);
    }
    
    // Add NJ account button
    const addNJAccountBtn = document.getElementById('addNJAccountBtn');
    if (addNJAccountBtn) {
        addNJAccountBtn.addEventListener('click', addNJAccount);
    }
    
    // Refresh button
    const loadSavedAccountsBtn = document.getElementById('loadSavedAccountsBtn');
    if (loadSavedAccountsBtn) {
        loadSavedAccountsBtn.addEventListener('click', loadSavedAccounts);
    }
});

async function refreshAccountData(index) {
    if (index < 0 || index >= savedAccounts.length) return;
    
    const account = savedAccounts[index];
    const sources = account.sources || [account.source || 'NY'];
    const hasNY = sources.includes('NY') && account.account_number;
    const hasNJ = sources.includes('NJ') && (account.violation_number || account.nj_violation_number);
    
    if (!hasNY && !hasNJ) {
        showError('Account needs either NY account number or NJ violation number');
        return;
    }
    
    // Set loading state
    savedAccounts[index].isLoading = true;
    renderSavedAccounts();
    
    let totalBalance = 0;
    let nyBalance = 0;
    let njBalance = 0;
    let allBillNumbers = [];
    let allViolations = 0;
    let hasError = false;
    let errorMessages = [];
    let balanceBreakdown = [];
    let nyData = null;
    let njData = null;
    
    // Process NY account first (if exists)
    if (hasNY) {
        try {
            console.log(`Processing NY account for index ${index}...`);
            const nyResponse = await fetch('/api/fetch-single-account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    account_number: account.account_number,
                    plate_number: account.plate_number || account.ny_plate_number,
                    source: 'NY'
                })
            });
            
            nyData = await nyResponse.json();
            
            if (nyData.success) {
                nyBalance = nyData.balance_amount || 0;
                totalBalance += nyBalance;
                allBillNumbers = allBillNumbers.concat(nyData.toll_bill_numbers || []);
                allViolations += nyData.violation_count || 0;
                // Store NY balance separately
                savedAccounts[index].ny_balance_amount = nyBalance;
                console.log(`✅ NY account balance: $${nyBalance.toFixed(2)}`);
                balanceBreakdown.push(`NY: $${nyBalance.toFixed(2)}`);
            } else {
                hasError = true;
                errorMessages.push(`NY: ${nyData.error || 'Failed to fetch'}`);
                console.log(`❌ NY account failed: ${nyData.error || 'Failed to fetch'}`);
            }
        } catch (error) {
            console.error('Error fetching NY account:', error);
            hasError = true;
            errorMessages.push(`NY: ${error.message}`);
        }
    }
    
    // Process NJ account second (if exists) - sequentially after NY
    if (hasNJ) {
        try {
            const violationNumber = account.violation_number || account.nj_violation_number;
            const njPlateNumber = account.nj_plate_number || account.plate_number;
            
            console.log(`Processing NJ account for index ${index}...`);
            const njResponse = await fetch('/api/fetch-nj-violation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    violation_number: violationNumber,
                    plate_number: njPlateNumber
                })
            });
            
            njData = await njResponse.json();
            
            if (njData.success) {
                njBalance = njData.balance_amount || 0;
                totalBalance += njBalance;
                allBillNumbers = allBillNumbers.concat(njData.toll_bill_numbers || []);
                allViolations += njData.violation_count || 0;
                // Store NJ balance separately
                savedAccounts[index].nj_balance_amount = njBalance;
                console.log(`✅ NJ account balance: $${njBalance.toFixed(2)}`);
                balanceBreakdown.push(`NJ: $${njBalance.toFixed(2)}`);
            } else {
                hasError = true;
                errorMessages.push(`NJ: ${njData.error || 'Failed to fetch'}`);
                console.log(`❌ NJ account failed: ${njData.error || 'Failed to fetch'}`);
            }
        } catch (error) {
            console.error('Error fetching NJ account:', error);
            hasError = true;
            errorMessages.push(`NJ: ${error.message}`);
        }
    }
    
    // Update account with combined data
    savedAccounts[index].isLoading = false;
    savedAccounts[index].balance_amount = totalBalance;
    // Ensure separate balances are set (even if 0)
    savedAccounts[index].ny_balance_amount = nyBalance;
    savedAccounts[index].nj_balance_amount = njBalance;
    savedAccounts[index].violation_count = allViolations;
    savedAccounts[index].toll_bill_numbers = [...new Set(allBillNumbers)]; // Remove duplicates
    savedAccounts[index].last_updated = new Date().toLocaleString();
    
    // Save updated account data to server
    saveAccountsToServer(true); // Suppress message
    
    // Send email if account has email address and at least one source succeeded
    const accountEmail = savedAccounts[index].email;
    const hasAnySuccess = (nyData && nyData.success) || (njData && njData.success); // At least one source succeeded
    
    if (accountEmail && accountEmail.trim() && hasAnySuccess) {
        // Create combined result object for email
        const combinedResult = {
            'success': true,
            'account_number': account.account_number || '',
            'plate_number': account.plate_number || '',
            'violation_number': account.violation_number || account.nj_violation_number || '',
            'nj_plate_number': account.nj_plate_number || account.plate_number || '',
            'balance_amount': totalBalance,
            'ny_balance_amount': nyBalance,
            'nj_balance_amount': njBalance,
            'toll_bill_numbers': [...new Set(allBillNumbers)],
            'violation_count': allViolations,
            'sources': sources
        };
        
        // Send email asynchronously
        fetch('/api/send-account-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: accountEmail.trim(),
                toll_data: combinedResult
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`✅ Email sent successfully to ${accountEmail}`);
            } else {
                console.error(`❌ Failed to send email to ${accountEmail}: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            console.error(`❌ Error sending email to ${accountEmail}:`, error);
        });
    } else if (accountEmail && accountEmail.trim() && !hasAnySuccess) {
        console.log(`⚠️  Email not sent - no data fetched successfully for account ${index}`);
    } else if (!accountEmail || !accountEmail.trim()) {
        console.log(`⚠️  Email not sent - no email address configured for account ${index}`);
    }
    
    // Show result with breakdown
    let breakdownText = '';
    if (balanceBreakdown.length > 0) {
        breakdownText = ` (${balanceBreakdown.join(' + ')})`;
    }
    
    if (hasError && errorMessages.length > 0) {
        showError(`Some errors occurred: ${errorMessages.join('; ')}. Total Balance: $${totalBalance.toFixed(2)}${breakdownText}`);
    } else {
        let successMsg = `✅ Balance updated: $${totalBalance.toFixed(2)}${breakdownText}`;
        if (accountEmail && accountEmail.trim() && hasAnySuccess) {
            successMsg += ` - Email sent to ${accountEmail}`;
        }
        showSuccessMessage(successMsg);
        // Also log to console for debugging
        console.log(`📊 Balance breakdown for account ${index}:`);
        if (hasNY) console.log(`   NY Balance: $${nyBalance.toFixed(2)}`);
        if (hasNJ) console.log(`   NJ Balance: $${njBalance.toFixed(2)}`);
        console.log(`   Total Balance: $${totalBalance.toFixed(2)}`);
    }
    
    renderSavedAccounts();
}

// Make functions globally available
window.addSavedAccount = addSavedAccount;
window.addNJAccount = addNJAccount;
window.removeSavedAccount = removeSavedAccount;
window.editSavedAccount = editSavedAccount;
window.saveEditedAccount = saveEditedAccount;
window.cancelEditAccount = cancelEditAccount;
window.refreshAccountData = refreshAccountData;
window.loadSavedAccounts = loadSavedAccounts;



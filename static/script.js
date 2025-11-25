// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tollForm');
    const fetchBtn = document.getElementById('fetchBtn');
    const resultsSection = document.getElementById('resultsSection');
    const errorMessage = document.getElementById('errorMessage');
    const loadingOverlay = document.getElementById('loadingOverlay');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const accountNumber = document.getElementById('accountNumber').value.trim();
        const plateNumber = document.getElementById('plateNumber').value.trim();
        const email = document.getElementById('email').value.trim();
        
        if (!accountNumber || !plateNumber) {
            showError('Please enter both account number and plate number');
            return;
        }
        
        // Show loading
        loadingOverlay.style.display = 'flex';
        fetchBtn.disabled = true;
        errorMessage.style.display = 'none';
        resultsSection.style.display = 'none';
        
        try {
            const response = await fetch('/api/fetch-toll-info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    account_number: accountNumber,
                    plate_number: plateNumber,
                    headless: false,
                    email: email
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayResults(data);
                
                // Show email confirmation if email was sent
                if (data.email_sent) {
                    const emailInput = document.getElementById('email');
                    if (emailInput && emailInput.value.trim()) {
                        setTimeout(() => {
                            alert(`✅ Email sent successfully to ${emailInput.value.trim()}!\n\nCheck your inbox for your toll information.`);
                        }, 500);
                    }
                }
            } else {
                let errorMsg = data.error || 'Failed to fetch toll information. Please check your credentials and try again.';
                
                // Provide helpful message for common errors
                if (errorMsg.includes('ERR_ABORTED') || errorMsg.includes('blocking')) {
                    errorMsg = 'The E-ZPass NY website is blocking automated requests. This is a security measure.\n\n' +
                               'Possible solutions:\n' +
                               '• Verify you can access the website manually in a browser\n' +
                               '• Try using a VPN or different network\n' +
                               '• Contact E-ZPass NY about API access\n\n' +
                               'Original error: ' + errorMsg;
                }
                
                showError(errorMsg);
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please check your connection and try again.');
        } finally {
            loadingOverlay.style.display = 'none';
            fetchBtn.disabled = false;
        }
    });
    
    function displayResults(data) {
        // Display Balance Due - show only Account Balance
        const balanceDueAmount = document.getElementById('balanceDueAmount');
        
        // Get account balance amount (not total balance due)
        let balanceAmt = data.balance_amount || 0;
        
        // Ensure we have a valid number
        balanceAmt = parseFloat(balanceAmt) || 0;
        
        // Display account balance
        balanceDueAmount.textContent = `$${balanceAmt.toFixed(2)}`;
        balanceDueAmount.style.color = '#ffffff';
        
        // Display toll bill numbers only
        const tollsList = document.getElementById('tollsList');
        if (tollsList) {
            if (data.toll_bill_numbers && data.toll_bill_numbers.length > 0) {
                tollsList.innerHTML = data.toll_bill_numbers.map(billNumber =>
                    `<div class="toll-item">${billNumber}</div>`
                ).join('');
            } else if (data.toll_entries && data.toll_entries.length > 0) {
                // Extract bill numbers from toll entries if not already extracted
                const billNumbers = [];
                data.toll_entries.forEach(entry => {
                    // Look for bill numbers (typically alphanumeric codes or numbers)
                    // Common patterns: "Bill #12345", "Invoice: ABC123", "Toll Bill: 123456"
                    const billMatch = entry.match(/(?:bill|invoice|toll\s*bill)[\s#:]*([A-Z0-9-]+)/i);
                    if (billMatch && billMatch[1]) {
                        billNumbers.push(billMatch[1]);
                    } else {
                        // Try to find any alphanumeric code that might be a bill number
                        const codeMatch = entry.match(/\b([A-Z]{2,}\d{4,}|\d{6,})\b/);
                        if (codeMatch && codeMatch[1]) {
                            billNumbers.push(codeMatch[1]);
                        }
                    }
                });
                
                if (billNumbers.length > 0) {
                    tollsList.innerHTML = billNumbers.map(billNumber =>
                        `<div class="toll-item">${billNumber}</div>`
                    ).join('');
                } else {
                    tollsList.innerHTML = '<div class="toll-item">No toll bill numbers found</div>';
                }
            } else {
                tollsList.innerHTML = '<div class="toll-item">No bill numbers found</div>';
            }
        }

        // Display account info
        document.getElementById('accountNumberDisplay').textContent = data.account_number || 'N/A';
        document.getElementById('plateNumberDisplay').textContent = data.plate_number || 'N/A';
        
        const now = new Date();
        document.getElementById('lastUpdated').textContent = now.toLocaleString();
        
        // Show results section
        resultsSection.style.display = 'grid';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Try to load last data on page load
    fetch('/api/last-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayResults(data);
            }
        })
        .catch(error => {
            console.log('No previous data available');
        });
});


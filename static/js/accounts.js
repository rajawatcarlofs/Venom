function loadAccounts() {
    fetch('/api/accounts').then(res => res.json()).then(accounts => {
        const tbody = document.getElementById('accountsBody');
        if (accounts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">No accounts added yet. Click "Add New Account" to add one.</td></tr>';
        } else {
            tbody.innerHTML = accounts.map(acc => `
                <tr>
                    <td>${acc.phone}</td>
                    <td>${acc.user_name}</td>
                    <td>${acc.user_id}</td>
                    <td><span class="badge bg-${acc.status === 'online' ? 'success' : 'danger'}">${acc.status.toUpperCase()}</span></td>
                    <td><small>${formatDate(acc.created_at)}</small></td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="disconnectAccount(${acc.id})"><i class="fas fa-times"></i></button>
                    </td>
                </tr>
            `).join('');
        }
    });
}

function addAccount() {
    const phone = document.getElementById('phone').value;
    if (!phone) {
        showNotification('Please enter phone number', 'error');
        return;
    }
    fetch('/api/account/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({phone})
    }).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification(data.message);
            const addModal = bootstrap.Modal.getInstance(document.getElementById('addAccountModal'));
            addModal.hide();
            const otpModal = new bootstrap.Modal(document.getElementById('otpModal'));
            otpModal.show();
        } else {
            showNotification(data.error, 'error');
        }
    });
}

function verifyOTP() {
    const otp = document.getElementById('otp').value;
    fetch('/api/account/verify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({otp})
    }).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Account added successfully!');
            bootstrap.Modal.getInstance(document.getElementById('otpModal')).hide();
            loadAccounts();
        } else {
            showNotification(data.error, 'error');
        }
    });
}

function disconnectAccount(accountId) {
    if (!confirm('Are you sure you want to disconnect this account?')) return;
    fetch(`/api/account/${accountId}/disconnect`, {method: 'POST'}).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Account disconnected');
            loadAccounts();
        } else {
            showNotification(data.error, 'error');
        }
    });
}

loadAccounts();

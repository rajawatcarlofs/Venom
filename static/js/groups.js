function loadAccountsForGroups() {
    fetch('/api/accounts').then(res => res.json()).then(accounts => {
        const list = document.getElementById('accountsList');
        list.innerHTML = accounts.map(acc => `
            <label class="list-group-item">
                <input type="checkbox" class="form-check-input me-2" value="${acc.id}" data-account>
                ${acc.user_name} (${acc.phone})
            </label>
        `).join('');
    });
}

function loadGroups() {
    const selectedAccounts = Array.from(document.querySelectorAll('[data-account]:checked')).map(el => parseInt(el.value));
    if (selectedAccounts.length === 0) {
        showNotification('Please select at least one account', 'error');
        return;
    }
    fetch('/api/groups/load', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({account_ids: selectedAccounts})
    }).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification(`Loaded ${data.groups_loaded} groups`);
            loadGroupsList();
        } else {
            showNotification(data.error, 'error');
        }
    });
}

function loadGroupsList() {
    fetch('/api/groups').then(res => res.json()).then(groups => {
        const tbody = document.getElementById('groupsBody');
        if (groups.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">No groups loaded yet.</td></tr>';
        } else {
            tbody.innerHTML = groups.map(g => `
                <tr>
                    <td><input type="checkbox" class="form-check-input" value="${g.id}" data-group></td>
                    <td>${g.name}</td>
                    <td><span class="badge bg-info">${g.type.toUpperCase()}</span></td>
                    <td>${g.members}</td>
                    <td><small>${formatDate(g.created_at)}</small></td>
                </tr>
            `).join('');
        }
    });
}

function selectAllGroups() {
    const checkboxes = document.querySelectorAll('[data-group]');
    checkboxes.forEach(cb => cb.checked = document.getElementById('selectAll').checked);
}

function saveGroupSelection() {
    const selectedGroups = Array.from(document.querySelectorAll('[data-group]:checked')).map(el => parseInt(el.value));
    fetch('/api/groups/save-selection', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({group_ids: selectedGroups})
    }).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Selection saved successfully!');
        } else {
            showNotification(data.error, 'error');
        }
    });
}

function exportGroups() {
    fetch('/api/groups/export').then(res => res.json()).then(data => {
        const blob = new Blob([JSON.stringify(data.data, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `groups-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        showNotification('Groups exported successfully!');
    });
}

loadAccountsForGroups();
loadGroupsList();

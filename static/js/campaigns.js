function loadCampaigns() {
    fetch('/api/campaigns').then(res => res.json()).then(campaigns => {
        const tbody = document.getElementById('campaignsBody');
        if (campaigns.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">No campaigns created yet.</td></tr>';
        } else {
            tbody.innerHTML = campaigns.map(c => `
                <tr>
                    <td>${c.name}</td>
                    <td>${c.account_ids.length}</td>
                    <td>${c.group_ids.length}</td>
                    <td>${getStatusBadge(c.status)}</td>
                    <td>${c.messages_sent || 0} / ${c.failed_sends || 0}</td>
                    <td><small>${formatDate(c.created_at)}</small></td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="startCampaign(${c.id})"><i class="fas fa-play"></i></button>
                        <button class="btn btn-sm btn-warning" onclick="pauseCampaign(${c.id})"><i class="fas fa-pause"></i></button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCampaign(${c.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }
    });
}

function loadAccountsForCampaign() {
    fetch('/api/accounts').then(res => res.json()).then(accounts => {
        const list = document.getElementById('campaignAccounts');
        list.innerHTML = accounts.map(acc => `
            <label class="list-group-item">
                <input type="checkbox" class="form-check-input me-2" value="${acc.id}" data-campaign-account>
                ${acc.user_name}
            </label>
        `).join('');
    });
}

function loadGroupsForCampaign() {
    fetch('/api/groups').then(res => res.json()).then(groups => {
        const list = document.getElementById('campaignGroups');
        list.innerHTML = groups.map(g => `
            <label class="list-group-item">
                <input type="checkbox" class="form-check-input me-2" value="${g.id}" data-campaign-group>
                ${g.name}
            </label>
        `).join('');
    });
}

function createCampaign() {
    const name = document.getElementById('campaignName').value;
    const message = document.getElementById('campaignMessage').value;
    const accountIds = Array.from(document.querySelectorAll('[data-campaign-account]:checked')).map(el => parseInt(el.value));
    const groupIds = Array.from(document.querySelectorAll('[data-campaign-group]:checked')).map(el => parseInt(el.value));
    
    if (!name || !message || accountIds.length === 0 || groupIds.length === 0) {
        showNotification('Please fill all required fields', 'error');
        return;
    }
    
    fetch('/api/campaign/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, message, account_ids: accountIds, group_ids: groupIds})
    }).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Campaign created successfully!');
            bootstrap.Modal.getInstance(document.getElementById('createCampaignModal')).hide();
            loadCampaigns();
        } else {
            showNotification(data.error, 'error');
        }
    });
}

function startCampaign(campaignId) {
    fetch(`/api/campaign/${campaignId}/start`, {method: 'POST'}).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Campaign started!');
            loadCampaigns();
        } else {
            showNotification(data.error, 'error');
        }
    });
}

function pauseCampaign(campaignId) {
    fetch(`/api/campaign/${campaignId}/pause`, {method: 'POST'}).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Campaign paused');
            loadCampaigns();
        }
    });
}

function deleteCampaign(campaignId) {
    if (!confirm('Delete this campaign?')) return;
    fetch(`/api/campaign/${campaignId}/delete`, {method: 'DELETE'}).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Campaign deleted');
            loadCampaigns();
        }
    });
}

loadCampaigns();
loadAccountsForCampaign();
loadGroupsForCampaign();

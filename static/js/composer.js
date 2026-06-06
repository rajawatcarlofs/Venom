function saveTemplate() {
    const content = document.getElementById('messageContent').value;
    if (!content) {
        showNotification('Please write a message first', 'error');
        return;
    }
    const modal = new bootstrap.Modal(document.getElementById('saveTemplateModal'));
    modal.show();
}

function confirmSaveTemplate() {
    const name = document.getElementById('templateName').value;
    const content = document.getElementById('messageContent').value;
    if (!name) {
        showNotification('Please enter template name', 'error');
        return;
    }
    fetch('/api/template/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, content})
    }).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Template saved!');
            bootstrap.Modal.getInstance(document.getElementById('saveTemplateModal')).hide();
            document.getElementById('templateName').value = '';
            loadTemplates();
        }
    });
}

function loadTemplates() {
    fetch('/api/templates').then(res => res.json()).then(templates => {
        const list = document.getElementById('templatesList');
        if (templates.length === 0) {
            list.innerHTML = '<div class="list-group-item text-center py-4"><p class="text-muted mb-0">No templates</p></div>';
        } else {
            list.innerHTML = templates.map(t => `
                <a href="#" class="list-group-item list-group-item-action" onclick="loadTemplate(event, '${t.content.replace(/'/g, "\\'")}')">
                    <div class="d-flex w-100 justify-content-between">
                        <strong>${t.name}</strong>
                        <button type="button" class="btn btn-sm btn-danger" onclick="deleteTemplate(event, ${t.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <small>${t.content.substring(0, 50)}...</small>
                </a>
            `).join('');
        }
    });
}

function loadTemplate(e, content) {
    e.preventDefault();
    document.getElementById('messageContent').value = content;
    document.getElementById('messageContent').dispatchEvent(new Event('input'));
}

function deleteTemplate(e, templateId) {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Delete this template?')) return;
    fetch(`/api/template/${templateId}/delete`, {method: 'DELETE'}).then(res => res.json()).then(data => {
        if (data.success) {
            showNotification('Template deleted');
            loadTemplates();
        }
    });
}

function clearMessage() {
    document.getElementById('messageContent').value = '';
    document.getElementById('messageContent').dispatchEvent(new Event('input'));
}

loadTemplates();

function loadDashboard() {
    fetch('/api/accounts').then(r => r.json()).then(a => {
        document.getElementById('total-accounts').textContent = a.length;
    });
    fetch('/api/groups').then(r => r.json()).then(g => {
        document.getElementById('total-groups').textContent = g.length;
    });
    fetch('/api/campaigns').then(r => r.json()).then(c => {
        document.getElementById('active-campaigns').textContent = c.filter(x => x.status === 'running').length;
    });
}
loadDashboard();

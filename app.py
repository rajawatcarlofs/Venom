from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import json
from database import Database, init_db
from telegram_handler import TelegramHandler
from auth import check_auth, generate_session_token
import threading

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database and telegram handler
db = Database()
tg_handler = TelegramHandler(db)

# Create required directories
os.makedirs('sessions', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Initialize database on startup
init_db()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_token' not in session:
            return redirect(url_for('login'))
        if not check_auth(session.get('admin_token')):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Authentication Routes ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_auth(password):
            token = generate_session_token()
            session['admin_token'] = token
            db.log_activity('Admin login successful')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    db.log_activity('Admin logout')
    session.clear()
    return redirect(url_for('login'))

# ==================== Dashboard Routes ====================

@app.route('/')
@login_required
def index():
    """Redirect to dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    stats = {
        'total_accounts': len(db.get_all_accounts()),
        'total_groups': len(db.get_all_groups()),
        'active_campaigns': len(db.get_active_campaigns()),
        'messages_sent': db.get_stat('messages_sent') or 0,
        'failed_deliveries': db.get_stat('failed_deliveries') or 0,
    }
    return render_template('dashboard.html', stats=stats)

# ==================== Account Routes ====================

@app.route('/accounts')
@login_required
def accounts_page():
    """Account management page"""
    accounts = db.get_all_accounts()
    return render_template('accounts.html', accounts=accounts)

@app.route('/api/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get all accounts"""
    accounts = db.get_all_accounts()
    return jsonify([{'id': a.id, 'phone': a.phone, 'user_id': a.user_id, 'user_name': a.user_name, 'status': a.status, 'created_at': a.created_at} for a in accounts])

@app.route('/api/account/add', methods=['POST'])
@login_required
def add_account():
    """Add new account - initiate Telegram login"""
    try:
        phone = request.json.get('phone', '')
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        phone = phone.replace(' ', '').replace('-', '').replace('+', '')
        if len(phone) < 10:
            return jsonify({'success': False, 'error': 'Invalid phone number'}), 400
        
        result = tg_handler.start_login(phone)
        if result['success']:
            session['pending_phone'] = phone
            db.log_activity(f'Started login for {phone}')
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error adding account: {str(e)}")
        db.log_activity(f'Error adding account: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/verify', methods=['POST'])
@login_required
def verify_account():
    """Verify account with OTP"""
    try:
        otp = request.json.get('otp', '')
        phone = session.get('pending_phone', '')
        
        if not otp or not phone:
            return jsonify({'success': False, 'error': 'OTP and phone required'}), 400
        
        result = tg_handler.complete_login(phone, otp)
        if result['success']:
            db.add_account(phone, result.get('user_id'), result.get('user_name', 'Unknown'))
            session.pop('pending_phone', None)
            db.log_activity(f'Successfully added account {phone}')
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error verifying account: {str(e)}")
        db.log_activity(f'Error verifying account: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/<int:account_id>/disconnect', methods=['POST'])
@login_required
def disconnect_account(account_id):
    """Disconnect account"""
    try:
        result = tg_handler.disconnect_account(account_id)
        if result['success']:
            db.update_account_status(account_id, 'offline')
            db.log_activity(f'Disconnected account {account_id}')
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error disconnecting account: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/<int:account_id>/status', methods=['GET'])
@login_required
def get_account_status(account_id):
    """Get account status"""
    try:
        status = tg_handler.get_account_status(account_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting account status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Groups Routes ====================

@app.route('/groups')
@login_required
def groups_page():
    """Group management page"""
    accounts = db.get_all_accounts()
    return render_template('groups.html', accounts=accounts)

@app.route('/api/groups/load', methods=['POST'])
@login_required
def load_groups():
    """Load groups from selected accounts"""
    try:
        account_ids = request.json.get('account_ids', [])
        if not account_ids:
            return jsonify({'success': False, 'error': 'No accounts selected'}), 400
        
        groups = tg_handler.load_groups_for_accounts(account_ids)
        db.save_groups(groups)
        db.log_activity(f'Loaded groups from {len(account_ids)} accounts')
        return jsonify({'success': True, 'groups_loaded': len(groups)})
    except Exception as e:
        logger.error(f"Error loading groups: {str(e)}")
        db.log_activity(f'Error loading groups: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/groups', methods=['GET'])
@login_required
def get_groups():
    """Get all groups"""
    search = request.args.get('search', '')
    groups = db.get_all_groups(search)
    return jsonify([{'id': g.id, 'name': g.name, 'chat_id': g.chat_id, 'type': g.type, 'members': g.members, 'created_at': g.created_at} for g in groups])

@app.route('/api/groups/save-selection', methods=['POST'])
@login_required
def save_group_selection():
    """Save selected groups"""
    try:
        group_ids = request.json.get('group_ids', [])
        db.save_group_selection(group_ids)
        db.log_activity(f'Saved selection of {len(group_ids)} groups')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving group selection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/groups/export', methods=['GET'])
@login_required
def export_groups():
    """Export group list"""
    try:
        groups = db.get_all_groups()
        export_data = [{'id': g.id, 'name': g.name, 'chat_id': g.chat_id} for g in groups]
        return jsonify({'success': True, 'data': export_data})
    except Exception as e:
        logger.error(f"Error exporting groups: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/groups/import', methods=['POST'])
@login_required
def import_groups():
    """Import group list"""
    try:
        group_data = request.json.get('groups', [])
        for group in group_data:
            db.add_group(group.get('name'), group.get('chat_id'))
        db.log_activity(f'Imported {len(group_data)} groups')
        return jsonify({'success': True, 'imported': len(group_data)})
    except Exception as e:
        logger.error(f"Error importing groups: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Message Composer Routes ====================

@app.route('/composer')
@login_required
def composer_page():
    """Message composer page"""
    templates = db.get_all_templates()
    return render_template('composer.html', templates=templates)

@app.route('/api/templates', methods=['GET'])
@login_required
def get_templates():
    """Get all message templates"""
    templates = db.get_all_templates()
    return jsonify([{'id': t.id, 'name': t.name, 'content': t.content, 'created_at': t.created_at} for t in templates])

@app.route('/api/template/save', methods=['POST'])
@login_required
def save_template():
    """Save message template"""
    try:
        data = request.json
        name = data.get('name', '')
        content = data.get('content', '')
        
        if not name or not content:
            return jsonify({'success': False, 'error': 'Name and content required'}), 400
        
        db.add_template(name, content)
        db.log_activity(f'Saved template: {name}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving template: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/template/<int:template_id>/delete', methods=['DELETE'])
@login_required
def delete_template(template_id):
    """Delete template"""
    try:
        db.delete_template(template_id)
        db.log_activity(f'Deleted template {template_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Campaign Routes ====================

@app.route('/campaigns')
@login_required
def campaigns_page():
    """Campaign management page"""
    accounts = db.get_all_accounts()
    groups = db.get_all_groups()
    campaigns = db.get_all_campaigns()
    return render_template('campaigns.html', accounts=accounts, groups=groups, campaigns=campaigns)

@app.route('/api/campaigns', methods=['GET'])
@login_required
def get_campaigns():
    """Get all campaigns"""
    campaigns = db.get_all_campaigns()
    return jsonify([{'id': c.id, 'name': c.name, 'message': c.message[:100], 'account_ids': c.account_ids, 'group_ids': c.group_ids, 'status': c.status, 'created_at': c.created_at} for c in campaigns])

@app.route('/api/campaign/create', methods=['POST'])
@login_required
def create_campaign():
    """Create new campaign"""
    try:
        data = request.json
        name = data.get('name', '')
        message = data.get('message', '')
        account_ids = data.get('account_ids', [])
        group_ids = data.get('group_ids', [])
        
        if not all([name, message, account_ids, group_ids]):
            return jsonify({'success': False, 'error': 'All fields required'}), 400
        
        campaign_id = db.add_campaign(
            name=name,
            message=message,
            account_ids=account_ids,
            group_ids=group_ids,
            schedule_config=data.get('schedule_config', {})
        )
        db.log_activity(f'Created campaign: {name}')
        return jsonify({'success': True, 'campaign_id': campaign_id})
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<int:campaign_id>/start', methods=['POST'])
@login_required
def start_campaign(campaign_id):
    """Start campaign"""
    try:
        campaign = db.get_campaign(campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        db.update_campaign_status(campaign_id, 'running')
        
        def run_campaign():
            try:
                tg_handler.execute_campaign(campaign_id)
                db.update_campaign_status(campaign_id, 'completed')
            except Exception as e:
                logger.error(f"Campaign execution error: {str(e)}")
                db.update_campaign_status(campaign_id, 'error')
                db.log_activity(f'Campaign {campaign_id} error: {str(e)}', 'error')
        
        thread = threading.Thread(target=run_campaign, daemon=True)
        thread.start()
        
        db.log_activity(f'Started campaign {campaign_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error starting campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<int:campaign_id>/pause', methods=['POST'])
@login_required
def pause_campaign(campaign_id):
    """Pause campaign"""
    try:
        db.update_campaign_status(campaign_id, 'paused')
        db.log_activity(f'Paused campaign {campaign_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error pausing campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<int:campaign_id>/resume', methods=['POST'])
@login_required
def resume_campaign(campaign_id):
    """Resume campaign"""
    try:
        db.update_campaign_status(campaign_id, 'running')
        db.log_activity(f'Resumed campaign {campaign_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error resuming campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<int:campaign_id>/stop', methods=['POST'])
@login_required
def stop_campaign(campaign_id):
    """Stop campaign"""
    try:
        db.update_campaign_status(campaign_id, 'stopped')
        db.log_activity(f'Stopped campaign {campaign_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error stopping campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<int:campaign_id>/delete', methods=['DELETE'])
@login_required
def delete_campaign(campaign_id):
    """Delete campaign"""
    try:
        db.delete_campaign(campaign_id)
        db.log_activity(f'Deleted campaign {campaign_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Logs Routes ====================

@app.route('/logs')
@login_required
def logs_page():
    """Logs and monitoring page"""
    return render_template('logs.html')

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    """Get system logs"""
    limit = request.args.get('limit', 100, type=int)
    logs = db.get_logs(limit)
    return jsonify([{'id': l.id, 'activity': l.activity, 'level': l.level, 'timestamp': l.timestamp} for l in logs])

@app.route('/api/logs/export', methods=['GET'])
@login_required
def export_logs():
    """Export logs as JSON"""
    try:
        logs = db.get_logs(1000)
        export_data = [{'id': l.id, 'activity': l.activity, 'level': l.level, 'timestamp': l.timestamp} for l in logs]
        return jsonify({'success': True, 'data': export_data})
    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Settings Routes ====================

@app.route('/settings')
@login_required
def settings_page():
    """Settings page"""
    settings = db.get_all_settings()
    return render_template('settings.html', settings=settings)

@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    """Get all settings"""
    settings = db.get_all_settings()
    return jsonify(settings)

@app.route('/api/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update settings"""
    try:
        data = request.json
        for key, value in data.items():
            db.set_setting(key, value)
        db.log_activity(f'Updated settings')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== Application Entry Point ====================

if __name__ == '__main__':
    try:
        logger.info("Starting Telegram Message Manager Application")
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

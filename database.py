import sqlite3
import json
from datetime import datetime
import os

class Account:
    def __init__(self, id, phone, user_id, user_name, status='offline', created_at=None):
        self.id = id
        self.phone = phone
        self.user_id = user_id
        self.user_name = user_name
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()

class Group:
    def __init__(self, id, name, chat_id, type='group', members=0, created_at=None):
        self.id = id
        self.name = name
        self.chat_id = chat_id
        self.type = type
        self.members = members
        self.created_at = created_at or datetime.now().isoformat()

class Campaign:
    def __init__(self, id, name, message, account_ids, group_ids, status='draft', schedule_config=None, created_at=None):
        self.id = id
        self.name = name
        self.message = message
        self.account_ids = account_ids
        self.group_ids = group_ids
        self.status = status
        self.schedule_config = schedule_config or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.messages_sent = 0
        self.failed_sends = 0

class Template:
    def __init__(self, id, name, content, created_at=None):
        self.id = id
        self.name = name
        self.content = content
        self.created_at = created_at or datetime.now().isoformat()

class Log:
    def __init__(self, id, activity, level='info', timestamp=None):
        self.id = id
        self.activity = activity
        self.level = level
        self.timestamp = timestamp or datetime.now().isoformat()

class Database:
    def __init__(self, db_path='telegram_manager.db'):
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def execute(self, sql, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self.connection.commit()
        return cursor
    
    def execute_query(self, sql, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    def execute_one(self, sql, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchone()
    
    # Account Methods
    def add_account(self, phone, user_id, user_name):
        sql = "INSERT INTO accounts (phone, user_id, user_name, status, created_at) VALUES (?, ?, ?, 'online', ?)"
        cursor = self.execute(sql, (phone, user_id, user_name, datetime.now().isoformat()))
        return cursor.lastrowid
    
    def get_all_accounts(self):
        sql = "SELECT * FROM accounts ORDER BY created_at DESC"
        rows = self.execute_query(sql)
        return [Account(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
    
    def get_account(self, account_id):
        sql = "SELECT * FROM accounts WHERE id = ?"
        row = self.execute_one(sql, (account_id,))
        if row:
            return Account(row[0], row[1], row[2], row[3], row[4], row[5])
        return None
    
    def update_account_status(self, account_id, status):
        sql = "UPDATE accounts SET status = ? WHERE id = ?"
        self.execute(sql, (status, account_id))
    
    def delete_account(self, account_id):
        sql = "DELETE FROM accounts WHERE id = ?"
        self.execute(sql, (account_id,))
    
    # Group Methods
    def add_group(self, name, chat_id, type='group', members=0):
        sql = "INSERT INTO groups (name, chat_id, type, members, created_at) VALUES (?, ?, ?, ?, ?)"
        cursor = self.execute(sql, (name, chat_id, type, members, datetime.now().isoformat()))
        return cursor.lastrowid
    
    def get_all_groups(self, search=''):
        if search:
            sql = "SELECT * FROM groups WHERE name LIKE ? ORDER BY name"
            rows = self.execute_query(sql, (f'%{search}%',))
        else:
            sql = "SELECT * FROM groups ORDER BY name"
            rows = self.execute_query(sql)
        return [Group(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
    
    def get_group(self, group_id):
        sql = "SELECT * FROM groups WHERE id = ?"
        row = self.execute_one(sql, (group_id,))
        if row:
            return Group(row[0], row[1], row[2], row[3], row[4], row[5])
        return None
    
    def save_groups(self, groups):
        for group in groups:
            sql = "SELECT id FROM groups WHERE chat_id = ?"
            existing = self.execute_one(sql, (group['chat_id'],))
            if not existing:
                self.add_group(group['name'], group['chat_id'], group.get('type', 'group'))
    
    def delete_group(self, group_id):
        sql = "DELETE FROM groups WHERE id = ?"
        self.execute(sql, (group_id,))
    
    def save_group_selection(self, group_ids):
        self.set_setting('selected_groups', json.dumps(group_ids))
    
    def get_selected_groups(self):
        setting = self.get_setting('selected_groups')
        if setting:
            return json.loads(setting)
        return []
    
    # Campaign Methods
    def add_campaign(self, name, message, account_ids, group_ids, schedule_config=None):
        sql = "INSERT INTO campaigns (name, message, account_ids, group_ids, status, schedule_config, created_at) VALUES (?, ?, ?, ?, 'draft', ?, ?)"
        config_json = json.dumps(schedule_config or {})
        cursor = self.execute(sql, (name, message, json.dumps(account_ids), json.dumps(group_ids), config_json, datetime.now().isoformat()))
        return cursor.lastrowid
    
    def get_all_campaigns(self):
        sql = "SELECT * FROM campaigns ORDER BY created_at DESC"
        rows = self.execute_query(sql)
        campaigns = []
        for row in rows:
            c = Campaign(row[0], row[1], row[2], json.loads(row[3]), json.loads(row[4]), row[5], json.loads(row[6]), row[7])
            campaigns.append(c)
        return campaigns
    
    def get_campaign(self, campaign_id):
        sql = "SELECT * FROM campaigns WHERE id = ?"
        row = self.execute_one(sql, (campaign_id,))
        if row:
            return Campaign(row[0], row[1], row[2], json.loads(row[3]), json.loads(row[4]), row[5], json.loads(row[6]), row[7])
        return None
    
    def get_active_campaigns(self):
        sql = "SELECT * FROM campaigns WHERE status IN ('running', 'paused')"
        rows = self.execute_query(sql)
        campaigns = []
        for row in rows:
            c = Campaign(row[0], row[1], row[2], json.loads(row[3]), json.loads(row[4]), row[5], json.loads(row[6]), row[7])
            campaigns.append(c)
        return campaigns
    
    def update_campaign_status(self, campaign_id, status):
        sql = "UPDATE campaigns SET status = ? WHERE id = ?"
        self.execute(sql, (status, campaign_id))
    
    def update_campaign_stats(self, campaign_id, messages_sent=0, failed_sends=0):
        sql = "UPDATE campaigns SET messages_sent = messages_sent + ?, failed_sends = failed_sends + ? WHERE id = ?"
        self.execute(sql, (messages_sent, failed_sends, campaign_id))
    
    def delete_campaign(self, campaign_id):
        sql = "DELETE FROM campaigns WHERE id = ?"
        self.execute(sql, (campaign_id,))
    
    # Template Methods
    def add_template(self, name, content):
        sql = "INSERT INTO templates (name, content, created_at) VALUES (?, ?, ?)"
        cursor = self.execute(sql, (name, content, datetime.now().isoformat()))
        return cursor.lastrowid
    
    def get_all_templates(self):
        sql = "SELECT * FROM templates ORDER BY created_at DESC"
        rows = self.execute_query(sql)
        return [Template(row[0], row[1], row[2], row[3]) for row in rows]
    
    def get_template(self, template_id):
        sql = "SELECT * FROM templates WHERE id = ?"
        row = self.execute_one(sql, (template_id,))
        if row:
            return Template(row[0], row[1], row[2], row[3])
        return None
    
    def delete_template(self, template_id):
        sql = "DELETE FROM templates WHERE id = ?"
        self.execute(sql, (template_id,))
    
    # Log Methods
    def log_activity(self, activity, level='info'):
        sql = "INSERT INTO logs (activity, level, timestamp) VALUES (?, ?, ?)"
        self.execute(sql, (activity, level, datetime.now().isoformat()))
    
    def get_logs(self, limit=100):
        sql = "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?"
        rows = self.execute_query(sql, (limit,))
        return [Log(row[0], row[1], row[2], row[3]) for row in rows]
    
    # Settings Methods
    def set_setting(self, key, value):
        sql = "SELECT id FROM settings WHERE key = ?"
        existing = self.execute_one(sql, (key,))
        
        if existing:
            sql = "UPDATE settings SET value = ? WHERE key = ?"
            self.execute(sql, (str(value), key))
        else:
            sql = "INSERT INTO settings (key, value) VALUES (?, ?)"
            self.execute(sql, (key, str(value)))
    
    def get_setting(self, key):
        sql = "SELECT value FROM settings WHERE key = ?"
        row = self.execute_one(sql, (key,))
        if row:
            return row[0]
        return None
    
    def get_all_settings(self):
        sql = "SELECT key, value FROM settings"
        rows = self.execute_query(sql)
        return {row[0]: row[1] for row in rows}
    
    # Statistics Methods
    def get_stat(self, key):
        sql = "SELECT value FROM statistics WHERE key = ?"
        row = self.execute_one(sql, (key,))
        if row:
            return int(row[0])
        return 0
    
    def increment_stat(self, key):
        current = self.get_stat(key)
        sql = "SELECT id FROM statistics WHERE key = ?"
        existing = self.execute_one(sql, (key,))
        
        if existing:
            sql = "UPDATE statistics SET value = ? WHERE key = ?"
            self.execute(sql, (current + 1, key))
        else:
            sql = "INSERT INTO statistics (key, value) VALUES (?, ?)"
            self.execute(sql, (key, 1))

def init_db():
    db = Database()
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        user_name TEXT,
        status TEXT DEFAULT 'offline',
        created_at TEXT
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        chat_id INTEGER UNIQUE NOT NULL,
        type TEXT DEFAULT 'group',
        members INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        message TEXT NOT NULL,
        account_ids TEXT NOT NULL,
        group_ids TEXT NOT NULL,
        status TEXT DEFAULT 'draft',
        schedule_config TEXT,
        created_at TEXT,
        messages_sent INTEGER DEFAULT 0,
        failed_sends INTEGER DEFAULT 0
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity TEXT NOT NULL,
        level TEXT DEFAULT 'info',
        timestamp TEXT
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value INTEGER DEFAULT 0
    )
    """)
    
    db.close()

import os
import json
from datetime import datetime

def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)

def get_file_size(file_path):
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def format_file_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_timestamp():
    return datetime.now().isoformat()

def parse_phone_number(phone):
    phone = phone.replace(' ', '').replace('-', '').replace('+', '')
    if not phone.isdigit() or len(phone) < 10:
        return None
    return f"+{phone}"

def safe_json_encode(obj):
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return "{}"

def safe_json_decode(json_str, default=None):
    try:
        return json.loads(json_str)
    except Exception:
        return default or {}

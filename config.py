import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'telegram_manager.db')
    API_ID = os.getenv('TELEGRAM_API_ID', '')
    API_HASH = os.getenv('TELEGRAM_API_HASH', '')
    SESSION_PATH = os.getenv('SESSION_PATH', 'sessions')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    LOG_PATH = os.getenv('LOG_PATH', 'logs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MESSAGE_DELAY = int(os.getenv('MESSAGE_DELAY', '2'))
    RANDOM_DELAY = int(os.getenv('RANDOM_DELAY', '1'))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '52428800'))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    @staticmethod
    def get_config():
        return Config()

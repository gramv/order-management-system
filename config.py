import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # URL encode the password to handle special characters
    DB_PASSWORD = quote_plus(os.environ.get('SUPABASE_DB_PASSWORD', ''))
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://postgres.vmkaynbnljwubhxvvflb:{DB_PASSWORD}"
        "@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        "?sslmode=require"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Maximum file size (optional)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

    @staticmethod
    def init_app(app):
        pass
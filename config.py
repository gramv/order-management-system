import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import cloudinary


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

    # Add these to your Config class
    # Allowed file types for sales documents
    ALLOWED_REPORT_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    MAX_REPORT_SIZE = 5 * 1024 * 1024  # 5MB max file size
    
    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    @staticmethod
    def init_app(app):
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET'],
            secure=True
        )

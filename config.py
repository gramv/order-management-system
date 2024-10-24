import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    # Secret key configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Supabase PostgreSQL configuration
    DB_USER = os.environ.get('SUPABASE_DB_USER')
    DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD')
    DB_HOST = os.environ.get('SUPABASE_DB_HOST')
    DB_PORT = os.environ.get('SUPABASE_DB_PORT', '5432')
    DB_NAME = os.environ.get('SUPABASE_DB_NAME', 'postgres')
    
    # Construct database URL
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase API configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    
    # Upload folder configuration
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'app', 'uploads')

    @staticmethod
    def init_app(app):
        pass
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # URL encode the password to handle special characters
    DB_PASSWORD = quote_plus(os.environ.get('SUPABASE_DB_PASSWORD', ''))
    
    # Database Configuration using the working connection settings
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://postgres.vmkaynbnljwubhxvvflb:{DB_PASSWORD}"
        "@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Add the working connection parameters
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'sslmode': 'require',
            'host': 'aws-0-us-east-1.pooler.supabase.com',
            'port': '6543',
            'client_encoding': 'utf8'
        }
    }

    @staticmethod
    def init_app(app):
        pass
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

def test_db_connection():
    # URL encode the password
    password = quote_plus(os.getenv('SUPABASE_DB_PASSWORD', ''))
    
    # Construct connection string
    connection_string = (
        f"postgresql://postgres.vmkaynbnljwubhxvvflb:{password}"
        "@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    
    # Create engine with explicit TCP connection parameters
    engine = create_engine(
        connection_string,
        connect_args={
            'sslmode': 'require',
            'host': 'aws-0-us-east-1.pooler.supabase.com',
            'port': '6543',
        }
    )
    
    try:
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1')).scalar()
            print("Database connection successful!")
            print(f"Test query result: {result}")
            return True
    except Exception as e:
        print("Database connection failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_db_connection()
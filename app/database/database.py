from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import settings 


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        # Try to connect to the database
        connection = engine.connect()
        print("Successfully connected to the database!")
        connection.close()
        return True
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        return False

# Test connection when the module is imported
if __name__ == "__main__":
    test_connection()


        
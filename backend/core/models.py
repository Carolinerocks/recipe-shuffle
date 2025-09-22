from sqlalchemy import create_engine, Column, Integer, String, Text, ARRAY, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import psycopg2
from .config import DB_CONFIG

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    meal_id = Column(String(50), unique=True, nullable=False)  # TheMealDB ID
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    area = Column(String(100))
    instructions = Column(Text)
    image_url = Column(String(500))
    youtube_url = Column(String(500))
    ingredients = Column(ARRAY(String))  # List of ingredients
    measures = Column(ARRAY(String))     # List of measures
    tags = Column(ARRAY(String))        # List of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            # Build database connection string
            db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            print("Database connection successful!")
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise e
    
    def create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(self.engine)
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Failed to create database tables: {e}")
            raise e
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def close_session(self, session):
        """Close database session"""
        session.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.pool import QueuePool
from .settings import get_settings
import logging
from user_management.infrastructure.base import  BaseModel
logger = logging.getLogger(__name__)

class DatabaseConfig:
    _engine=None
    _session_local=None

    @classmethod
    def init_db(cls):
        settings = get_settings()
        logger.info(f"Initializing database connection to {settings.DATABASE_URL}")

        cls._engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
            echo=settings.ECHO_SQL,
            pool_recycle=3600
        )
        cls._session_local = sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)
        logger.info("Database connection initialized successfully.")

    @classmethod
    def get_engine(self):
        if self._engine is None:
            self.init_db()
        return self._engine
    @classmethod
    def get_session(cls) -> Session:
        """Get database session"""
        if cls._session_local is None:
            cls.init_db()
        return cls._session_local()
    
    @classmethod
    def create_all_tables(cls):
        """Create all database tables"""
        
        engine = cls.get_engine()
        BaseModel.metadata.create_all(bind=engine)
        logger.info("All tables created")
    
    @classmethod
    def drop_all_tables(cls):
        """Drop all tables (use with caution!)"""
        
        engine = cls.get_engine()
        BaseModel.metadata.drop_all(bind=engine)
        logger.info("All tables dropped")


def get_db() -> Session:
    """Dependency injection for database session"""
    db = DatabaseConfig.get_session()
    try:
        yield db
    finally:
        db.close()
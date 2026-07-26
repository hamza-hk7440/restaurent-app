# backend/app/shared/infrastructure/database/base.py


from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid
from user_management.infrastructure.config.database import DatabaseConfig


Base = declarative_base()


class BaseModel:

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier (UUID)"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        doc="Timestamp of record creation"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        doc="Timestamp of last update"
    )



def create_all_tables():

    
    engine = DatabaseConfig.get_engine()
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully")


def drop_all_tables():
  
    engine = DatabaseConfig.get_engine()
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped successfully")


def get_table_names():
   
    return list(Base.metadata.tables.keys())



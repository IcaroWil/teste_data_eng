from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings

source_engine = create_engine(settings.source_db_url, pool_pre_ping=True)
target_engine = create_engine(settings.target_db_url, pool_pre_ping=True)
SourceSessionLocal = sessionmaker(bind=source_engine, autocommit=False, autoflush=False)
TargetSessionLocal = sessionmaker(bind=target_engine, autocommit=False, autoflush=False)

def get_source_session():
    db = SourceSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_target_session():
    db = TargetSessionLocal()
    try:
        yield db
    finally:
        db.close()
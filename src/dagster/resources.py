from dagster import ConfigurableResource
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SourceDBResource(ConfigurableResource):
    db_url: str
    
    def get_engine(self):
        return create_engine(self.db_url, pool_pre_ping=True)
    
    def get_session(self):
        engine = self.get_engine()
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        return SessionLocal()


class TargetDBResource(ConfigurableResource):
    db_url: str
    
    def get_engine(self):
        return create_engine(self.db_url, pool_pre_ping=True)
    
    def get_session(self):
        engine = self.get_engine()
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        return SessionLocal()


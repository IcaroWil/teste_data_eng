from fastapi import Depends

from src.db.session import get_source_session

SourceDB = get_source_session
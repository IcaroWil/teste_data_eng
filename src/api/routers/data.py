from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.api.dependencies import SourceDB
from src.db.source_models import Data as SourceData

router = APIRouter(prefix="/data", tags=["data"])

@router.get("")
def get_data(
    start: datetime = Query(..., description="início do intervalo"),
    end: datetime = Query(..., description="fim do intervalo"),
    variables: Optional[list[Literal["wind_speed", "power", "ambient_temperature"]]] = Query(
        None, description="lista de variáveis a retornar"
    ),
    db: Session = Depends(SourceDB),
):
    stmt = select(SourceData).where(and_(SourceData.timestamp >= start, SourceData.timestamp <= end))
    rows = db.execute(stmt).scalars().all()

    result = []
    for row in rows:
        item = {"timestamp": row.timestamp}
        if not variables:
            item["wind_speed"] = row.wind_speed
            item["power"] = row.power
            item["ambient_temperature"] = row.ambient_temperature
        else:
            for v in variables:
                item[v] = getattr(row, v)
        result.append(item)

    return result
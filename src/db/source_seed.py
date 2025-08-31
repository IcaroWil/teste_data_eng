from datetime import datetime, timedelta, timezone
import random

from sqlalchemy import text

from src.db.session import source_engine
from src.db.source_models import Base, Data

def create_schema():
    Base.metadata.create_all(bind=source_engine)

def seed_random_data(days: int = 10):
    start = datetime.now(timezone.utc) - timedelta(days=days)
    end = datetime.now(timezone.utc)
    step = timedelta(minutes=1)

    with source_engine.begin() as conn:
        conn.execute(text("DELETE FROM data"))
        print(f"Gerando dados de {start.strftime('%Y-%m-%d')} até {end.strftime('%Y-%m-%d')}")
        
        current = start
        rows = []
        while current <= end:
            wind_speed = random.uniform(2.0, 15.0)
            power = max(0.0, wind_speed ** 3 * 0.1 + random.uniform(-5.0, 5.0))
            ambient_temperature = random.uniform(10.0, 40.0)
            
            rows.append({
                "timestamp": current,
                "wind_speed": wind_speed,
                "power": power,
                "ambient_temperature": ambient_temperature,
            })

            if len(rows) >= 5000:
                conn.execute(Data.__table__.insert(), rows)
                rows.clear()

            current += step

        if rows:
            conn.execute(Data.__table__.insert(), rows)
        print("Dados gerados!")

if __name__ == "__main__":
    create_schema()
    seed_random_data(10)
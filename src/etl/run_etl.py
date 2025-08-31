from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.session import target_engine, TargetSessionLocal
from src.db.target_models import Base as TargetBase, Signal, Data as TargetData
from src.etl.client import FonteClient
from src.etl.transform import aggregate_10min_long

def ensure_target_schema(session: Session):
    TargetBase.metadata.create_all(bind=target_engine)
    for name in ["wind_speed", "power", "ambient_temperature"]:
        exists = session.scalar(select(Signal).where(Signal.name == name))
        if not exists:
            session.add(Signal(name=name))
    session.commit()

def run_for_date(date_utc: datetime, api_base_url: str = "http://localhost:8000"):
    client = FonteClient(api_base_url)
    day_start = date_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)

    variables = ["wind_speed", "power"]
    print(f"Buscando dados de {day_start.strftime('%Y-%m-%d')}")
    records = client.fetch_data(day_start, day_end, variables)
    print(f"Recebidos {len(records)} registros")

    with TargetSessionLocal() as session:
        ensure_target_schema(session)

        signals = {s.name: s for s in session.execute(select(Signal)).scalars()}

        metric_to_signal = {}
        for var in variables:
            for metric in ["mean", "min", "max", "stddev"]:
                name = f"{var}_{metric}"
                if name not in signals:
                    session.add(Signal(name=name))
                    session.flush()
                    signals[name] = session.execute(select(Signal).where(Signal.name == name)).scalar_one()
                metric_to_signal[(var, metric)] = signals[name]

        for var in variables:
            agg_long = aggregate_10min_long(records, var)
            rows = []
            for r in agg_long.to_dict(orient="records"):
                sig = metric_to_signal[(var, r["metric"])]
                rows.append({
                    "signal_id": sig.id,
                    "timestamp": r["timestamp"],
                    "value": float(r["value"]) if r["value"] == r["value"] else 0.0,
                })
            if rows:
                session.execute(TargetData.__table__.insert(), rows)
                print(f"Salvos {len(rows)} pontos para {var}")
        
        session.commit()

if __name__ == "__main__":
    run_for_date(datetime.now(timezone.utc))
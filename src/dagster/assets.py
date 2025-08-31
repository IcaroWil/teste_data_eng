from datetime import datetime, timedelta, timezone
from dagster import asset, DailyPartitionsDefinition, get_dagster_logger

from src.dagster.resources import SourceDBResource, TargetDBResource
from src.etl.client import FonteClient
from src.etl.transform import aggregate_10min_long
from src.db.target_models import Base as TargetBase, Signal, Data as TargetData
from sqlalchemy import select


daily_partitions = DailyPartitionsDefinition(
    start_date="2025-08-01",
    end_offset=1,
)

@asset(
    partitions_def=daily_partitions,
    description="ETL diário para agregações de 10 minutos",
)
def etl_daily_aggregations(
    context,
    source_db: SourceDBResource,
    target_db: TargetDBResource,
):
    """Executa ETL para uma data específica (partição diária)."""
    logger = get_dagster_logger()
    
    partition_date = context.partition_key
    date_utc = datetime.strptime(partition_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    
    logger.info(f"Iniciando ETL para {partition_date}")
    
    api_base_url = "http://localhost:8000"
    client = FonteClient(api_base_url)
    
    day_start = date_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
    
    variables = ["wind_speed", "power"]
    logger.info(f"Buscando dados de {day_start.strftime('%Y-%m-%d')}")
    
    try:
        records = client.fetch_data(day_start, day_end, variables)
        logger.info(f"Recebidos {len(records)} registros")
    except Exception as e:
        logger.error(f"Erro ao buscar dados da API: {e}")
        raise
    

    with target_db.get_session() as session:
        TargetBase.metadata.create_all(bind=target_db.get_engine())
        
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
        
        total_saved = 0
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
                total_saved += len(rows)
                logger.info(f"Salvos {len(rows)} pontos para {var}")
        
        session.commit()
        logger.info(f"ETL concluído para {partition_date}. Total: {total_saved} pontos salvos.")
        
        return {
            "date": partition_date,
            "records_processed": len(records),
            "points_saved": total_saved,
            "variables": variables
        }

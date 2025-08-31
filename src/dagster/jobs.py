from datetime import datetime
from dagster import job, schedule, RunConfig

from src.dagster.assets import etl_daily_aggregations, daily_partitions

@job(
    description="Job para executar ETL diário de agregações",
    config={
        "resources": {
            "source_db": {
                "config": {
                    "db_url": "postgresql+psycopg2://admin:321@localhost:5432/source_db"
                }
            },
            "target_db": {
                "config": {
                    "db_url": "postgresql+psycopg2://admin:123@localhost:5433/target_db"
                }
            }
        }
    }
)
def etl_job():
    etl_daily_aggregations()

@schedule(
    job=etl_job,
    cron_schedule="0 2 * * *",
    description="Executa ETL diariamente às 02:00",
)
def daily_etl_schedule():
    return RunConfig(
        partition_key=daily_partitions.get_partition_key_for_timestamp(
            datetime.now().timestamp()
        )
    )
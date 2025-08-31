from dagster import Definitions

from src.dagster.assets import etl_daily_aggregations
from src.dagster.jobs import etl_job, daily_etl_schedule
from src.dagster.resources import SourceDBResource, TargetDBResource

defs = Definitions(
    assets=[etl_daily_aggregations],
    jobs=[etl_job],
    schedules=[daily_etl_schedule],
    resources={
        "source_db": SourceDBResource,
        "target_db": TargetDBResource,
    },
)

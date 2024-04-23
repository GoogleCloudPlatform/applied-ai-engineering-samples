from .core import DBConnector
from .PgConnector import PgConnector, pg_specific_data_types
from .BQConnector import BQConnector
from utilities import PROJECT_ID, PG_INSTANCE, PG_DATABASE, PG_USER, PG_PASSWORD, PG_REGION,BQ_REGION,BQ_OPENDATAQNA_DATASET_NAME,BQ_DATASET_NAME,BQ_TABLE_LIST,BQ_LOG_TABLE_NAME

pgconnector = PgConnector(PROJECT_ID, PG_REGION, PG_INSTANCE, PG_DATABASE, PG_USER, PG_PASSWORD)
bqconnector = BQConnector(PROJECT_ID,BQ_REGION,BQ_DATASET_NAME,BQ_OPENDATAQNA_DATASET_NAME,BQ_LOG_TABLE_NAME)


__all__ = ["pgconnector", "pg_specific_data_types", "bqconnector"]
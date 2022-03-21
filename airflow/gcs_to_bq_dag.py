import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

COLOUR_DEF = {
    'yellow': 'tpep_pickup_datetime',
    'green': 'lpep_pickup_datetime'
}

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=3,
    tags=['dtc-gcp'],
) as dag:

    for colour, column in COLOUR_DEF.items():

        gcs_to_gcs = GCSToGCSOperator(
            task_id=f"gcs_to_gcs_{colour}_task",
            source_bucket=BUCKET,
            source_object=f'raw/{colour}_tripdata_2019-*.parquet',
            destination_object=f'{colour}/{colour}_tripdata_2019-',
            destination_bucket=BUCKET,
            move_object=False,
        )

        gcs_to_bq_ext = BigQueryCreateExternalTableOperator(
            task_id=f"gcs_to_bq_ext_{colour}_task",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": f"external_table_{colour}_by_airflow",
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [f"gs://{BUCKET}/{colour}/*"],
                },
            },
        )

        CREATE_PART_TABLE_QUERY = f"CREATE OR REPLACE TABLE dtc-gcp-339512.trips_data_all.external_table_{colour}_by_airflow_partitioned \
            PARTITION BY DATE({column}) AS \
            SELECT * FROM {BIGQUERY_DATASET}.external_table_{colour}_by_airflow;"

        bq_ext_to_part = BigQueryInsertJobOperator(
            task_id=f"bq_ext_to_part_{colour}_task",
            configuration={
                "query": {
                    "query": CREATE_PART_TABLE_QUERY,
                    "useLegacySql": False,
                }
            }
        )

        gcs_to_gcs >> gcs_to_bq_ext >> bq_ext_to_part

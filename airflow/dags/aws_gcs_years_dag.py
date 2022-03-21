import os
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("GCP_BQ_DATASET")
TEMP_STORAGE_PATH = os.getenv('TEMP_STORAGE_PATH', 'not-found')
START_YEAR = int(os.getenv("START_YEAR", "2022"))
END_YEAR = int(os.getenv("END_YEAR", "2022"))
URL_PREFIX = 'https://noaa-ghcn-pds.s3.amazonaws.com'

def format_to_parquet(**kwargs):
    src_file = kwargs['src_file']
    header = kwargs['column_names']
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(
      src_file,
      read_options = pv.ReadOptions(column_names=column_names)
    )
    pq.write_table(table, src_file.replace('.csv', '.parquet'))


def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

default_args = {
    "owner": "airflow",
    "start_date": datetime.now(),
    "end_date": datetime.now() + timedelta(days=1),
    # "start_date": datetime(START_YEAR,1,1),
    # "end_date": datetime(END_YEAR,1,3),
    "depends_on_past": False,
    "retries": 1,
}


# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_years",
    # schedule_interval="0 0 2 1 *",
    schedule_interval="@once",
    default_args=default_args,
    # catchup=True,
    catchup=False,
    max_active_runs=3,
    tags=['ghcnd'],
) as dag:


    year = '{{dag_run.logical_date.strftime("%Y")}}'
    year = 1888
    column_names = ['id','date','element','value','m_flag','q_flag','s_flag','obs_time']
    csv_file_name = f'/{year}.csv'
    dataset_url = URL_PREFIX + '/csv' + csv_file_name
    csv_file_path = TEMP_STORAGE_PATH + csv_file_name
    parquet_file_name = csv_file_name.replace('.csv', '.parquet')
    parquet_file_path = TEMP_STORAGE_PATH + parquet_file_name
    parquet_object_path = f"raw{parquet_file_name}"
    parquet_uri = f"gs://{BUCKET}/{parquet_object_path}"
    external_table_name = f"external_table_{year}"
    table_name = f"{year}"

    download_dataset_task = BashOperator(
        task_id=f"download_dataset_task",
        bash_command=f"curl -sS {dataset_url} > {csv_file_path}"
    )

    format_to_parquet_task = PythonOperator(
        task_id=f"format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": csv_file_path,
            "column_names": column_names
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id=f"local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw{parquet_file_name}",
            "local_file": parquet_file_path
        },
    )

    clear_local_files = BashOperator(
        task_id=f"clear_local_files",
        bash_command=f"rm {csv_file_path} {parquet_file_path}"
    )

    gcs_to_bq_ext = BigQueryCreateExternalTableOperator(
        task_id=f"gcs_to_bq_ext_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": external_table_name,
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [parquet_uri],
            },
        },
    )

    CREATE_TABLE_QUERY = f"CREATE OR REPLACE TABLE {PROJECT_ID}.{BIGQUERY_DATASET}.{table_name} \
        PARTITION BY parsed_date \
        CLUSTER BY id AS \
        SELECT PARSE_DATE('%Y%m%d', CAST(date AS string)) as parsed_date, * FROM {PROJECT_ID}.{BIGQUERY_DATASET}.{external_table_name};"

    bq_ext_to_part = BigQueryInsertJobOperator(
        task_id=f"bq_ext_to_table_task",
        configuration={
            "query": {
                "query": CREATE_TABLE_QUERY,
                "useLegacySql": False,
            }
        }
    )

    download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> clear_local_files >> gcs_to_bq_ext >> bq_ext_to_part


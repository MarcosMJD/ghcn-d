import os
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
TEMP_STORAGE_PATH = os.getenv('TEMP_STORAGE_PATH', 'not-found')
URL_PREFIX = 'https://s3.amazonaws.com/nyc-tlc/misc'

csv_file_name = '/taxi+_zone_lookup.csv'
dataset_url = URL_PREFIX + csv_file_name
csv_path = TEMP_STORAGE_PATH + csv_file_name
parquet_file_name = csv_file_name.replace('.csv', '.parquet')
parquet_path = TEMP_STORAGE_PATH + parquet_file_name

def format_to_parquet(**kwargs):
    src_file = kwargs['src_file']
    task = kwargs['ti']
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    parquet_path = src_file.replace('.csv', '.parquet')
    pq.write_table(table, parquet_path)
    task.xcom_push(key='parquet_file', value=parquet_path)


# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, **kwargs):
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

    task = kwargs['ti']
    local_file = task.xcom_pull(key='parquet_file', task_ids=['format_to_parquet_task'])[0]

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

default_args = {
    "owner": "airflow",
    "start_date": datetime.now(),
    "end_date": datetime.now() + timedelta(days=1),
    "depends_on_past": False,
    "retries": 1,
}


# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_zones_dag_homework",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-gcp-zones-homework'],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"curl -sS {dataset_url} > {csv_path}"
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        provide_context=True,
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": csv_path
        },
    )

    # TODO: Homework - research and try XCOM to communicate output values between 2 tasks/operators
    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        provide_context=True,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw{parquet_file_name}",
        },
    )

    clear_local_files = BashOperator(
        task_id="clear_local_files",
        bash_command=f"rm {csv_path} {parquet_path}"
    )

    download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> clear_local_files
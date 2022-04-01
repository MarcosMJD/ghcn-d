import os
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("GCP_BQ_DATASET")
REGION=os.environ.get("GCP_REGION")
START_YEAR = int(os.getenv("START_YEAR", "2022"))
DATAPROC_CLUSTER = 'ghcnd'

default_args = {
    "owner": "airflow",
    "start_date": datetime.now() - timedelta(days=2),
    "depends_on_past": False,
    "retries": 0,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_transformation_dataproc_spark_job",
    schedule_interval="0 6 * * *",
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    tags=['ghcnd'],
) as dag:

    END_YEAR = '{{dag_run.logical_date.strftime("%Y")}}'

    submit_dataproc_spark_job_task = BashOperator(
        task_id="submit_dataproc_spark_job_task",
        bash_command= ( f"gcloud dataproc jobs submit pyspark "
        "../spark/process_year_tables.py "
        f"--cluster={DATAPROC_CLUSTER} "
        f"--region={REGION} "
        f"--jars '../spark/spark-bigquery-with-dependencies_2.12-0.24.0.jar' "
        f"-- {START_YEAR} {END_YEAR}" 
        )
    )

    SPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": DATAPROC_CLUSTER},
    "pyspark_job": {"main_python_file_uri": "../spark/process_year_tables.py"},
    "jar_file_uris": ["../spark/spark-bigquery-with-dependencies_2.12-0.24.0.jar"],
    },
}
pyspark_task = DataprocSubmitJobOperator(
    task_id="submit_dataproc_spark_job_task", job="../spark/process_year_tables.py", region=REGION, project_id=PROJECT_ID
)
    submit_dataproc_spark_job_task   


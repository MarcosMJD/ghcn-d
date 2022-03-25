#!/bin/bash
set -a

# EDIT these vars to match those when seting up requirements and virtual mahine
GOOGLE_APPLICATION_CREDENTIALS_FOLDER="/home/marcos/.google/credentials/"
GOOGLE_APPLICATION_CREDENTIALS_FILE="ghcn-d-698480b9cb8d.json"
GCP_PROJECT_ID=ghcn-d
GCP_PROJECT_REGION=europe-west6
GCP_PROJECT_DATA_LAKE_NAME=ghcnd_raw
GCP_PROJECT_BQ_DATASET_NAME=ghcnd
# GCP_PROJECT_BQ_DATASET_DBT_DEV shoud be <first initial><last name> where these are 
# the first name and last name used when creating the dbt cloud account.
# E.g. Marcos Jimenez -> mjimenez
GCP_PROJECT_BQ_DATASET_DBT_DEV=mjimenez
# This refers to the past years to be processed. From 1763 to 2021.
# Please note that from 1961 each year takes more than 1GiB. 
START_YEAR=2000



#
# DO NOT edit the following
#
AIRFLOW_UID=$(id -u)
GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS_FOLDER}${GOOGLE_APPLICATION_CREDENTIALS_FILE}
TF_VAR_PROJECT=${GCP_PROJECT_ID}
TF_VAR_REGION=${GCP_PROJECT_REGION}
TF_VAR_DATA_LAKE_BUCKET=${GCP_PROJECT_DATA_LAKE_NAME}
TF_VAR_BQ_DATASET=${GCP_PROJECT_BQ_DATASET_NAME}
TF_VAR_BQ_DATASET_DBT_DEV="dbt_${GCP_PROJECT_BQ_DATASET_DBT_DEV}"
set +a
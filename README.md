# Global Historical Climatology Network Daily Data Pipeline

## Project requirements

Build a dashboard with two tiles.  
- Select a dataset.
- Create a pipeline for processing this dataset and putting it to a datalake.
- Create a pipeline for moving the data from the lake to a data warehouse.
- Transform the data in the data warehouse: prepare it for the dashboard.
- Create a dashboard.

## Problem statement
Global historical weather data is large, collected from year 1763 until today. There are over 160K weather stations across the world, each of them generating several observations on a daily basis. This sum up a total of more than 1.75B overvations.  
The data is also not ready to perform analytics tasks over the entire dataset or that require integrated geolocation information.
All this information has to be processed (ELT) to enable analitics tasks covering information from several years, locations, observation date and type ans so on  
As an example:  
- Max daily temperature in France (over all territory) in 1992.
- Plot a comparison of the main daily minimum temperature by year between NewYork and Miami.
- Overall ten hottest days in Madrid.
It is advisable that joins and aggregations will be needed for such kind of analysis.

## Main objective
Develop the data infrastructure including data pipeline and dashboard for users to perform advanced analytics tasks on the global historical weather data.

## Dataset description

### NOAA Global Historical Climatology Network Daily (GHCN-D)
[Global Historical Climatology Network - Daily](https://github.com/awslabs/open-data-docs/tree/main/docs/noaa/noaa-ghcn) is a dataset from NOAA that contains daily observations over global land areas (e.g. TMAX, SNOW...). It contains station-based observations from land-based stations worldwide. It is updated daily. The data is in CSV format. Each file corresponds to a year from 1763 to present and is named as such.  
Each file contains all weather observations from all the stations for all days in that year.  
Data description of the stations, including geolocation is available in a separate file.  

Information of all stations is stored in a specific file.
File format examples:
- http://noaa-ghcn-pds.s3.amazonaws.com/csv.gz/1788.csv.gz
- http://noaa-ghcn-pds.s3.amazonaws.com/csv.gz/1788.csv
- http://noaa-ghcn-pds.s3.amazonaws.com/ghcnd-stations.txt


## Technologies
- Cloud: GCP
- Infrastructure as code (IaC): Terraform
- Workflow orchestration: Airflow
- Data Wareshouse: BigQuery
- Data Lake: GCS
- Batch processing/Transformations: Dbt and Spark
- Stream processing: None
- Dashboard: Google Data Studio

## Proposal to address the requirements
- Infraestructure as code: Use Terraform to create a bucket GCS and dataset in BQ
  - ghcdn_raw bucket to store parquet files.
  - dhcdn dataset for the ingestion into BigQuery.
  - dbt_xxxx dataset for dbt development environment.
  - production dataset for dbt production environment.
- Data ingestion: Use Airflow to get data from AWS bucket to CGS and then to BigQuery:  
  - Dag aws_gcs_other_stasets_dag to ingest stations and countries data only once.  
    - stations and countries are txt files, so need to be transformed to csv and then to parquet files.  
  - Dag aws_gcs_past_years_dag to ingest observations from last years (until 2021) on a yearly basis with cathup:  
  - Dag aws_gcs_current_year_dag to ingest observations from current year on a dayly basis (cathup of only one day):  
    To accelerate queries and data processing, each table of year (with observations) has been partitioned by date of observation and clustered by station.  
    Original date type integer from parquet file schema is transformed to date when generating BigQuery table in order to be able to partition by time.  
- Transformations: Use dbt to perform unions, joins and aggregations on BQ.  
  - Stage:  
    - Stations and countries: Create staged model from stations and countries tables in Big Query.  
      - In the stations model, extract country_code field from the station id field.  
    - Years:
      - Option 1 (discarded). Create staged model (view) for each year. 
        The number of years may be too large, there is a one to one restriction model-table in dbt. 
      - Option 2: Create a fact_observations model that will loop through all Big Query year tables and transforming them and inioning them.  
        Transformation for each year table: each row will have all observations for a day from a station. This will save space and will perform better. In case of several observations (by a single station) of the same type in the same day, observations are averaged. tmax, tmin and prcp observations are converted to degree and mm.
        In order to allow partitioning by year, a new field partition_date is generated with year-1-1 as the date for all observations for that year.
        The transformation is implemented as a macro (process_year_table)
    - Job:
      - For the creation of the production dataset, a job has been created. 
  - Core:
    - Create fact_observations materialized model by joining years with station and country tables. Generated table will be partitioned by partition_date and clustered by country_code and station id.

- Dashboard: Connect Google Data Studio to BQ dataset and design dashboard  
- Orchestration: Use Airflow to orchestrate data ingestion. Use dbt jobs to orchestrate transformation pipeline.  

## Results

## Setup and running

Terraform and Airflow will run as containers in a VM in Google Cloud.
Dbt cloud will be used to perform data transformation pipeline

### Requirements
1. Google Cloud Platform account and project
2. Virtual Machine in Google Cloud Compute Engine
3. dbt cloud account
  
### Setup environment on a Virtual Machine
- VM on GCP
  - Installation of tools. Terraform, Airflow, dbt?, spark, AWS cli

### Run pipeline
- Edit setup.sh
  - Set START_YEAR. 
- Run source setup.sh to apply the configuration
- Terraform
  - cd terraform
  - terraform init
  - terraform plan
  - terraform apply yes
- Airflow
  - cd ..
  - cd airflow
  - docker-compose build
  - docker-compose up airflow-init
  - docker-compose up
  - run data_ingestion_ghcn_other_datasets
  - run data_ingestion_past_years. This may take long.
  - run data_ingestion_current_year for current year (2022)
- dbt
  - Edit the dbt job 'dbt build' to run the following command with the specific range of years:  
    `dbt run --vars "{'is_test_run': true,'start_year':2000,'end_year':2022}"`  
  Note: start_year and end_year defines the range of years to be processed. Be coherent.
- Google Data Studio
  - Log in datastudio.google.com
  - Create Data Source -> BigQuery
  - Select project, dataset and table: ghcn-d -> ghcnd -> fact_observations -> Connect
  - Create Report -> Add to report



## ToDo

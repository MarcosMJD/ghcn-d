# GCP

## Create a GCP account

## Create a new project in GCP

When creating a project, use a project id that is unique, edit it since it can not be modified later on. Use the following projecy name and id: 
    Project name = project id = ghcn-d
Select the project

## Create a service account

Sercice account authorize applications to perform authotised API calls. They are not user accounts of Google Workspace Domain  
Go to IAM -> Service accounts
- Add one service account
  - Fill the details
  - Add Viewer role (plain viewer role)
  - No need to grant access to multiple users
- Create keys in the service account
  - Actions icon -> Manage Keys -> AddKey -> Create new key -> Create
  - Save the json in a safe directory.
    - Windows: `C:\Users\USERNAME\.google\credentials\...json`
    - Linux: `${HOME}/.google/credentials/...json`

## Set up permissions to the service account for GCS y Big Query

- Go to IAM & Admin -> IAM
- Edit the service account icon -> Edit principal
- Add the following roles:
  - Storage Admin
  - Storage Object Admin
  - BigQuery Admin

## Enable APIs for the SDK to communicate though IAM
https://console.cloud.google.com/apis/library/iam.googleapis.com

## Enable APIs 
Be sure to have enabled the following APIs for your project in the GCP account:
- Compute Engine
- Cloud Storage
- BigQuery

# DBT
Create a free dbt cloud account using this link https://www.getdbt.com/signup/
Note that the name and last name are used to create a dataset in BigQuery for development. E.g Marcos Jimenez -> mjimenez
Create a dbt cloud project:
Detailed instructions can be found here: https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/dbt_cloud_setup.md#create-a-dbt-cloud-project
- Main menu -> Account -> Projects -> New Project
  - Name: ghcn-d
  - Advanced settings: Project subdirectory: dbt
  - BigQuery
  - Upload a Service Account JSON file: Use the credentials file generated when setting up GPC account
  - Test
  - Continue
  - Git Clone -> Git URL: git@github.com:YOUR_GIT_USERNAME/ghcn-d.git
  - Import
  - Copy the generated deployment key
  - Go to your git provider (e.g. github) and edit the configuration of the project ghcn-d. 
    - Settings (Settings tab in the GitHub repository page)
    - Deploy keys
    - Add deploy keys
      - Name dbt
      - Paste the key
      - Allow write access
      - Add key
  - Continue







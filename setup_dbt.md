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
  - Go to your git provider (e.g. github) and edit the configuration of the project ghcn-d:  
    - Settings (Settings tab in the GitHub repository page)
    - Deploy keys
    - Add deploy keys
      - Name dbt
      - Paste the key
      - Allow write access
      - Add key
  - Continue
  - Skip & Complete
  - Create a production environment:
    - Click Main Menu icon -> Environments
    - New Environment
    - Name: production
    - Type: deployment
    - Dataset: production
    - Save







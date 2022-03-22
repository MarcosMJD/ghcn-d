{{ config(materizalied='view')}}

select * from {{ source('staging','stations') }}
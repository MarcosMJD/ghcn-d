{{ config(materialized='table') }}

select
    years.id,
    years.parsed_date,
    years.partition_date,
    years.tmax,
    years.tmin,
    years.prcp,
    years.snow,
    years.snwd,
    years.m_flag,
    years.q_flag,
    years.s_flag,
    stations.name as station_name,
    stations.latitude,
    stations.longitude,
    stations.elevation,
    stations.country_code,
    countries.name as country_name
from {{ ref('stg_years_loop') }} as years
inner join {{ ref('stg_stations') }} as stations
on years.id = stations.id
inner join {{ ref('stg_countries') }} as countries
on stations.country_code = countries.code
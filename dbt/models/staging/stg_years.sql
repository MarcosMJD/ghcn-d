{{ config(materialized='view') }}

with averaged as
(
    with exploded as 
    ( 
        select
            id,
            parsed_date,
            case
                when element = 'TMAX' THEN cast(value/10 as numeric)
                else null
            end as tmax,
            case
                when element = 'TMIN' THEN cast(value/10 as numeric)
                else null
            end as tmin,
            case
                when element = 'PRCP' THEN cast(value/10 as numeric)
                else null
            end as prcp,
            case
                when element = 'SNOW' THEN cast(value as numeric)
                else null
            end as snow,
            case
                when element = 'SNWD' THEN cast(value as numeric)
                else null
            end as snwd,
            m_flag,
            q_flag,
            s_flag,
        from {{ source('staging_years','1888') }}
    )
    select
        id,
        parsed_date,
        m_flag,
        q_flag,
        s_flag,
        avg(tmax) over (partition by id, parsed_date) as tmax,
        avg(tmin) over (partition by id, parsed_date) as tmin,
        avg(prcp) over (partition by id, parsed_date) as prcp,
        avg(snow) over (partition by id, parsed_date) as snow,
        avg(snwd) over (partition by id, parsed_date) as snwd,
        row_number() over (partition by id, parsed_date) as rn
    from exploded
)
select 
    id,
    parsed_date,
    date (extract(year from parsed_date),1,1) as partition_date,
    tmax,
    tmin,
    prcp,
    snow,
    snwd,
    m_flag,
    q_flag,
    s_flag
from averaged
where rn = 1

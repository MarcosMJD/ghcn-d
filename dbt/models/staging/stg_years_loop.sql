{{ config(materialized='view') }}

{% for year in var('years') %}
    {{ process_year_table(year.name) }}
    {{ 'union all' if not loop.last }}
{% endfor %}


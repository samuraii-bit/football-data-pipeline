{{ config(materialized='view') }}

with ranked_matches as (
    select
        (raw_data->>'id')::int as match_id,
        (raw_data->>'utcDate')::timestamp as match_date,
        raw_data->'status' as match_status,
        raw_data->'homeTeam'->>'name' as home_team,
        raw_data->'awayTeam'->>'name' as away_team,
        (raw_data->'score'->'fullTime'->>'home')::int as home_score,
        (raw_data->'score'->'fullTime'->>'away')::int as away_score,
        loaded_at,
        row_number() over (partition by (raw_data->>'id')::int order by loaded_at desc) as rn
    from {{ source('public', 'raw_matches') }}
)

select
    match_id,
    match_date,
    match_status,
    home_team,
    away_team,
    home_score,
    away_score,
    loaded_at
from ranked_matches
where rn = 1  -- Берем самую последнюю версию матча по времени загрузки
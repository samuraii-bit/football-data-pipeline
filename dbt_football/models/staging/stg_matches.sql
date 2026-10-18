{{ config(materialized='view') }}

with raw as (
    select * from {{ source('raw_data', 'raw_matches') }}
)

select
    (match_data->>'id')::int as match_id,
    (match_data->>'utcDate')::timestamp as match_date,
    match_data->>'status' as match_status,
    (match_data->'homeTeam'->>'id')::int as home_team_id,
    match_data->'homeTeam'->>'name' as home_team_name,
    (match_data->'awayTeam'->>'id')::int as away_team_id,
    match_data->'awayTeam'->>'name' as away_team_name,
    (match_data->'score'->'fullTime'->>'home')::int as home_score,
    (match_data->'score'->'fullTime'->>'away')::int as away_score
from raw
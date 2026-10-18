with ranked_matches as (
    select
        (match_data->>'id')::int                        as match_id,
        (match_data->>'utcDate')::timestamp             as match_date,
        match_data->>'status'                           as match_status,
        match_data->'homeTeam'->>'name'                 as home_team_name,
        match_data->'awayTeam'->>'name'                 as away_team_name,
        (match_data->'score'->'fullTime'->>'home')::int as home_score,
        (match_data->'score'->'fullTime'->>'away')::int as away_score,
        loaded_at,
        id,
        row_number() over (
            partition by (match_data->>'id')::int
            order by loaded_at desc, id desc
        ) as rn
    from {{ source('raw_data', 'raw_matches') }}
)

select
    match_id,
    match_date,
    match_status,
    home_team_name,
    away_team_name,
    home_score,
    away_score,
    loaded_at
from ranked_matches
where rn = 1
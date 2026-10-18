select 
    match_id,
    home_team_name,
    away_team_name,
    home_score,
    away_score
from {{ ref('stg_matches') }}
where home_score < 0 or away_score < 0
   or home_score > 20 or away_score > 20 /* обычно больше 10 не забивают, а 20 и подавно... */
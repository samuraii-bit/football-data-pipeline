import os
import requests
import json
from sqlalchemy import create_engine, text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONN = "postgresql://postgres:postgres@postgres:5432/football_dwh"
COMPETITION_CODE = "PL"
API_URL = f"https://api.football-data.org/v4/competitions/{COMPETITION_CODE}/matches"
FOOTBALL_DATA_API_TOKEN = os.getenv("FOOTBALL_DATA_API_TOKEN")

def save_raw_data():
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_TOKEN}
    print(f"Запрос данных для лиги {COMPETITION_CODE}...")
    response = requests.get(API_URL, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"Ошибка API: {response.status_code}")
    
    data = response.json()
    matches = data.get("matches", [])
    
    if not matches:
        print("Матчи не найдены.")
        return

    engine = create_engine(DB_CONN)

    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_matches (
        id SERIAL PRIMARY KEY,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        match_id INT,
        match_data JSONB
    );
    """
    
    with engine.begin() as connection:
        connection.execute(text(create_table_query))

        connection.execute(text("TRUNCATE TABLE raw_matches;"))

        for match in matches:
            match_id = match.get("id")
            connection.execute(
                text("INSERT INTO raw_matches (match_id, match_data) VALUES (:m_id, :m_data)"),
                {"m_id": match_id, "m_data": json.dumps(match)}
            )

    print(f"Успешно сохранено {len(matches)} матчей в таблицу raw_matches базы PostgreSQL!")

if __name__ == "__main__":
    save_raw_data()
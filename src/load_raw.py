from datetime import datetime
import json
import os
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_CONN = os.getenv(
    "DB_CONN", "postgresql://postgres:postgres@postgres:5432/football_dwh"
)
COMPETITION_CODE = "PL"
API_URL = f"https://api.football-data.org/v4/competitions/{COMPETITION_CODE}/matches"
FOOTBALL_DATA_API_TOKEN = os.getenv("FOOTBALL_DATA_API_TOKEN")



def save_raw_data(**context):
  if not FOOTBALL_DATA_API_TOKEN:
    raise ValueError("Критическая ошибка: Переменная FOOTBALL_DATA_API_TOKEN не задана!")

  headers = {"X-Auth-Token": FOOTBALL_DATA_API_TOKEN}
  print("Запрос данных из Football-Data API...")

  try:
    response = requests.get(API_URL, headers=headers, timeout=(5, 30))
    response.raise_for_status()  генерация исключения при 4xx/5xx
  except requests.exceptions.RequestException as e:
    raise RuntimeError(f"Ошибка соединения с API: {e}")

  data = response.json()
  matches = data.get("matches", [])


  if not isinstance(matches, list) or len(matches) == 0:
    raise ValueError("API вернул пустой список матчей или некорректную структуру данных!")

  
  sample_match = matches[0]
  required_keys = ["id", "utcDate", "status", "homeTeam", "awayTeam"]
  for key in required_keys:
    if key not in sample_match:
      raise ValueError(f"Нарушение контракта API: отсутствует обязательное поле '{key}'")

  engine = create_engine(DB_CONN)
  load_timestamp = datetime.utcnow()
  
  run_id = context.get("dag_run").run_id if "dag_run" in context else "manual_run"

  create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_matches (
        id SERIAL PRIMARY KEY,
        match_id INT,
        raw_data JSONB,
        loaded_at TIMESTAMP,
        run_id VARCHAR(255)
    );
    """

  with engine.begin() as connection:
    connection.execute(text(create_table_query))

    inserted_count = 0
    for match in matches:
      match_id = match.get("id")
      if not match_id:
        continue

      connection.execute(
          text("""
                INSERT INTO raw_matches (match_id, raw_data, loaded_at, run_id)
                VALUES (:match_id, :raw_data, :loaded_at, :run_id)
            """),
          {
              "match_id": match_id,
              "raw_data": json.dumps(match),  # Передаем как JSON-строку для JSONB
              "loaded_at": load_timestamp,
              "run_id": run_id,
          },
      )
      inserted_count += 1

  print(f"Успешно сохранено {inserted_count} записей в raw_matches (run_id: {run_id}).")


if __name__ == "__main__":
  save_raw_data()
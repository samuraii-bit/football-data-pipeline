import os 
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

COMPETITION_CODE = "PL"

API_URL = f"https://api.football-data.org/v4/competitions/{COMPETITION_CODE}/matches"

FOOTBALL_DATA_API_TOKEN = os.getenv("FOOTBALL_DATA_API_TOKEN")

def fetch_matches():
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_TOKEN }

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запрашиваем данные для лиги: {COMPETITION_CODE}...")

    response = requests.get(API_URL, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"Ошибка API: статус-код {response.status_code}, ответ: {response.text}")
    
    data = response.json()

    matches = data.get("matches", [])
    if not matches:
        print("ВНИМАНИЕ: Список матчей пуст!")
        return []
    
    print(f"Успешно получено матчей: {len(matches)}")

    sample_match = matches[0]
    required_keys = ["id", "utcDate", "status", "homeTeam", "awayTeam", "score"]
    missing_keys = [key for key in required_keys if key not in sample_match]
    
    if missing_keys:
        print(f"ОШИБКА КАЧЕСТВА ДАННЫХ: Нарушена схема JSON! Отсутствуют ключи: {missing_keys}")
    else:
        print("Data Quality Check пройден: Схема ответа соответствует спецификации.")
        
    return matches

if __name__ == "__main__":
    try:
        matches_data = fetch_matches()
        if matches_data:
            # Выведем информацию о первом матче для наглядности
            first_match = matches_data[0]
            home = first_match["homeTeam"]["name"]
            away = first_match["awayTeam"]["name"]
            score = first_match["score"]["fullTime"]
            date = first_match["utcDate"]
            print(f"\nПример матча: {home} vs {away} | Счет: {score['home']}:{score['away']} | Дата: {date}")
    except Exception as e:
        print(f"Ошибка выполнения пайплайна: {e}")
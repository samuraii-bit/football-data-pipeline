# Football Data Pipeline & Quality Framework

Сквозной аналитический ETL-пайплайн для сбора, трансформации и автоматического тестирования футбольной статистики. Проект ориентирован на практическую реализацию принципов Data Quality и Data Testing (Data QA) с использованием современного стека разработки.

## Архитектура проекта

```text
[Football-Data REST API] 
         │ (Python / Requests)
         ▼
[PostgreSQL: Raw Storage (JSONB)]
         │
         ▼
[dbt: Staging Layer & Business Models]
         │
         ▼
[dbt test: Data Quality Validation]
         ▲
         │ (Оркестрация по расписанию)
[Apache Airflow (Docker)]
```

## Стек технологий

* **Язык программирования:** Python 3.10 (requests, sqlalchemy, psycopg2)
* **Хранилище данных (DWH):** PostgreSQL 15
* **Трансформация и тестирование:** dbt (data build tool)
* **Оркестрация:** Apache Airflow
* **Инфраструктура:** Docker, Docker Compose

---

## Структура репозитория

```text
football-data-pipeline/
├── dags/
│   └── football_pipeline_dag.py     # DAG оркестратора Airflow
├── dbt_football/
│   ├── models/
│   │   └── staging/
│   │       ├── stg_matches.sql      # SQL-модель очистки и распаковки сырых данных
│   │       └── schema.yml           # Декларативные тесты полей (unique, not_null)
│   ├── tests/
│   │   └── assert_no_negative_scores.sql # Кастомный бизнес-тест на аномалии счета
│   └── profiles.yml                 # Конфигурация подключения dbt к БД
├── src/
│   ├── extract.py                   # Скрипт валидации и запроса данных из API
│   └── load_raw.py                  # Загрузка JSON-ответов в таблицу raw_matches
├── docker-compose.yml               # Конфигурация контейнеров PostgreSQL и Airflow
├── requirements.txt                 # Зависимости Python
└── README.md

```

## Инструкция по запуску

### 1. Клонирование репозитория и настройка окружения

Создайте файл `.env` в корне проекта или укажите токен API непосредственно в конфигурации. Для работы требуется полученный токен на сайте football-data.org.

### 2. Запуск инфраструктуры (Docker Compose)

В корневой директории проекта выполните команду:

```bash
docker compose up -d
```

Команда поднимет контейнеры с PostgreSQL (порт 5432) и Apache Airflow (порт 8080).

### 3. Ручной запуск пайплайна

- Перейдите в веб-интерфейс Airflow по адресу http://localhost:8080 (логин/пароль по умолчанию: admin / admin, или их можно найти в логах).
- Найдите DAG с именем `football_data_quality_pipeline` и активируйте его.
- Нажмите кнопку **Trigger DAG** для ручного запуска полного цикла: выгрузка сырых данных в хранилище, выполнение трансформаций через `dbt run` и запуск тестов качества через `dbt test`.
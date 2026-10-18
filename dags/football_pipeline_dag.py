from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.append('/opt/airflow')
from src.load_raw import save_raw_data

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'football_data_quality_pipeline',
    default_args=default_args,
    description='Пайплайн сбора футбольной статистики с контролем качества данных через dbt',
    schedule_interval='0 6 * * *',  # Запуск каждый день в 06:00
    catchup=False,
) as dag:

    # Загрузка сырых данных из API
    extract_and_load_raw = PythonOperator(
        task_id='extract_and_load_raw',
        python_callable=save_raw_data,
    )

    # Трансформация данных через dbt
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt_football && dbt run --profiles-dir .',
    )

    # Тестирование качества данных через dbt
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt_football && dbt test --profiles-dir .',
    )

    # Порядок выполнения (Dependencies)
    extract_and_load_raw >> dbt_run >> dbt_test
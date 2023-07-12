from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'check_sqlite_database',
    default_args=default_args,
    description='Check the contents of the SQLite database and log the results',
    schedule_interval=timedelta(days=1),
)

def check_database():
    hook = SqliteHook(sqlite_conn_id='sqlite_default')
    rows = hook.get_records('SELECT * FROM episodes')
    for row in rows:
        print(row)

check_database_task = PythonOperator(
    task_id='check_database',
    python_callable=check_database,
    dag=dag,
)

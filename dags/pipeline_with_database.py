from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from datetime import timedelta
import pendulum
import requests
import xmltodict

local_tz = pendulum.timezone("America/Los_Angeles")

@dag(dag_id='marketplace_podcast_withDB',default_args={'owner': 'airflow'}, schedule_interval=timedelta(days=1), start_date=pendulum.datetime(2022, 1, 1, tz=local_tz), catchup=False)
def marketplace_podcast():
    @task()
    def download_parse_extract():
        url = 'https://www.marketplace.org/feed/podcast/marketplace/'
        response = requests.get(url)
        data = xmltodict.parse(response.content)
        episodes = data['rss']['channel']['item']
        return episodes

    create_table = SqliteOperator(
        task_id='create_table',
        sqlite_conn_id='sqlite_default',
        sql='''
            CREATE TABLE IF NOT EXISTS episodes (
                link TEXT,
                title TEXT,
                filename TEXT,
                pubDate TEXT,
                description TEXT,
                transcript TEXT
            );
        '''
    )

    download_parse_extract() >> create_table

marketplace_podcast_dag = marketplace_podcast()

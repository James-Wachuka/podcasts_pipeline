from airflow.decorators import dag, task
from airflow.providers.sqlite.hooks.sqlite import SqliteHook
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from datetime import timedelta
import pendulum
import requests
import xmltodict

local_tz = pendulum.timezone("America/Los_Angeles")

@dag(dag_id='storing_data_dag',default_args={'owner': 'airflow'}, schedule_interval=timedelta(days=1), start_date=pendulum.datetime(2022, 1, 1, tz=local_tz), catchup=False)
def marketplace_podcast():
    @task()
    def download_parse_extract():
        url = 'https://www.marketplace.org/feed/podcast/marketplace/'
        response = requests.get(url)
        data = xmltodict.parse(response.content)
        episodes = data['rss']['channel']['item']
        return episodes

    @task()
    def load_to_db(episodes):
        hook = SqliteHook(sqlite_conn_id='sqlite_default')
        stored_episodes = hook.get_records('SELECT link FROM episodes')
        stored_episodes = [episode[0] for episode in stored_episodes]
        for episode in episodes:
            if episode['link'] not in stored_episodes:
                filename = episode['link'].split('/')[-1]
                hook.run(f"INSERT INTO episodes VALUES ('{episode['link']}', '{episode['title']}', '{filename}', '{episode['pubDate']}', '{episode['description']}', NULL)")
    
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

    download_task = download_parse_extract()
    load_task = load_to_db(download_task)
    download_task >> create_table >> load_task

marketplace_podcast_dag = marketplace_podcast()

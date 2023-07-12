from airflow.decorators import dag, task
from datetime import timedelta
import pendulum
import requests
import xmltodict

local_tz = pendulum.timezone("America/Los_Angeles")

@dag(default_args={'owner': 'airflow'}, schedule_interval=timedelta(days=1), start_date=pendulum.datetime(2022, 1, 1, tz=local_tz), catchup=False)
def marketplace_podcast():
    @task()
    def download_parse_extract():
        url = 'https://www.marketplace.org/feed/podcast/marketplace/'
        response = requests.get(url)
        data = xmltodict.parse(response.content)
        episodes = data['rss']['channel']['item']
        return episodes

    download_parse_extract()

marketplace_podcast_dag = marketplace_podcast()

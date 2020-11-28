# -*- coding: utf-8 -*-
import logging
import socket
import time
from datetime import datetime

import requests

from monitor_api.errors import PostError, GetSourceError
from utils.json_helper import read_json_from_file


class MonitorApi:
    def __init__(self):
        self.api_url = read_json_from_file('resources/config.json')['api_url']

    def get_sources(self):
        url = f'{self.api_url}/monitor/api/sources'
        for i in range(10):
            try:
                req = requests.get(url)
                if req.status_code != 200:
                    raise GetSourceError(f'{datetime.now()} - Ошибка получения источников - {req.status_code}')
                logging.info(f'{datetime.now()} - {req.status_code}. Источники получены')
                return req.json()
            except (Exception, socket.gaierror) as e:
                logging.error(f'{datetime.now()} - {e.__class__} - {e} - Источники не получены.')
                time.sleep(10)
        raise Exception(f'{datetime.now()} - Источники не получены.')

    def update_source(self, info, source_id):
        url_put = f'{self.api_url}/monitor/api/sources/{source_id}/?format=json'
        payload = info.encode('utf-8')
        headers_post = {
            'Content-Type': 'application/json'
        }
        for i in range(10):
            try:
                response = requests.request("PUT", url_put, headers=headers_post, data=payload)
                if response.status_code != 200:
                    raise PostError(f'{datetime.now()} - Ошибка - {response.status_code}')
                logging.info(f'{datetime.now()} - Данные отправлены успешно. Код - {response.status_code}')
                return
            except Exception as e:
                logging.error(f'{datetime.now()} - {e.__class__} - {e} - Данные не отправлены.')
                time.sleep(10)
        logging.error(f'{datetime.now()} - Данные не отправлены')

    def add_subscribers(self, subscribers):
        url_post = f"{self.api_url}/monitor/api/stats/"
        payload = subscribers.encode('utf-8')
        headers_post = {
            'Content-Type': 'application/json'
        }
        for i in range(10):
            try:
                response = requests.request("POST", url_post, headers=headers_post, data=payload)
                if response.status_code != 201:
                    raise PostError(f'{datetime.now()} - Ошибка - {response.status_code}')
                logging.info(f'{datetime.now()} - Данные отправлены успешно. Код - {response.status_code}')
                return
            except Exception as e:
                logging.error(f'{datetime.now()} - {e.__class__} - {e} - Данные не отправлены.')
                time.sleep(10)
        logging.error(f'{datetime.now()} - Данные не отправлены')

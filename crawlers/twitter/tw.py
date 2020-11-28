import logging
import time
from datetime import datetime
from urllib.error import URLError

import requests
import ujson
from utils.json_helper import write_json_to_file, dump, read_json_from_file
from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from crawlers.crawler import Crawler
from crawlers.errors import RequestError, GetInfoError

logging.basicConfig(level='INFO')


class Tw(Crawler):
    def __init__(self):
        super().__init__()
        self.config = read_json_from_file('resources/config.json')
        self.selenium_server_url = self.config['tw_server_url']
        self.guest_token = self.config['tw_guest_token']
        self.remote = self.config['remote']
        self.auth_token = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs' \
                          '%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
        self.graphql_endpoint = 'E4iSsd6gypGFWx2eUhSC1g'
        self.cursor = ''
        self.delay_after_request_error = 1

    @property
    def get_headers(self):
        return {'Host': 'api.twitter.com',
                'Connection': 'keep - alive',
                'authorization': self.auth_token,
                'x-guest-token': self.guest_token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/81.0.4044.122 Safari/537.36',
                'Referer': 'https://twitter.com'
                }

    def get_raw_info(self, screen_name, internal_id=None):
        url = f'https://api.twitter.com/graphql/{self.graphql_endpoint}/UserByScreenName?variables=%7B%22' \
              f'screen_name%22%3A%22{screen_name}%22%2C%22withHighlightedLabel%22%3Atrue%7D'
        return self.__request_json(url)

    def get_internal_id(self, link):
        screen_name = self.get_screen_name(link)
        return self.get_raw_info(screen_name=screen_name)['data']['user']['rest_id']

    def get_tokens(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        if self.remote:
            driver = Remote(command_executor=self.selenium_server_url,
                            desired_capabilities=chrome_options.to_capabilities())
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        driver.get('http://twitter.com')
        gt = driver.get_cookie('gt')['value']
        self.config.update({'tw_guest_token': gt})
        write_json_to_file('resources/config.json', dump(self.config))
        logging.info(f'Получен новый токен: {gt}')
        driver.quit()
        return gt

    def __request_json(self, url):
        for i in range(5):
            try:
                query = requests.get(url, headers=self.get_headers)
                if query.status_code == 200:
                    return ujson.loads(query.text)
                elif query.status_code == 403 or query.status_code == 429:
                    logging.warning(f'Ошибка {query.status_code}. Возможно, невалидный токен')
                    self.guest_token = self.get_tokens()
                else:
                    raise RequestError(f'Ошибка {query.status_code} при запросе JSON')
            except RequestError as e:
                time.sleep(self.delay_after_request_error)
                Crawler.log_error(e)
            except (URLError, ConnectionError, Exception) as e:
                time.sleep(self.delay_after_request_error)
                Crawler.log_error(e)
        raise GetInfoError('Не удается получить информацию об источнике')

    def get_info(self, link, internal_id=None):
        screen_name = Crawler.get_screen_name(link)
        user_info = self.get_raw_info(screen_name=screen_name)
        user_id = user_info['data']['user']['rest_id']
        key_exist = 'legacy' in user_info['data']['user']
        if not key_exist:
            raise GetInfoError(f'Ошибка получения информации об аккаунте')
        info = user_info['data']['user']['legacy']
        parsed_info = {
            'name': info['name'],
            'link': f'https://twitter.com/{info["screen_name"]}',
            'internal_id': str(user_id),
            'avatar': (info['profile_image_url_https']).replace('_normal', ''),
            'type_social': 'TW',
        }
        if info['name'] == '':
            parsed_info.update({'name': info['screen_name']})
        return parsed_info

    def get_subscribers_count(self, link, internal_id=None):
        screen_name = Crawler.get_screen_name(link)
        user_info = self.get_raw_info(screen_name=screen_name)
        key_exist = 'legacy' in user_info['data']['user']
        if not key_exist:
            raise GetInfoError(f'Ошибка получения подписчиков')
        info = user_info['data']['user']['legacy']
        subscribers = {
            'updated_at': datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z'),
            'count_subscribers': info['followers_count']
        }
        return subscribers

import logging
import time
from datetime import datetime

from instagram_web_api import ClientError

from crawlers.crawler import Crawler
from crawlers.instagram.my_client import MyClient

logging.basicConfig(level='INFO')


class Decorators:
    @classmethod
    def try_except(self, func):
        def try_except_function(self, *args, **kwargs):
            for i in range(10):
                try:
                    results = func(self, *args, **kwargs)
                    return results
                except (ClientError, Exception) as e:
                    Crawler.log_error(e)
                    if 'Not Found' in str(e):
                        raise ValueError('Профиль не найден')
                    time.sleep(5)
                    continue

        return try_except_function


class Insta(Crawler):
    def __init__(self):
        super().__init__()
        self.insta = MyClient(auto_patch=True, drop_incompat_keys=True)
        logging.info(f'Инициализация клиента Инстаграм')

    @Decorators.try_except
    def __catch_exception_in_get_method(self, method, *args, **kwargs):
        return method(*args, **kwargs)

    def get_internal_id(self, link):
        screen_name = Crawler.get_screen_name(link)
        info = self.get_raw_info(screen_name=screen_name)
        return info['id']

    def get_raw_info(self, screen_name, internal_id=None):
        return self.__catch_exception_in_get_method(self.insta.user_info2, screen_name)

    def get_info(self, link, internal_id=None):
        screen_name = Crawler.get_screen_name(link)
        info = self.get_raw_info(screen_name=screen_name)
        parsed_info = {
            'name': info['full_name'],
            'link': f'https://www.instagram.com/{info["username"]}',
            'internal_id': info['id'],
            'avatar': info['profile_pic_url'],
            'type_social': 'IN',
        }
        if info['full_name'] == '':
            parsed_info.update({'name': info['username']})
        if not parsed_info['avatar']:
            parsed_info.update({'avatar': info['profile_pic_url_hd']})
        return parsed_info

    def get_subscribers_count(self, link, internal_id=None):
        screen_name = Crawler.get_screen_name(link)
        info = self.get_raw_info(screen_name=screen_name)
        subscribers = {
            'updated_at': datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z'),
            'count_subscribers': info['edge_followed_by']['count']
        }
        return subscribers

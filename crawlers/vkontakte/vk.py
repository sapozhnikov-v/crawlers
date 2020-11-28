import logging
from datetime import datetime

import vk_api
from vk_api import ApiError

from crawlers.crawler import Crawler
from crawlers.errors import LinkError, ExtractIdError, GetInfoError

logging.basicConfig(level='INFO')


class Vk(Crawler):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.vk_session = vk_api.VkApi(username, password, auth_handler=self.__auth_handler,
                                       captcha_handler=self.__captcha_handler)
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        logging.info("Инициализация клиента ВК")

    @staticmethod
    def __auth_handler():
        key = input('Введите код аутентификации: ')
        remember_device = True
        return key, remember_device

    @staticmethod
    def __captcha_handler(captcha):
        key = input(f'Введите код с картинки {captcha.get_url()}').strip()
        return captcha.try_again(key)

    def get_internal_id(self, link):
        screen_name = self.get_screen_name(link)
        profile_id = self.vk.utils.resolveScreenName(screen_name=screen_name)
        if not isinstance(profile_id, dict):
            raise LinkError(f'Некорректная ссылка - {link}')
        profile_type = profile_id['type']
        obj_id = profile_id['object_id']
        if profile_type == 'user':
            return obj_id
        elif profile_type == 'group' or profile_type == 'page':
            return -obj_id
        raise ExtractIdError(f'Неизвестный тип ID {link}')

    def get_raw_info(self, internal_id, screen_name=None):
        try:
            if internal_id > 0:
                return self.vk.users.get(user_ids=internal_id, fields='photo_100, screen_name, counters')[0]
            return self.vk.groups.getById(group_id=-internal_id, fields='members_count')[0]
        except ApiError as e:
            raise GetInfoError(f'{e}. Ошибка получения информации о профиле {internal_id}')

    def get_info(self, internal_id, link=None):
        info = self.get_raw_info(internal_id)
        parsed_info = {
            'name': '',
            'link': f'https://vk.com/{info["screen_name"]}',
            'internal_id': internal_id,
            'avatar': info['photo_100'],
            'type_social': 'VK'
        }
        if internal_id > 0:
            parsed_info.update({'name': f'{info["first_name"]} {info["last_name"]}'})
            return parsed_info
        parsed_info.update({'name': info['name']})
        return parsed_info

    def get_subscribers_count(self, internal_id, link=None):
        info = self.get_raw_info(internal_id)
        subscribers = {
            'updated_at': datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z'),
        }
        if internal_id > 0:
            subscribers.update({'count_subscribers': info['counters']['clips_followers']})
            return subscribers
        subscribers.update({'count_subscribers': info['members_count']})
        return subscribers

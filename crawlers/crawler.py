from datetime import datetime
import logging
import re
from abc import ABC, abstractmethod

from crawlers.errors import LinkError


class Crawler(ABC):
    @abstractmethod
    def __init__(self, login=None, password=None):
        pass

    @abstractmethod
    def get_internal_id(self, link):
        pass

    @abstractmethod
    def get_info(self, internal_id, link):
        pass

    @abstractmethod
    def get_raw_info(self, internal_id, screen_name):
        pass

    @abstractmethod
    def get_subscribers_count(self, internal_id, link):
        pass

    @staticmethod
    def get_screen_name(link):
        try:
            return re.search('com/(?P<id>[\w_.-]+)', link).group('id')
        except AttributeError:
            raise LinkError(f'Некорректный URL - {link}')

    @staticmethod
    def log_error(e, text=None):
        return logging.error(f'{datetime.now()} - {e.__class__} - {e}. {text}')
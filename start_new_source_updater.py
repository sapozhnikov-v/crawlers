import logging
import time

from utils.json_helper import read_json_from_file, write_json_to_file, dump

from crawlers.instagram.insta import Insta
from crawlers.twitter.tw import Tw
from crawlers.vkontakte.vk import Vk
from monitor_api.api import MonitorApi

config = read_json_from_file('resources/config.json')
logging.basicConfig(level='INFO')


def get_crawler(type_social):
    if type_social == 'IN':
        return insta
    if type_social == 'VK':
        return vk
    if type_social == 'TW':
        return tw


def update_new_sources():
    sources = monitor.get_sources()
    write_json_to_file('sources_from_monitor.json', dump(sources))
    count = 0
    for source in sources:
        internal_id = source['internal_id']
        if internal_id:
            continue
        count += 1
        source_id = source['id']
        link = source['link']
        type_social = source['type_social']
        crawler = get_crawler(type_social)
        logging.info(f'{count}. Получаем информацию для {link}')
        internal_id = crawler.get_internal_id(link)
        info = crawler.get_info(internal_id=int(internal_id), link=link)
        info.update({'id': source_id})
        monitor.update_source(dump(info), source_id)
        subscribers = crawler.get_subscribers_count(internal_id=int(internal_id), link=link)
        subscribers.update({'source': source_id})
        monitor.add_subscribers(dump(subscribers))


if __name__ == '__main__':
    monitor = MonitorApi()
    vk = Vk(config['vk_login'], config['vk_password'])
    insta = Insta()
    tw = Tw()

    while True:
        update_new_sources()
        logging.info('Ждём 5 секунд')
        time.sleep(5)

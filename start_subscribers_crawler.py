import logging
import time

from crawlers.twitter.tw import Tw
from crawlers.vkontakte.vk import Vk
from crawlers.instagram.insta import Insta
from monitor_api.api import MonitorApi
from utils.json_helper import read_json_from_file, write_json_to_file, dump

config = read_json_from_file('resources/config.json')
logging.basicConfig(level='INFO')


def get_crawler(type_social):
    if type_social == 'IN':
        return insta
    if type_social == 'VK':
        return vk
    if type_social == 'TW':
        return tw


def update_sources():
    sources = monitor.get_sources()
    write_json_to_file('sources_from_monitor.json', dump(sources))

    count = 0
    for source in sources:
        count += 1

        internal_id = source['internal_id']
        source_id = source['id']
        link = source['link']
        name = source['name']
        avatar = source['avatar']
        type_social = source['type_social']
        crawler = get_crawler(type_social)
        logging.info(f'{count}. Получаем информацию для {link}')
        if not internal_id:
            internal_id = crawler.get_internal_id(link)
            subscribers = crawler.get_subscribers_count(internal_id=int(internal_id), link=link)
            subscribers.update({'source': source_id})
            monitor.add_subscribers(dump(subscribers))
        info = crawler.get_info(internal_id=int(internal_id), link=link)
        if link == info['link'] and name == info['name'] and avatar == info['avatar']:
            logging.info(f'Ничего нового')
            continue
        if link != info['link']:
            logging.info('Обновлена ссылка')
        if name != info['name']:
            logging.info('Обновлено имя')
        if avatar != info['avatar']:
            logging.info('Обновлен аватар')
        info.update({'id': source_id})
        monitor.update_source(dump(info), source_id)


def get_subscribers():
    sources = monitor.get_sources()
    write_json_to_file('sources_from_monitor.json', dump(sources))

    count = 0
    for source in sources:
        count += 1
        internal_id = source['internal_id']
        source_id = source['id']
        link = source['link']
        type_social = source['type_social']
        crawler = get_crawler(type_social)
        logging.info(f'{count}. Получаем количество подписчиков для {link}')
        if not internal_id:
            internal_id = crawler.get_internal_id(link)
        subscribers = crawler.get_subscribers_count(internal_id=int(internal_id), link=link)
        subscribers.update({'source': source_id})
        monitor.add_subscribers(dump(subscribers))


if __name__ == '__main__':
    monitor = MonitorApi()
    vk = Vk(config['vk_login'], config['vk_password'])
    insta = Insta()
    tw = Tw()

    while True:
        update_sources()
        get_subscribers()
        logging.info('Ждём час')
        time.sleep(3600)

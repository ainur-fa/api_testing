# -*- coding: utf-8 -*-
from time import sleep
from pathlib import Path
import logging
import configparser
import redis


def init_config():
    """Init configuration"""
    cp = configparser.ConfigParser()
    config_file = str(Path(__file__).parent.joinpath('settings.ini'))
    cp.read(config_file)
    cp_section = cp['store']
    host = cp_section.get('HOST')
    port = int(cp_section.get('PORT'))
    return host, port


def retry(count=3, interval=1):

    def my_decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.info('DB connection failed, attemp: %s', attempt)
                    attempt += 1
                    if attempt > count:
                        raise e
                    sleep(interval)
        return wrapper

    return my_decorator


HOST, PORT = init_config()


class Store:

    def __init__(self, host=HOST, port=PORT):
        self._r = redis.Redis(host=host, port=port, socket_timeout=2, decode_responses=True)

    def ping(self):
        return self._r.ping()

    @retry()
    def get(self, key):
        return self._r.get(key)

    @retry()
    def set(self, name, value, ex=None):
        return self._r.set(name, value, ex)

    def cache_get(self, key):
        try:
            logging.info('Getting value from cache')
            return self._r.get(key)
        except Exception as e:
            logging.info(e)
            return None

    def cache_set(self, name, value, ex=None):
        try:
            logging.info('Writing value to cache')
            return self._r.set(name, value, ex)
        except Exception as e:
            logging.info(e)

    def create_interests(self):
        interests = ["cars", "pets", "travel", "hi-tech", "sport", "music",
                     "books", "tv", "cinema", "geek", "otus"]
        for _id, interest in enumerate(interests, start=1):
            self.set(f'i:{_id}', interest)

    def disconnect(self):
        self._r.connection_pool.disconnect()


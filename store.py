# -*- coding: utf-8 -*-
from time import sleep
import logging
import redis

HOST = 'localhost'
PORT = 6379


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


class Store:

    def __init__(self):
        self._r = redis.Redis(host=HOST, port=PORT, socket_timeout=2, decode_responses=True)
        self._r.ping()
        self.create_interests()

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
        self._r.connection_pool = None

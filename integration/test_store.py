# -*- coding: utf-8 -*-
import uuid
from time import sleep
from store import Store

STORE = Store()


class TestStore:

    def test_get_set(self):
        name, value = 'name', 'value'
        assert STORE.set(name, value)
        assert STORE.get(name) == value

    def test_cache_set(self):
        name, value = 'name', 'value'
        assert STORE.set(name, value, ex=2)
        assert STORE.get(name) == value
        sleep(2)
        assert STORE.get(name) is None

    def test_cache_get(self):
        name, value = uuid.uuid4().int, uuid.uuid4().int
        STORE.set(name, value)
        STORE.disconnect()
        assert STORE.cache_get(uuid.uuid4().int) is None

    def test_reconnect(self):
        name, value = 'name', 'value'
        assert STORE.ping()
        STORE.disconnect()
        assert STORE.set(name, value)
        assert STORE.get(name) == value







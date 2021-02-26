# -*- coding: utf-8 -*-
from http.server import HTTPServer
from http.client import HTTPConnection
from threading import Thread
import datetime
import hashlib
import json
import pytest
import constants
from api import MainHTTPHandler

HOST = "localhost"
PORT = 8080


@pytest.fixture(scope='session', autouse=True)
def start_api():
    server = HTTPServer((HOST, PORT), MainHTTPHandler)
    t = Thread(target=server.serve_forever)
    t.start()
    yield
    server.shutdown()
    t.join()


@pytest.fixture(scope='session')
def client_connection():
    connection = HTTPConnection(HOST, PORT)
    yield connection
    connection.close()


def do_request(client_connection, req):
    client_connection.request("POST", "/method/", json.dumps(req))
    r = client_connection.getresponse()
    return json.load(r)


def set_valid_auth(request):
    if request.get("login") == constants.ADMIN_LOGIN:
        request["token"] = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") +
                                           constants.ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + constants.SALT
        request["token"] = hashlib.sha512(msg.encode('utf-8')).hexdigest()
    return request


class TestRequests:

    @pytest.mark.parametrize("req",
                             [{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "",
                               "arguments": {}},
                              {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd",
                               "arguments": {}},
                              {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "",
                               "arguments": {}}],
                             ids=lambda arg: str(arg))
    def test_bad_auth(self, req, client_connection):
        response = do_request(client_connection, req)
        assert response.get('code') == constants.FORBIDDEN

    @pytest.mark.parametrize("req", [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}}
        ], ids=lambda arg: str(arg))
    def test_invalid_method_request(self, req, client_connection):
        response = do_request(client_connection, req)
        assert response.get('code') == constants.INVALID_REQUEST

    @pytest.mark.parametrize("args", [
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
        ], ids=lambda arg: str(arg))
    def test_invalid_score_request(self, args, client_connection):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": args}
        response = do_request(client_connection, request)
        assert response.get('code') == constants.INVALID_REQUEST

    def test_ok_score_admin_request(self, client_connection):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        response = do_request(client_connection, set_valid_auth(request))
        assert response.get("code") == constants.OK
        assert response.get("response").get('score') == 42

    @pytest.mark.parametrize("args", [
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
        ], ids=lambda arg: str(arg))
    def test_invalid_interests_request(self, args, client_connection):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": args}
        response = do_request(client_connection, set_valid_auth(request))
        assert response.get("code") == constants.INVALID_REQUEST

    @pytest.mark.parametrize("args", [
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ], ids=lambda arg: str(arg))
    def test_ok_interests_request(self, args, client_connection):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": args}
        response = do_request(client_connection, set_valid_auth(request))
        assert response.get("code") == constants.OK
        assert len(args['client_ids']) == len(response['response'])

    @pytest.mark.parametrize("args", [
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
        ], ids=lambda arg: str(arg))
    def test_ok_score_request(self, args, client_connection):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": args}
        response = do_request(client_connection, set_valid_auth(request))
        print()
        print(response)
        assert response.get("code") == constants.OK
        assert float(response.get("response").get('score')) > 0

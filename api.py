#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scoring API
"""

import json
import datetime
import logging
import hashlib
import uuid
from argparse import ArgumentParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from store import Store
from api_requests import ClientsInterestsRequest, OnlineScoreRequest, MethodRequest
from scoring import get_score, get_interests
from custom_erros import ValidationError
from constants import SALT, ADMIN_SALT, OK, BAD_REQUEST, FORBIDDEN, \
    NOT_FOUND, INVALID_REQUEST, INTERNAL_ERROR, ERRORS


def check_auth(request):
    """Проверка авторизации"""
    logging.info('Trying authorization as "%s"', request.login)
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode(
                'utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode(
            'utf-8')).hexdigest()
    if digest == request.token:
        logging.info('Authorization success')
        return True
    logging.info('Authorization failed, expected "%s",\n but "%s" received', digest, request.token)
    return False


def authorization(func):
    """Проверка авторизации перед выполнением func"""
    def wrapper(request, ctx, store):
        response, code = ERRORS.get(FORBIDDEN), FORBIDDEN
        if check_auth(request):
            response, code = func(request, ctx, store)
        return response, code

    return wrapper


def method_handler(request, ctx, store):
    """Обработчик имеющихся методов"""
    try:
        req = MethodRequest()
        req.validate(request.get('body'))
        logging.info('Requested method value: "%s"', req.method)
        if req.method == 'online_score':
            response, code = online_score_handler(req, ctx, store)
        elif req.method == 'clients_interests':
            response, code = clients_interests_handler(req, ctx, store)
        else:
            logging.info('Unavailable method value')
            response, code = ERRORS.get(INVALID_REQUEST), INVALID_REQUEST
        return response, code
    except ValidationError:
        return ERRORS.get(INVALID_REQUEST), INVALID_REQUEST


@authorization
def online_score_handler(req, ctx, store):
    """Обработчик для online_score"""
    arguments = req.arguments
    online_score = OnlineScoreRequest()
    online_score.validate(arguments)
    ctx['has'] = [key for key, val in arguments.items() if val is not None]
    if req.is_admin:
        score = int(ADMIN_SALT)
    else:
        score = get_score(store, online_score.phone, online_score.email,
                          online_score.birthday,
                          online_score.gender, online_score.first_name,
                          online_score.last_name)
    response = {'score': score}
    logging.info('Score: %s', score)
    return response, OK


@authorization
def clients_interests_handler(req, ctx, store):
    """Обработчик для clients_interests"""
    clients_interests = ClientsInterestsRequest()
    clients_interests.validate(req.arguments)
    ctx['nclients'] = len(clients_interests.client_ids)
    interests = {_id: get_interests(store, _id) for _id in
                 clients_interests.client_ids}
    logging.info('Client interest: %s', interests)
    return interests, OK


class MainHTTPHandler(BaseHTTPRequestHandler):
    """Главный обработчик запросов"""
    router = {
        "method": method_handler
    }
    store = Store()

    @staticmethod
    def get_request_id(headers):
        """Получение id запроса или генерация нового"""
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        """Обработка POST запросов"""
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        logging.info('New request context: %s', context)
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
            logging.info('Received request: %s', request)
        except Exception as e:
            code = BAD_REQUEST
            logging.info(e)

        if request:
            path = self.path.strip("/")
            if path in self.router:
                logging.info('Requested path: %s', path)
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context,
                        self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s", e)
                    code = INTERNAL_ERROR
            else:
                logging.info('%s is not valid path', path)
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"),
                 "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf-8'))


if __name__ == "__main__":
    AP = ArgumentParser()
    AP.add_argument("-p", "--port", dest='port', action="store", type=int, default=8080)
    AP.add_argument("-l", "--log", dest='log', action="store", default=None)
    opts = AP.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s", opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

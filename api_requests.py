# -*- coding: utf-8 -*-
import logging
from fields import Field, ClientIDsField, DateField, CharField, EmailField, \
    PhoneField, BirthDayField, GenderField, ArgumentsField
from constants import ADMIN_LOGIN


class Req:

    def __init__(self, kwargs):
        self.fields = [field for field, value in self.__class__.__dict__.items()
                       if isinstance(value, Field)]
        logging.info('Available %s fields: %s', self.__class__.__name__, self.fields)
        logging.info('Received %s fields: %s', self.__class__.__name__, list(kwargs.keys()))
        for field in self.fields:
            value = kwargs[field] if field in kwargs else None
            try:
                setattr(self, field, value)
            except Exception as e:
                logging.info(e)
                raise e

        self.verify()

    def verify(self):
        pass


class ClientsInterestsRequest(Req):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Req):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def verify(self):
        validate_pairs = any(
            [self.phone and self.email, self.first_name and self.last_name,
             self.gender is not None and self.birthday])
        if not validate_pairs:
            raise AttributeError(
                'At least one pair expected from the '
                '(first_name - last_name, email - phone, birthday - gender)')


class MethodRequest(Req):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=True)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

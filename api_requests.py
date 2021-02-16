# -*- coding: utf-8 -*-
import logging
from fields import Field, ClientIDsField, DateField, CharField, EmailField, \
    PhoneField, BirthDayField, GenderField, ArgumentsField
from constants import ADMIN_LOGIN
from custom_erros import ValidationError


class ApiRequest:

    def __init__(self):
        self.fields = [field for field, value in self.__class__.__dict__.items()
                       if isinstance(value, Field)]

    def validate(self, kwargs):
        logging.debug('Available %s fields: %s', self.__class__.__name__, self.fields)
        logging.debug('Received %s fields: %s', self.__class__.__name__, list(kwargs.keys()))

        errors = []
        for field in self.fields:
            value = kwargs[field] if field in kwargs else None
            try:
                setattr(self, field, value)
            except ValidationError as e:
                errors.append(e)
                logging.error(e)
        if errors:
            raise ValidationError("Fields validate error")


class ClientsInterestsRequest(ApiRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(ApiRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self, kwargs):
        super().validate(kwargs)
        validate_pairs = any(
            [self.phone and self.email, self.first_name and self.last_name,
             self.gender is not None and self.birthday])
        if not validate_pairs:
            logging.error(
                'At least one pair expected from the (first_name - last_name, email - phone, birthday - gender)')
            raise ValidationError("Fields validate error")


class MethodRequest(ApiRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=True)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

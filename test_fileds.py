import datetime
import pytest
from api_requests import *


def get_test_class(field, required, nullable):
    class My(ApiRequest):
        value = field(required, nullable)
    return My


def run_test_field(field, value):
    dict_items = list(ClientsInterestsRequest.__dict__.values()) + list(OnlineScoreRequest.__dict__.values())
    item = [i for i in dict_items if type(i) == field][0]
    my_class = get_test_class(field, item.required, item.nullable)
    class_instance = my_class()
    class_instance.validate(kwargs={'value': value})


class TestOkFields:

    @pytest.mark.parametrize("value", ['test@eerg', 'test@eerg.ru', '@', ''],
                             ids=lambda arg: str(arg))
    def test_ok_email(self, value):
        run_test_field(EmailField, value)

    @pytest.mark.parametrize("value", ([1, 2, 5], [1], [12124124, ]),
                             ids=lambda arg: str(arg))
    def test_ok_client_ids(self, value):
        run_test_field(ClientIDsField, value)

    @pytest.mark.parametrize("value", (0, 1, 2), ids=lambda arg: str(arg))
    def test_ok_gender(self, value):
        run_test_field(GenderField, value)

    @pytest.mark.parametrize("value", ('12.01.1990', '', datetime.datetime.now().date().strftime('%d.%m.%Y')),
                             ids=lambda arg: str(arg))
    def test_ok_birthday(self, value):
        run_test_field(BirthDayField, value)

    @pytest.mark.parametrize("value", ('79175002040', 79175002086),
                             ids=lambda arg: str(arg))
    def test_ok_phone(self, value):
        run_test_field(PhoneField, value)


class TestInvalidFields:

    @pytest.mark.parametrize("value", ('test.eerg', 'test#eerg', -1),
                             ids=lambda arg: str(arg))
    def test_invalid_email(self, value):
        with pytest.raises(ValueError):
            run_test_field(EmailField, value)

    @pytest.mark.parametrize("value", (['1s', 2], [], ['wefwef']),
                             ids=lambda arg: str(arg))
    def test_invalid_client_ids(self, value):
        with pytest.raises(ValueError):
            run_test_field(ClientIDsField, value)

    @pytest.mark.parametrize("value", (3, -1, 'a'), ids=lambda arg: str(arg))
    def test_invalid_gender(self, value):
        with pytest.raises(ValueError):
            run_test_field(GenderField, value)

    @pytest.mark.parametrize("value", (3, -1, 'a', '1990.12.01'), ids=lambda arg: str(arg))
    def test_invalid_birthday(self, value):
        with pytest.raises(ValueError):
            run_test_field(BirthDayField, value)

    @pytest.mark.parametrize("value", ('7917500', 'qwertyuiopa', '89175002040', '7917500204a'),
                             ids=lambda arg: str(arg))
    def test_invalid_phone(self, value):
        with pytest.raises(ValueError):
            run_test_field(PhoneField, value)

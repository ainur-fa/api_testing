import datetime
import pytest
from api_requests import *


class TestOkFields:

    @pytest.mark.parametrize("value", ['test@eerg', 'test@eerg.ru', '@', ''],
                             ids=lambda arg: str(arg))
    def test_ok_email(self, value):
        assert EmailField().validate(value)

    @pytest.mark.parametrize("value", ([1, 2, 5], [1], [12124124, ]),
                             ids=lambda arg: str(arg))
    def test_ok_client_ids(self, value):
        assert ClientIDsField().validate(value)

    @pytest.mark.parametrize("value", (0, 1, 2), ids=lambda arg: str(arg))
    def test_ok_gender(self, value):
        assert GenderField().validate(value)

    @pytest.mark.parametrize("value", ('12.01.1990', datetime.datetime.now().date().strftime('%d.%m.%Y')),
                             ids=lambda arg: str(arg))
    def test_ok_birthday(self, value):
        assert BirthDayField().validate(value)

    @pytest.mark.parametrize("value", ('79175002040', 79175002086),
                             ids=lambda arg: str(arg))
    def test_ok_phone(self, value):
        assert PhoneField().validate(value)


class TestInvalidFields:

    @pytest.mark.parametrize("value", ('test.eerg', 'test#eerg', [1, 2]),
                             ids=lambda arg: str(arg))
    @pytest.mark.xfail
    def test_invalid_email(self, value):
        with pytest.raises(ValueError):
            assert EmailField().validate(value)

    @pytest.mark.parametrize("value", (['1s', 2], [], ['wefwef']),
                             ids=lambda arg: str(arg))
    @pytest.mark.xfail
    def test_invalid_client_ids(self, value):
        with pytest.raises(ValueError):
            assert ClientIDsField().validate(value)

    @pytest.mark.parametrize("value", (3, -1, 'a'), ids=lambda arg: str(arg))
    @pytest.mark.xfail
    def test_invalid_gender(self, value):
        with pytest.raises(ValueError):
            assert GenderField().validate(value)

    @pytest.mark.parametrize("value", (3, -1, 'a', '1990.12.01'), ids=lambda arg: str(arg))
    @pytest.mark.xfail
    def test_invalid_birthday(self, value):
        with pytest.raises(ValueError):
            assert BirthDayField().validate(value)

    @pytest.mark.parametrize("value", ('7917500', 'qwertyuiopa', '89175002040', '7917500204a'),
                             ids=lambda arg: str(arg))
    @pytest.mark.xfail
    def test_invalid_phone(self, value):
        with pytest.raises(ValueError):
            assert PhoneField().validate(value)

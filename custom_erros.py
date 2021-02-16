# -*- coding: utf-8 -*-


class ValidationError(ValueError):
    """Ошибка при валидации поля"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

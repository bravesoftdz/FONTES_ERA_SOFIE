# coding: utf-8

from library.common.miscellaneous import REGEX_MAIL
from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeDateTime

SCHEME_USER_BLOCKED = SchemeObject(
    required=True,
    dict_pairs={
        'reason': SchemeString(True),
        'when': SchemeDateTime(True)
    }
)

SCHEME_USER = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, REGEX_MAIL),
        'full_name': SchemeString(False, '.+'),
        'short_name': SchemeString(False, '.+'),
        'cpf': SchemeString(False, '^\d{11}$'),
        'level': SchemeString(False, '^(PLATFORM|COMPANY)$'),
        'company': SchemeString(False, '.*'),
        'password': SchemeString(False, '.+'),
        'blocked': SchemeObject(False, SCHEME_USER_BLOCKED),
    }
)

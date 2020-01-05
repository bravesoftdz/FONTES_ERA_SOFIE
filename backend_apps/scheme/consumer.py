# coding: utf-8

from library.common.miscellaneous import REGEX_MAIL
from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeDateTime

SCHEME_CARD_KNOW = SchemeObject(
    required=True,
    dict_pairs={
        'sofier': SchemeString(True, '\d{11}'),
        'card': SchemeString(True, '.+'),
        'date_time': SchemeDateTime(True)
    }
)

SCHEME_CONSUMER = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '^(\d{11}|\d{14})$'),
        'full_name': SchemeString(True, '.+'),
        'kind_of_person': SchemeString(True, '^(J|F)$'),
        'main_phone': SchemeString(True, '^\d{10,11}'),
        'main_email': SchemeString(True, REGEX_MAIL),
        'to_care': SchemeString(False, '.+'),
        'birthday': SchemeDateTime(False),
        'gender': SchemeString(False, '^(M|F|O)$'),
        'rg': SchemeString(False, '\d{8,15}'),
        'mother_name': SchemeString(False, '.+')
    }
)

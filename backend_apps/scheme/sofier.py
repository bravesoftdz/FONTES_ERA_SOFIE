# coding: utf-8

from library.common.miscellaneous import REGEX_MAIL
from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeDateTime, SchemeBoolean, SchemeList
from scheme.several import SCHEME_HEADER

SCHEME_SOFIER_BLOCKED = SchemeObject(
    required=True,
    dict_pairs={
        'reason': SchemeString(True),
        'when': SchemeDateTime(True)
    }
)

SCHEME_SOFIER_ACCOUNT = SchemeObject(
    required=True,
    dict_pairs={
        'code': SchemeString(False, '.+'),
        'name': SchemeString(False, '.+'),
        'agency': SchemeString(False, '.+'),
        'account': SchemeString(False, '^\d+$'),
        'account_digit': SchemeString(False, '^\d+$')
    }
)

SCHEME_SOFIER = SchemeObject(
    required=True,
    dict_pairs={
        'sofier_id': SchemeString(True, '[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'),
        'name': SchemeString(False, '^\d{11}$'),
        'password': SchemeString(False, '.+'),
        'short_name': SchemeString(False, '.+'),
        'full_name': SchemeString(False, '.+'),
        'email': SchemeString(False, REGEX_MAIL),
        'main_phone': SchemeString(False, '^\d{10,11}$'),
        'birthday': SchemeDateTime(False),
        'blocked': SchemeObject(False, SCHEME_SOFIER_BLOCKED),
        'bank_checking_account': SchemeObject(False, SCHEME_SOFIER_ACCOUNT),
        'shop_name': SchemeString(False, '^[a-z0-9-]{2,20}$'),
        'is_alpha': SchemeBoolean(False),
        'sign_origin': SchemeList(False, SCHEME_HEADER),
        'indication_code': SchemeString(False, '^[A-Z]{3}$')
    }
)

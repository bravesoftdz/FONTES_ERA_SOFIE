# coding: utf-8

from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeBoolean

SCHEME_COMPANY = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'full_name': SchemeString(False, '.+'),
        'cnpj': SchemeString(False, r'^\d{14}$'),
        'active': SchemeBoolean(False),
        'card_bookmark_color': SchemeString(True, '#[a-fA-F0-9]{6}'),
        'description': SchemeString(False, '.+'),
    }
)

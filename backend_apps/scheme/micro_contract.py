# coding: utf-8

from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeBoolean

SCHEME_MICROCONTRACT = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'active': SchemeBoolean(True),
        'code': SchemeString(True, '.+')
    }
)

# coding: utf-8

from library.crud.scheme_validator import SchemeObject, SchemeString

SCHEME_TRANSACTION_STATUS = SchemeObject(
    required=True,
    dict_pairs={
        'state': SchemeString(True, '^(QUEUE|PAUSED|PROCESSING|FINISHED)$'),

    }
)

SCHEME_TRANSACTION = SchemeObject(
    required=True,
    dict_pairs={
        'transaction': SchemeString(True, '.+'),
        'status': SchemeObject(True, SCHEME_TRANSACTION_STATUS),
    }
)

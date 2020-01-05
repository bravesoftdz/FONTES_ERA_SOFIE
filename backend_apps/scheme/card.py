# coding: utf-8

from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeNumber, SchemeList, SchemeBoolean, SchemeDateTime

SCHEME_DATACOLLECT_ITEM = SchemeObject(
    required=True,
    dict_pairs={
        'type': SchemeString(True, '^(PAY_INFO|CONSUMER_INFO|ADDRESS|REFERENCES)$'),
        'show': SchemeBoolean(True)
    }
)

SCHEME_QUOTES = SchemeObject(
    required=True,
    dict_pairs={
        'qtt': SchemeNumber(True, False, 1),
        'value': SchemeNumber(True, True, 1),
        'with_rate': SchemeBoolean(True)
    }
)

SCHEME_PAYMENT_CONDITIONS = SchemeObject(
    required=True,
    dict_pairs={
        'title': SchemeString(True, '.+'),
        'method': SchemeString(True, '^(CREDIT_CARD|POST_PAID)$'),
        'price': SchemeNumber(True, True, 0),
        'reward': SchemeNumber(True, True, 0),
        'fee': SchemeNumber(True, True, 0),
        'points': SchemeNumber(False, False, 0),
        'quotes': SchemeObject(False, SCHEME_QUOTES),
        'days_for_reward': SchemeNumber(True, False, 0)
    }
)

SCHEME_PUBLICATION = SchemeObject(
    required=True,
    dict_pairs={
        'who': SchemeString(True, '.*'),
        'when': SchemeDateTime(True),
    }
)

SCHEME_VALIDITY = SchemeObject(
    required=True,
    dict_pairs={
        'start': SchemeDateTime(True),
        'end': SchemeDateTime(True)
    }
)

SCHEME_CARD_TITLE = SchemeObject(
    required=True,
    dict_pairs={
        'title': SchemeString(True, '.*'),
        'sub_title': SchemeString(True, '.*'),
        'row_1': SchemeString(False, '.*'),
        'row_2': SchemeString(False, '.*')
    }
)

SCHEME_BOOKMARK_ITEM = SchemeObject(
    required=True,
    dict_pairs={
        'display': SchemeBoolean(True),
        'row_1': SchemeString(False, '.*'),
        'row_2': SchemeString(False, '.*'),
        'row_3': SchemeString(False, '.*')
    }
)

SCHEME_BOOKMARK = SchemeObject(
    required=True,
    dict_pairs={
        'card': SchemeObject(True, SCHEME_BOOKMARK_ITEM),
        'detail_1': SchemeObject(False, SCHEME_BOOKMARK_ITEM),
        'detail_2': SchemeObject(False, SCHEME_BOOKMARK_ITEM),
        'detail_3': SchemeObject(False, SCHEME_BOOKMARK_ITEM)
    }
)

SCHEME_REFERENCE_CODES = SchemeObject(
    required=False,
    dict_pairs={
        'reference_1': SchemeString(False),
        'reference_2': SchemeString(False),
        'reference_3': SchemeString(False),
        'reference_4': SchemeString(False),
        'reference_5': SchemeString(False)
    }
)

SCHEME_CARD = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'company': SchemeString(True, '.+'),
        'expertise': SchemeString(False, '^(SALE|SERVICE|SEARCH|LEAD)$'),
        'title': SchemeObject(True, SCHEME_CARD_TITLE),
        'bookmarks': SchemeObject(True, SCHEME_BOOKMARK),
        'description': SchemeString(True, '.+', ['br', 'ul', 'li', 'strong']),
        'training': SchemeString(False, '.+'),
        'micro_contract': SchemeString(False, '.+'),
        'publication': SchemeObject(False, SCHEME_PUBLICATION),
        'validity': SchemeObject(False, SCHEME_VALIDITY),
        'payment_conditions': SchemeList(True, SCHEME_PAYMENT_CONDITIONS),
        'reference_codes': SchemeObject(False, SCHEME_REFERENCE_CODES),
        'description_on_invoice': SchemeString(False, '^.{5,13}$'),
        'in_homologation': SchemeBoolean(True),
        'data_collect_flow': SchemeList(True, SCHEME_DATACOLLECT_ITEM),
        'categories': SchemeList(True, SchemeString(True, '.+'))
    }
)

# coding: utf-8

from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeList, SchemeBoolean

SCHEME_TRAINING_QUESTION = SchemeObject(
    required=True,
    dict_pairs={
        'question': SchemeString(False, '.+'),
        'options': SchemeList(False, SchemeString(False, '.+')),
        'responses': SchemeList(False, SchemeString(False, '.+')),
    }
)

SCHEME_TRAINING = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'title': SchemeString(False, '.+'),
        'description': SchemeString(False, '.+'),
        'active': SchemeBoolean(False),
        'expertise': SchemeString(False, '^(SALE|SERVICE|SEARCH|LEAD)$'),
        'url_video': SchemeString(False, '^https://.*'),
        'company': SchemeString(False, '.+'),
        'questions': SchemeList(False, SCHEME_TRAINING_QUESTION)
    }
)

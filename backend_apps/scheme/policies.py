from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeBoolean, SchemeList, SchemeNumber
from scheme.several import SCHEME_HEADER

SCHEME_POLICIES = SchemeObject(
    required=True,
    dict_pairs={
        'version': SchemeString(True, '\d\.\d\.\d'),
        'active': SchemeBoolean(True),
        'comments': SchemeString(False),
        'hash': SchemeString(True),
    }
)

SCHEME_POLICIES_ACCEPT = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'headers': SchemeList(True, SCHEME_HEADER),
        'version': SchemeString(True, '\d\.\d\.\d'),
        'accepted': SchemeBoolean(True),
        'read': SchemeBoolean(True),
        'seconds_to_read': SchemeNumber(True, False)
    }
)

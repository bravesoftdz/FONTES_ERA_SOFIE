from library.crud.scheme_validator import SchemeObject, SchemeString, SchemeList
from scheme.several import SCHEME_HEADER

SCHEME_LEAD = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(False),
        'lead_name': SchemeString(False),
        'email': SchemeString(False),
        'indication_code': SchemeString(False),
        'phone': SchemeString(False),
        'request_headers': SchemeList(False, SCHEME_HEADER),
    }
)

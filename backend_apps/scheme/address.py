# coding: utf-8


from library.crud.scheme_validator import SchemeObject, SchemeString

SCHEME_ADDRESS_DETAIL = SchemeObject(
    required=True,
    dict_pairs={
        'zip_code': SchemeString(True, '^\d{8}$'),
        'type': SchemeString(True, '.+'),
        'full_name': SchemeString(True, '.+'),
        'number': SchemeString(True, '.+'),
        'complement': SchemeString(False, '.+'),
        'reference': SchemeString(False, '.+'),
        'district': SchemeString(True, '.+'),
        'city': SchemeString(True, '.+'),
        'state': SchemeString(True, '^(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)$'),
        'country': SchemeString(True, '^BR$')
    }
)

SCHEME_ADDRESS = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'address': SchemeObject(True, SCHEME_ADDRESS_DETAIL)
    }
)

SCHEME_ADDRESS_ASSOCIATION = SchemeObject(
    required=True,
    dict_pairs={
        'name': SchemeString(True, '.+'),
        'address_type': SchemeString(True, '^(COMMERCIAL|RESIDENTIAL|OTHER)$'),
        'user': SchemeString(True, '.+'),
        'user_level': SchemeString(True, '.+')
    }
)

from library.crud.scheme_validator import SchemeObject, SchemeString

SCHEME_HEADER = SchemeObject(
    required=True,
    dict_pairs={
        '': SchemeString(True)
    }
)

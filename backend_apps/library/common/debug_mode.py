# coding: utf-8


from argparse import ArgumentParser


parser = ArgumentParser(
    prog='DebugMode',
    usage='Modeo Debug',
    description='Indica se o servidor está sendo executado em modo debug'
)
parser.add_argument('-d', '--debug', help='Indica que o servidor deve rodar em modo debug', action='store_true', default=False, required=False)
ARGS = parser.parse_known_args()[0]


IN_DEBUG_MODE = ARGS.debug

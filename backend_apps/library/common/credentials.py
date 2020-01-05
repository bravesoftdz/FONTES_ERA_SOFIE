# coding: utf-8


from argparse import ArgumentParser
from getpass import getpass


parser = ArgumentParser(
    prog='Crendencials',
    usage='Modo de autenticação',
    description='Crendencias do usuário de banco de dados'
)
parser.add_argument('-u', '--user', help='Usuário para autenticação no database', required=False)
parser.add_argument('-p', '--pwd', help='Senha para o usuário para autenticação no database', required=False)
ARGS = parser.parse_known_args()[0]


PWD = ARGS.pwd
USER= ARGS.user

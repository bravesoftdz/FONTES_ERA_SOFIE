# coding: utf-8

from locale import setlocale, LC_ALL
from os import walk, path
from platform import system
from runpy import run_path

"""
Módulo de compatibilização com o Servidor RESTful dinâmico

A lógica consiste em varrer todos os subdiretórios do diretório ao qual pertence
este arquivo e procurar módulos Python cujo nome seja `handlers.py`.

Este módulo é executado e deve devolver, então, uma variável denominada `HANDLERS` que
deve ser uma lista de `tornado.web.URLSpec` 
"""

if system() != 'Windows':
    setlocale(LC_ALL, 'pt_BR.UTF-8')

URLS2BRAIN = []

VERSION = 'MySofie/2019.07.16'

API_VERSION = '(?i)/api/v2'

ALL_PATHS = walk(path.join(path.dirname(path.realpath(__file__)), 'handler'))

TEMPLATE_DIR = None

for root, dirs, files in ALL_PATHS:
    for file in files:

        if not file.endswith('.py'):
            continue

        data = run_path(path.join(root, file))
        if 'HANDLERS' in data:
            URLS2BRAIN.extend(data['HANDLERS'])

for each in URLS2BRAIN:
    if each[0][0] != '/':
        each[0] = '/' + each[0]
    each[0] = API_VERSION + each[0]

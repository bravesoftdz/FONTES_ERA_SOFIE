# coding: utf-8

"""
Servidor REST dinâmico

Servidor REST dinâmico que carrega todas as aplicações localizadas em um determinado diretório
(passado via parâmetro).

É baseado no Tornado..
"""

from argparse import ArgumentParser
from logging import getLogger, Formatter, StreamHandler, DEBUG
from logging.handlers import RotatingFileHandler
from os import path, makedirs
from platform import system
from runpy import run_path
from signal import signal, SIGINT

from tornado import version as tornado_version
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, URLSpec

from heart_beat import HeartBeat

brain_version = '2018.11.09'

parser = ArgumentParser(
    prog='RESTService',
    usage='Servidor REST da plataforma MySofie',
    description='Provê servidão HTTP de forma dinâmica e agnóstica'
)
parser.add_argument('-p', '--port', help='Porta de servidão HTTP', type=int, required=True)
parser.add_argument('-m', '--manifest', help='Módulo Python cuja execução retorna uma lista de URLSpecs para publicação', type=str, required=True)
parser.add_argument('-d', '--debug', help='Indica que o servidor deve rodar em modo debug', action='store_true', default=False, required=False)
ARGS = parser.parse_known_args()[0]

LOG_FORMAT = '%(name)-15s;%(process)10d;%(thread)15d;%(asctime)s;%(levelname)-8s;%(module)s->%(funcName)s:%(lineno)d;%(message)s'


def get_urls_and_version(manifest: str, logger=None) -> tuple:
    """
    Para que uma solução REST seja compatível com este servidor é necessário criar um módulo Python cuja
    execução alimente uma variável do tipo lista com instâncias compatíveis com o `Application` do Tornado.

    O nome desta variável deve ser `URLS2BRAIN`

    Também é mandatório criar uma variável denominada `VERSION` que conterá uma string com a versão da aplicação
    que esta sendo carregada

    :param manifest:
        Caminho do módulo Python
    :param logger:

    :return:
       Tupla com três elementos:

       0 - Lista com os manipuladores a serem carregados
       1 - Versão da aplicação que foi carregada
       3 - Diretório com os arquivos templates, quando aplicável
    """
    data = run_path(manifest, init_globals={'logger': logger}, run_name='manifest')

    if 'URLS2BRAIN' not in data:
        raise Exception('O manifesto não possui a variável global "URLS2BRAIN"')

    if 'VERSION' not in data:
        raise Exception('O manifesto não possui a veriável global "VERSION"')

    if 'TEMPLATE_DIR' not in data:
        raise Exception('O manifesto não possui a veriável global "TEMPLATE_DIR"')

    return data['URLS2BRAIN'], data['VERSION'], data['TEMPLATE_DIR']


def main():
    """
    Método principal de execução
    """
    logger = getLogger('RESTService')
    logger.setLevel(DEBUG)
    logger.propagate = False
    formatter = Formatter(LOG_FORMAT)

    if system() == 'Windows':
        log_dir = '.\\log'
        if not path.isdir(log_dir):
            makedirs(log_dir)
        file_name = path.join(log_dir, 'RESTService.log')
    else:
        log_dir = path.join('/var', 'log', 'sofie')
        if not path.isdir(log_dir):
            makedirs(log_dir)
        file_name = path.join(log_dir, 'RESTService.log')

    handler2file = RotatingFileHandler(
        filename=file_name,
        maxBytes=1024 * 1024 * 10,
        backupCount=20
    )
    handler2file.setLevel(DEBUG)
    handler2file.setFormatter(formatter)
    logger.addHandler(handler2file)

    if ARGS.debug:
        handler2prompt = StreamHandler()
        handler2prompt.setLevel(DEBUG)
        handler2prompt.setFormatter(formatter)
        logger.addHandler(handler2prompt)

    logger.debug(f'Carregando o manifesto {ARGS.manifest}')

    views_from_manifest, manifest_version, template_dir = get_urls_and_version(ARGS.manifest, logger)

    logger.debug('Manifesto carregado com sucesso!')

    views = list()
    views.append(URLSpec('/heart_beat/?', HeartBeat))
    views.extend(views_from_manifest)

    def log(handler):
        """
        Geração de log das chamadas REST

        :param handler:
            Manipulador acionado
        """
        logger.info(
            'Time: [%.2f ms] Method: [%s] Status: [%d] URL: [%s]',
            handler.request.request_time() * 1e3,
            handler.request.method,
            handler.get_status(),
            handler.request.uri
        )

    def set_default_headers(self):
        """
        Método que será atribuido à classe handler, sobrescrevendo a existente
        """
        self.set_header('server', f'Brain/{brain_version} (Tornado/{tornado_version}) ({manifest_version})')

    for view in views_from_manifest:
        if isinstance(view, list):
            logger.debug('Publicando o manipulador: %s', view[0])
            setattr(view[1], 'set_default_headers', set_default_headers)
        else:
            raise Exception('Tipo não previsto: {}'.format(view.__class__.__name__))

    application = Application(
        handlers=views,
        log_function=log,
        debug=ARGS.debug,
        serve_traceback=ARGS.debug,
        template_path=template_dir
    )

    old_signal_handler = None

    def stop_server(signum, frame):
        """
        Finalização graciosa do servidor.

        Executa o manipulador original e em seguida interrompe o IOLoop.
        """
        try:
            if old_signal_handler:
                old_signal_handler(signum, frame)
        except KeyboardInterrupt as err:
            logger.error(str(err))
        except Exception as err:
            logger.error(str(err))

        IOLoop.instance().stop()

    old_signal_handler = signal(SIGINT, stop_server)

    logger.info('Iniciando o servidor RESTful na porta [%d]', ARGS.port)
    HTTPServer(application).listen(ARGS.port)
    IOLoop.instance().start()

    logger.info('Processo encerrado graciosamente!')


if __name__ == '__main__':
    main()

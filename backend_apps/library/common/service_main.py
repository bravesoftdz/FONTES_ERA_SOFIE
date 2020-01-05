# coding: utf-8

"""
Artefatos para agilizar a confecção de novos micro serviços
"""

from locale import setlocale, LC_ALL
from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, Logger
from logging.handlers import RotatingFileHandler
from os import path, makedirs
from platform import system
from signal import signal, SIGINT
from threading import Event

from library.common.debug_mode import IN_DEBUG_MODE

setlocale(LC_ALL, 'pt_BR.UTF-8')

SERVICE_LOGGER = None

LOG_FORMAT = '%(name)-15s;%(process)10d;%(thread)15d;%(asctime)s;%(levelname)-8s;%(module)s->%(funcName)s:%(lineno)d;%(message)s'


def build_logger(logger_name: str) -> Logger:
    """
    :param logger_name:
        Nome do arquivo de log referente ao serviço em questão
    :return:

    """
    logger = getLogger(logger_name)
    logger.setLevel(DEBUG)
    logger.propagate = False

    formatter = Formatter(LOG_FORMAT)

    if system() == 'Windows':
        log_dir = '.\\log'
        if not path.isdir(log_dir):
            makedirs(log_dir)
        file_name = path.join(log_dir, logger_name + '.log')
    else:
        log_dir = path.join('/var', 'log', 'sofie')
        if not path.isdir(log_dir):
            makedirs(log_dir)
        file_name = path.join(log_dir, logger_name + '.log')

    handler2file = RotatingFileHandler(
        filename=file_name,
        maxBytes=1024 * 1024 * 10,
        backupCount=20
    )
    handler2file.setLevel(DEBUG if IN_DEBUG_MODE else INFO)
    handler2file.setFormatter(formatter)
    logger.addHandler(handler2file)

    if IN_DEBUG_MODE:
        handler2prompt = StreamHandler()
        handler2prompt.setLevel(DEBUG)
        handler2prompt.setFormatter(formatter)
        logger.addHandler(handler2prompt)

    return logger


def service_main(logger_name: str, callback_start, callback_stop):
    """

    :param logger_name:
        Nome do arquivo de log referente ao serviço em questão
    :param callback_start:
        Método a ser executado na inicialização do serviço
    :param callback_stop:
        Método a ser executado na finalização do serviço
    """
    global SERVICE_LOGGER
    SERVICE_LOGGER = build_logger(logger_name)

    event = Event()
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
            SERVICE_LOGGER.error(str(err))
        except Exception as err:
            SERVICE_LOGGER.error(str(err))

        event.set()

    old_signal_handler = signal(SIGINT, stop_server)

    if callback_start:
        callback_start()

    SERVICE_LOGGER.info('Servico iniciado!')

    try:
        event.wait()
    except Exception as err:
        SERVICE_LOGGER.error(str(err))
    finally:
        if callback_stop:
            callback_stop()

    SERVICE_LOGGER.info('Servico finalizado')

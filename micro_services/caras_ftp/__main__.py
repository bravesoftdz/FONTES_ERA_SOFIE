# coding: utf-8

"""
Microsserviço responsável por gerar a importação de assinaturas
"""

from library.common.service_main import service_main
from micro_services.caras_ftp.executor import CarasFTPExecutor

executor = None


def start():
    global executor
    executor = CarasFTPExecutor()
    executor.start()


def stop():
    if not executor:
        return

    executor.stop()


if __name__ == '__main__':
    service_main('CarasFTP', start, stop)


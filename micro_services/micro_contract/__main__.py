# coding: utf-8

"""
Micro serviço responsável por executar continuamente os contratos inteligentes do MySofie
"""

from library.common.service_main import service_main

from micro_services.micro_contract.executor import MicroContractExecutor

executor = None


def start():
    global executor
    executor = MicroContractExecutor()
    executor.start()


def stop():
    if not executor:
        return

    executor.stop()


if __name__ == '__main__':
    service_main('MicroContract', start, stop)

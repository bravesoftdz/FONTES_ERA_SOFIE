# coding: utf-8

"""
Micro serviço responsável por lidar com os pagamentos via Cielo
"""

from library.common.service_main import service_main

from micro_services.payment_cielo.executor import PaymentCieloExecutor

executor = None


def start():
    global executor
    executor = PaymentCieloExecutor()
    executor.start()


def stop():
    if not executor:
        return

    executor.stop()


if __name__ == '__main__':
    service_main('PaymentCielo', start, stop)

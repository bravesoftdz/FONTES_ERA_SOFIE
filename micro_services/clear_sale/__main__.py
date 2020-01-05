# coding: utf-8

"""
Microsserviço responsável por lidar com a ClearSale
"""

from library.common.service_main import service_main

from micro_services.clear_sale.executor import ClearSaleExecutor

executor = None


def start():
    global executor
    executor = ClearSaleExecutor()
    executor.start()


def stop():
    if not executor:
        return

    executor.stop()


if __name__ == '__main__':
    service_main('ClearSale', start, stop)

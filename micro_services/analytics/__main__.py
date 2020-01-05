# coding: utf-8

"""
Microsserviço responsável por lidar com o Analytics
"""

from library.common.service_main import service_main

from micro_services.analytics.executor import AnalyticsExecutor

executor = None


def start():
    global executor
    executor = AnalyticsExecutor()
    executor.start()


def stop():
    if not executor:
        return

    executor.stop()


if __name__ == '__main__':
    service_main('Analytics', start, stop)

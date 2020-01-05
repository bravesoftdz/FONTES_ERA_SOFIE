# coding: utf-8

"""

"""

from library.common.service_main import service_main

from micro_services.email_sofie.executor import EmailExecutor

executor = None


def start():
    global executor
    executor = EmailExecutor()
    executor.start()


def stop():
    if not executor:
        return

    executor.stop()


if __name__ == '__main__':
    service_main('Email', start, stop)

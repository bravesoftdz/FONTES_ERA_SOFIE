# coding: utf-8

"""

"""

from threading import Thread, Event


class CarasFTPExecutor(Thread):
    """

    """
    def __init__(self):
        """

        """
        self.__event = Event()

        super().__init__()

    def run(self):
        """
        Mantêm o thread em execução
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('CarasFTPExecutor em execução!')

        self.__event.wait()

    def stop(self):
        """
        Solicita a finalização da Thread de ClearSaleExecutor
        """
        self.__event.set()
        self.join()

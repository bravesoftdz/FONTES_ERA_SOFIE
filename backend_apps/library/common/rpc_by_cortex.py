# coding: utf-8

"""


Referências:

- https://pika.readthedocs.io/en/stable/examples/heartbeat_and_blocked_timeouts.html

"""

from collections import namedtuple
from concurrent.futures import Future
from http import HTTPStatus
from json import loads
from queue import Queue
from threading import Thread, Event, Condition, Timer
from uuid import uuid1

from pika import BasicProperties

from library.common.exception import MySofieException, MySofieExceptionBridge
from library.storage.cortex import create_new_connection

ItemRequester = namedtuple('ItemRequester', ['future', 'exchange', 'routing_key', 'body', 'correlation_id', 'expiration'])


class RPCTimeOut(MySofieException):
    """
    Indica que o micro serviço responsável por responder a solicitação RPC
    """

    status_http = HTTPStatus.BAD_GATEWAY.value

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__('Problemas relacionados ao RPC')


class Requester(Thread):
    """

    """

    def __init__(self, table_control: dict, response_queue_name: str):
        """

        :param response_queue_name:
            Nome da fila para as respostas
        """
        self.__table_control = table_control
        self.__response_queue_name = response_queue_name
        self.__queue = Queue()
        self.__condition = Condition()
        self.__stop_event = Event()

        super().__init__()

    def enqueue(self, item):
        """

        :return:
        """
        with self.__condition:
            self.__queue.put(item)
            self.__condition.notify_all()

    def cancel_request(self, correlation_id: str):
        """

        :param correlation_id:
        :return:
        """
        future, timer = self.__table_control.pop(correlation_id, (None, None))
        if timer:
            timer.cancel()
        if future:
            future.set_exception(RPCTimeOut)

    def run(self):
        """

        :return:
        """
        item = timer = None

        while True:
            try:
                with self.__condition:
                    self.__condition.wait()

                channel = create_new_connection('RPC - REQUESTER').channel()
                channel.basic_qos(prefetch_count=1)
                channel.confirm_delivery()

                while not self.__queue.empty():
                    try:
                        item: ItemRequester = self.__queue.get(False)
                        if item:

                            if item.future:
                                timer = Timer(
                                    interval=item.expiration,
                                    function=self.cancel_request,
                                    args=[item.correlation_id]
                                )

                                self.__table_control[item.correlation_id] = (item.future, timer)

                            channel.basic_publish(
                                exchange=item.exchange,
                                routing_key=item.routing_key,
                                body=item.body,
                                properties=BasicProperties(
                                    reply_to=self.__response_queue_name,
                                    correlation_id=item.correlation_id,
                                    expiration=str((item.expiration * 95 // 100) * 1000)
                                )
                            )

                            if item.future:
                                timer.start()
                    except Exception as err:
                        if item:
                            item.future.set_exception(err)

                channel.connection.close()

                if self.__stop_event.is_set():
                    break

            except Exception as err:
                # TODO: GERAR LOG
                pass

    def stop(self):
        """

        :return:
        """
        self.__stop_event.set()
        with self.__condition:
            self.__condition.notify_all()
        self.join()


class Responser(Thread):
    """

    """

    def __init__(self, table_control: dict):
        """

        """
        self.__event = Event()

        self.__table_control = table_control

        self.__channel = create_new_connection('RPC - RESPONSER').channel()
        self.__channel.basic_qos(prefetch_count=1)
        self.__channel.confirm_delivery()

        self.__queue = self.__channel.queue_declare(
            queue='',
            durable=False,
            exclusive=True,
            auto_delete=True
        )

        self.__channel.basic_consume(
            self.cortex_callback,
            queue=self.__queue.method.queue,
            no_ack=False
        )

        super().__init__()

    def cortex_callback(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        try:
            future, timer = self.__table_control.pop(properties.correlation_id, (None, None))

            if timer:
                timer.cancel()

            if future:
                data = loads(body)

                if data and 'error_code' in data:
                    future.set_exception(MySofieExceptionBridge(data))
                else:
                    future.set_result((properties.headers, data))
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        """

        :return:
        """
        self.__channel.start_consuming()

        self.__event.wait()

        self.__channel.stop_consuming()

    def stop(self):
        """

        :return:
        """
        self.__event.set()

    @property
    def response_queue_name(self):
        """

        :return:
        """
        return self.__queue.method.queue


class RPCByCortex(object):
    """

    """

    __initiated = False

    def __new__(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(RPCByCortex, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        """

        """
        if not RPCByCortex.__initiated:
            RPCByCortex.__initiated = True

            self.__table_control = dict()

            self.__responser = Responser(self.__table_control)
            self.__requester = Requester(self.__table_control, self.__responser.response_queue_name)

            self.start()

    def enqueue(self, exchange: str, routing_key: str, body: str or bytes, seconds_time_out: int = 55, wait: bool = True) -> Future or None:
        """
        Enfilera um comando em uma fila no Cortex

        :param exchange:

        :param routing_key:

        :param body:

        :param seconds_time_out:

        :param wait:
            Indica se a rotina chamadora esperará pelo resultado do processamento (True) ou não (False)
        :return:
        """
        future = Future() if wait else None
        item = ItemRequester(future, exchange, routing_key, body, str(uuid1()), seconds_time_out)
        self.__requester.enqueue(item)
        return future

    def start(self):
        """

        :return:
        """
        self.__responser.start()
        self.__requester.start()

    def stop(self):
        """

        :return:
        """
        self.__requester.stop()
        self.__responser.stop()

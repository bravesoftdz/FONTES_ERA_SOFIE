from library.common.rpc_by_cortex import RPCByCortex
from library.common.miscellaneous import to_json
from datetime import datetime


class EventBase(object):
    """


    """

    ROUTE = None

    __slots__ = ('timestamp',)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.timestamp = datetime.utcnow()

    def enqueue(self):
        RPCByCortex().enqueue('exchange_ANALYTICS', f'SOFIE.ANALYTICS.{self.ROUTE}', to_json(self.to_dict()),
                              wait=False)

    def to_dict(self):
        body = dict()

        properties = list()
        classes = list(type(self).__mro__)
        classes.reverse()
        for classe in classes:
            if hasattr(classe, '__slots__'):
                properties.extend(list(classe.__slots__))

        type_ = self.__class__.__name__

        for key in properties:
            body[key] = getattr(self, key)

        return {'type': type_,
                'data': body}

from backend_apps.events.event_base import EventBase


class TransactionCreateEvent(EventBase):
    """


    """
    ROUTE = 'TRANSACTION.CREATE'

    __slots__ = ('sofier', 'card', 'transaction')


class TransactionCancelEvent(EventBase):
    """

    """

    ROUTE = 'TRANSACTION.CANCEL'

    __slots__ = ('transaction',)


class TransactionFinishedEvent(EventBase):
    """
    
    
    """

    ROUTE = 'TRANSACTION.FINISHED'

    __slots__ = ('transaction',)


class TransactionFeedBackEvent(EventBase):
    """
    
    
    """

    ROUTE = 'TRANSACTION.FEEDBACK'

    __slots__ = ('transaction', 'nps')

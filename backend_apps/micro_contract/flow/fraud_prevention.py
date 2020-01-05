# coding: utf-8

from datetime import datetime

from library.common.rpc_by_cortex import RPCByCortex
from library.common.miscellaneous import to_json


class FraudPreventionFlow(object):
    """

    """

    def __init__(self, vendor: str, micro_contract):
        """

        :param vendor:
        :param micro_contract:
        """
        self.__vendor = vendor
        self.__micro_contract = micro_contract
        super().__init__()

    def execute(self):
        """

        :return:
        """
        future = RPCByCortex().enqueue(
            exchange='exchange_FRAUD',
            routing_key='SOFIE.FRAUD.PREVENTION.{}.{}'.format(self.__vendor, self.__micro_contract.transaction.transaction),
            body=to_json({})
        )
        data = future.result()[1]

        self.__micro_contract.transaction.fraud_prevention.vendor = self.__vendor
        self.__micro_contract.transaction.fraud_prevention.approved = data['Rating'] > 3
        self.__micro_contract.transaction.fraud_prevention.when = datetime.utcnow()
        self.__micro_contract.transaction.fraud_prevention.log.append(data)
        self.__micro_contract.transaction.save_soul()

        return self.__micro_contract.transaction.fraud_prevention.approved

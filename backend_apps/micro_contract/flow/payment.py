# coding: utf-8

from datetime import datetime

from library.common.exception import MySofieException
from library.common.rpc_by_cortex import RPCByCortex
from library.common.miscellaneous import to_json


class NotAuthorized(MySofieException):
    """
    Indica que a pré autorização não foi efetuada
    """

    def __init__(self, reason: str):
        """

        """
        self.__reason = reason
        super().__init__('Operação não autorizada pela adquirente: [{}]'.format(reason))


class PaymentFlow(object):
    """
    Processa o fluxo de pagamento junto ao adquirente
    """

    def __init__(self, acquirer: str, micro_contract):
        """
        Inicia o objeto

        :param acquirer:
            Nome do adquirente
        """
        self.__acquirer = acquirer
        self.__micro_contract = micro_contract
        super().__init__()

    def pre_validation(self, number: str) -> str:
        """
        Efetua a pré-validação do cartão retornando a bandeira do mesmo

        :return:
            `str`
        """
        self.__micro_contract.transaction.payment_info.credit_card.acquirer = self.__acquirer
        future = RPCByCortex().enqueue(
            exchange='exchange_PAYMENT',
            routing_key='PAYMENT.{}.{}.QUERYBIN'.format(self.__acquirer, self.__micro_contract.transaction.transaction),
            body=to_json({'number': number})
        )
        data = future.result()[1]

        self.__micro_contract.transaction.payment_info.credit_card.validation.valid = data['is_valid']
        self.__micro_contract.transaction.payment_info.credit_card.validation.when = datetime.utcnow()
        self.__micro_contract.transaction.payment_info.credit_card.validation.log.append(data)
        self.__micro_contract.transaction.save_soul()

        if data['is_valid']:
            return data['provider']
        else:
            raise NotAuthorized('Não é um cartão de crédito ativo')

    def pre_authorization(self, credit_card_info: dict) -> str:
        """
        Efetua a pré autorização retornando o ID do pagamento

        :return:
            `str`
        """
        future = RPCByCortex().enqueue(
            exchange='exchange_PAYMENT',
            routing_key='PAYMENT.{}.{}.AUTHORIZATION'.format(self.__acquirer, self.__micro_contract.transaction.transaction),
            body=to_json(credit_card_info),
        )
        data = future.result()[1]

        self.__micro_contract.transaction.payment_info.credit_card.authorization.authorized = isinstance(data, dict) and data['Payment']['ReturnCode'] == '00'
        self.__micro_contract.transaction.payment_info.credit_card.authorization.when = datetime.utcnow()
        self.__micro_contract.transaction.payment_info.credit_card.authorization.log.append(data)
        self.__micro_contract.transaction.save_soul()

        if not self.__micro_contract.transaction.payment_info.credit_card.authorization.authorized:
            if isinstance(data, dict):
                raise NotAuthorized(data['Payment']['ReturnMessage'])
            else:
                raise NotAuthorized(data[0]['Message'])

        return data['Payment']['PaymentId']

    def capture(self, payment_id: str) -> bool:
        """
        Efetiva a captura do valor no cartão de crédito

        :return:
            `bool` Indica o sucesso, ou não, da operação
        """
        info_data = {
            'order_id': payment_id
        }
        future = RPCByCortex().enqueue(
            exchange='exchange_PAYMENT',
            routing_key='PAYMENT.{}.{}.CAPTURE'.format(self.__acquirer, self.__micro_contract.transaction.transaction),
            body=to_json(info_data),
        )
        data = future.result()[1]

        self.__micro_contract.transaction.payment_info.credit_card.catch.captured = isinstance(data, dict)
        self.__micro_contract.transaction.payment_info.credit_card.catch.when = datetime.utcnow()
        self.__micro_contract.transaction.payment_info.credit_card.catch.log.append(data)
        self.__micro_contract.transaction.save_soul()

        if not self.__micro_contract.transaction.payment_info.credit_card.catch.captured:
            raise NotAuthorized(data[0]['Message'])

        return True

    def cancel(self, payment_id: str) -> bool:
        """

        :param payment_id:
        :return:
        """
        info_data = {
            'order_id': payment_id
        }
        future = RPCByCortex().enqueue(
            exchange='exchange_PAYMENT',
            routing_key='PAYMENT.{}.{}.CANCEL'.format(self.__acquirer, self.__micro_contract.transaction.transaction),
            body=to_json(info_data),
        )
        data = future.result()[1]

        self.__micro_contract.transaction.payment_info.credit_card.cancellation.canceled = isinstance(data, dict)
        self.__micro_contract.transaction.payment_info.credit_card.cancellation.when = datetime.utcnow()
        self.__micro_contract.transaction.payment_info.credit_card.cancellation.log.append(data)
        self.__micro_contract.transaction.save_soul()

        if not self.__micro_contract.transaction.payment_info.credit_card.cancellation.canceled:
            raise NotAuthorized(data[0]['Message'])

        return True

# coding: utf-8

"""
Artefatos base para a representação e execução de uma tansação
"""

from datetime import datetime
from uuid import uuid1

from library.common.exception import ResourceNotFound
from library.storage.config import ConfigStorage
from library.storage.relation import RelationStorage
from micro_contract.actors.address import Address
from micro_contract.actors.card import Card
from micro_contract.actors.company import Company
from micro_contract.actors.consumer import Consumer
from micro_contract.actors.fraud_prevention import FraudPrevention
from micro_contract.actors.geo import GeoLocation
from micro_contract.actors.payment_condition import PaymentCondition
from micro_contract.actors.payment_info import PaymentInfo
from micro_contract.actors.sofier import Sofier
from micro_contract.actors.status import StatusTransaction
from micro_contract.actors.feedback_consumer import FeedbackConsumer
from micro_contract.exception import CardAlreadyDefined, CardNotDefined, ConsumirAlreadyDefined, PaymentNotApplicable, SofierAlreadyDefined, TransactionClosed, PaymentConditionNotSupported, TransactionNotFound


class Transaction(object):
    """
    Classe que representa uma transação independentemente da modelagem dos dados
    """

    CYPHER_RELATIONS = """
    MERGE (transaction:TRANSACTION {name: {transaction}})
    WITH transaction
    
    MATCH (sofier:SOFIER {name: {sofier}}) 
    MATCH (consumer:CONSUMER {name: {consumer}})
    MATCH (address:ADDRESS {name: {address}})
    MATCH (card:CARD {name: {card}})
    MATCH (company:COMPANY {name: {company}})
    
    MERGE (transaction)-[:PART]->(sofier)
    MERGE (transaction)-[:PART]->(consumer)
    MERGE (transaction)-[:PART]->(address)
    MERGE (transaction)-[:PART]->(card)
    MERGE (transaction)-[:PART]->(company)
    """

    def __init__(self, transaction: str or None = None):
        """
        Inicializa o objeto, sendo que se por

        :param transaction:
            ID da transação
        """
        self.__obj_consumer = None
        self.__obj_card = None
        self.__obj_sofier = None
        self.__obj_company = None
        self.__obj_address = None
        self.__obj_payment_condition = None
        self.__obj_payment_info = None
        self.__obj_status = None
        self.__obj_geo = None
        self.__obj_fraud_prevention = None
        self.__obj_feedback_consumer = None

        if transaction:
            self.__transaction = transaction
            self.__soul = self._get_soul()
        else:
            self.__transaction = str(uuid1())
            self.__soul: dict = {'transaction': self.__transaction, 'when': datetime.utcnow()}
            self.status.status = 'DATA_COLLECT'
            self.save_soul()

        super().__init__()

    def __repr__(self):
        """

        :return:
        """
        return f'Transaction({self.__transaction})'

    def _get_soul(self):
        """
        Recupera os dados da transação do banco de dados cacheando os dados por 10 minutos
        """
        buffer = ConfigStorage().config['transaction'].find_one({'transaction': self.__transaction}, {'_id': 0})
        if not buffer:
            raise TransactionNotFound(self.__transaction)

        return buffer

    def is_in_data_collect(self) -> bool:
        """

        :return:
        """
        if self.status.status != 'DATA_COLLECT':
            raise TransactionClosed()

        return True

    def save_soul(self):
        """
        Persiste o novo estado representacional da transação no banco de dados, limpando o cache.
        """
        self.__soul.update({
            'status': self.status.soul,
            'actors': {
                'address': self.address.address if self.address else None,
                'card': self.card.card if self.card else None,
                'company': self.company.company if self.company else None,
                'consumer': self.consumer.consumer if self.consumer else None,
                'sofier': self.sofier.sofier if self.sofier else None,
            },
            'geo': self.geo.soul,
            'fraud_prevention': self.fraud_prevention.soul if self.fraud_prevention else None,
            'payment_condition': self.payment_condition.soul if self.payment_condition else None,
            'payment_info': self.payment_info.soul,
            'payment_link': self.payment_link,
            'feedback_consumer': self.feedback_consumer.soul,
        })

        ConfigStorage().config['transaction'].update({'transaction': self.__transaction}, self.__soul, upsert=True)

    def create_relations(self):
        """
        Cria os relacionamentos entre uma transação e outras classes de recurso:

        - SOFIER
        - CONSUMIDOR
        - ENDEREÇO
        - CARD
        - COMPANY
        """
        RelationStorage().run(
            Transaction.CYPHER_RELATIONS,
            transaction=self.transaction,
            sofier=self.sofier.sofier if self.sofier else '',
            consumer=self.consumer.consumer if self.consumer else '',
            address=self.address.address if self.address else '',
            card=self.card.card if self.card else '',
            company=self.company.company if self.company else ''
        )

    def __get_card(self) -> Card:
        """
        Retorna a representação do Card, caso o mesmo esteja definido

        :return:
            ID do Card
        """
        if not self.__obj_card:
            try:
                if self.__soul['actors']['card']:
                    self.__obj_card = Card(self.__soul['actors']['card'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_card

    def __set_card(self, card: str):
        """
        Valida o CARD ao qual a transação fará referência. As regras são:

        [X] A Transação não pode ter um Card já associado
        [ ] A Transação deve estar no status 'DATA_COLLECT'
        [ ] O Card tem que existir: estar ativo, estar na validade

        :param card:
            ID do Card
        """
        self.is_in_data_collect()

        if self.__obj_card:
            raise CardAlreadyDefined()

        self.__obj_card = Card(card)

    def __get_sofier(self) -> Sofier:
        """
        Retorna a representação do Sofier, caso o mesmo esteja definido

        :return:
            Representação do Sofier
        """
        if not self.__obj_sofier:
            try:
                if self.__soul['actors']['sofier']:
                    self.__obj_sofier = Sofier(self.__soul['actors']['sofier'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_sofier

    def __set_sofier(self, value: str):
        """
        Valida o SOFIER ao qual a transação fará referências. As regras são:

        [X] A Transação não pode ter um Sofier já associado
        [ ] O Sofier tem que: existir, estar ativo

        :param value:
            ID do Sofier
        """
        self.is_in_data_collect()

        if self.__obj_sofier:
            raise SofierAlreadyDefined()

        self.__obj_sofier = Sofier(value)

    def __get_consumer(self) -> Consumer:
        """
        Retorna a representação do Consumidor, caso o mesmo esteja definido

        :return:
            Representação o Consumidor
        """
        if not self.__obj_consumer:
            try:
                if self.__soul['actors']['consumer']:
                    self.__obj_consumer = Consumer(self.__soul['actors']['consumer'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_consumer

    def __set_consumer(self, value: str):
        """
        Valida o CONSUMIDOR ao qual a transação fará referências. As regras são:

        [X] A Transação não pode ter um Consumidor já associado
        [ ] O Consumidor tem que: existir, estar ativo

        :param value:
            ID do Sofier
        """
        self.is_in_data_collect()

        if self.__obj_consumer:
            raise ConsumirAlreadyDefined()

        self.__obj_consumer = Consumer(value)

    def __get_payment_condition(self) -> PaymentCondition:
        """
        Retorna a representação da Condição de Pagamento, caso a mesma esteja definida

        :return:
            Representação da Condição de Pagamento
        """
        if not self.__obj_payment_condition:
            try:
                if self.__soul['payment_condition']:
                    self.__obj_payment_condition = PaymentCondition(None, None).from_soul(self.__soul['payment_condition'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_payment_condition

    def __set_payment_condition(self, value: str):
        """
        Valida a Condição de Pagamento escolhida. As regras são:

        [X] - O Card deve estar na fse `DATA_COLLECT`
        [X] - O Card deve estar definido
        [X] - O Card não deve ser do expertise SALE
        [ ] - A Condição de Pagamento deve estar previsto no Card

        :param value:
            ID da condição de pagamento
        """
        self.is_in_data_collect()

        if not self.card:
            raise CardNotDefined()

        if self.card.expertise != 'SALE':
            raise PaymentNotApplicable()

        try:
            self.__obj_payment_condition = PaymentCondition(self.card.card, value)
        except ResourceNotFound:
            raise PaymentConditionNotSupported(value)

    def __get_company(self) -> Company:
        """
        Retorna a representação da Empresa ao qual o Card, e consequêntemente a Transação, esta associada

        :return:
            Representação da Empresa
        """
        if not self.__obj_company and self.card:
            self.__obj_company = Company(self.card.company)

        return self.__obj_company

    def __get_address(self) -> Address:
        """
        Retorna a representação do Endereço associado à Transação, caso a mesma esteja definida

        :return:
        """
        if not self.__obj_address:
            try:
                if self.__soul['actors']['address']:
                    self.__obj_address = Address(self.__soul['actors']['address'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_address

    def __set_address(self, value):
        """
        Valida o código de Endereço escolhido. As regras são:

        [ ] - A trasação NÃO pode estar finalizada
        [ ] - O Endereço deve exisitir no cadastro
        [ ] - O Endereço deve estar associado ao Consumidor

        :param value:
            ID do Endereço sendo associado
        """
        self.is_in_data_collect()

        self.__obj_address = Address(value)

    def __get_payment_info(self) -> PaymentInfo:
        """

        :return:
        """
        if not self.__obj_payment_info:
            try:
                if self.__soul['payment_info']:
                    self.__obj_payment_info = PaymentInfo(self.__soul['payment_info'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_payment_info or PaymentInfo(dict())

    def __get_fraud_prevention(self) -> FraudPrevention:
        """

        :return:
        """
        if not self.__obj_fraud_prevention:
            try:
                if self.__soul['fraud_prevention']:
                    self.__obj_fraud_prevention = FraudPrevention(self.__soul['fraud_prevention'])
            except KeyError:
                pass
            except Exception:
                raise

        return self.__obj_fraud_prevention or FraudPrevention(dict())

    def __get_status(self) -> StatusTransaction:
        """

        :return:
        """
        if not self.__obj_status:
            try:
                if self.__soul['status']:
                    self.__obj_status = StatusTransaction(self.__soul['status'])
            except KeyError:
                self.__obj_status = StatusTransaction(dict())
            except Exception:
                raise

        return self.__obj_status

    def __get_geo(self) -> GeoLocation:
        """

        :return:
        """
        if not self.__obj_geo:
            try:
                self.__obj_geo = GeoLocation(self.__soul['geo'])
            except KeyError:
                self.__obj_geo = GeoLocation(dict())
            except Exception:
                raise

        return self.__obj_geo

    def __get_payment_link(self) -> dict:
        """

        :return:
        """
        if not self.__soul.get('payment_link'):
            self.__soul['payment_link'] = dict()

        return self.__soul['payment_link']

    def __set_payment_link(self, value: dict):
        """

        :param value:
        :return:
        """
        self.__soul['payment_link'] = value

    def __get_feedback_consumer(self) -> FeedbackConsumer:
        """

        :return:
        """
        if not self.__obj_feedback_consumer:
            self.__obj_feedback_consumer = FeedbackConsumer(self.__soul.get('feedback_consumer', dict()))

        return self.__obj_feedback_consumer

    card = property(__get_card, __set_card)

    sofier = property(__get_sofier, __set_sofier)

    consumer = property(__get_consumer, __set_consumer)

    company = property(__get_company)

    address = property(__get_address, __set_address)

    payment_condition = property(__get_payment_condition, __set_payment_condition)

    payment_info = property(__get_payment_info)

    fraud_prevention = property(__get_fraud_prevention)

    status = property(__get_status)

    geo = property(__get_geo)

    payment_link = property(__get_payment_link, __set_payment_link)

    feedback_consumer = property(__get_feedback_consumer)

    @property
    def transaction(self) -> str:
        """
        Expõe o atributo `transaction`

        :return:
            String representando o ID da transação
        """
        return self.__transaction

    @property
    def when(self) -> datetime:
        """

        :return:
        """
        return self.__soul['when']

    @property
    def soul(self) -> dict:
        """

        :return:
        """
        return self.__soul

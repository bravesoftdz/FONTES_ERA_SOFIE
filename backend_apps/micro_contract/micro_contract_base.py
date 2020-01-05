# coding: utf-8

"""
Aglutina as classes base para a execução de um micro contrato
"""

from abc import abstractmethod
from json import dumps
from locale import currency

from crud.sofier import SofierCRUD
from email_templates.send_email_by_template import EMailTemplate
from library.common.governance import DEVELOPER_SESSION
from library.common.miscellaneous import to_json
from library.common.paging_info import PagingInfo
from library.common.rpc_by_cortex import RPCByCortex
from library.storage.caching import CachingStorage
from library.storage.session import SessionStorage
from micro_contract.actors.consumer import Consumer
from micro_contract.exception import PaymentMethodNotSupported, DoubleSpend, TransactionCanceled
from micro_contract.flow.fraud_prevention import FraudPreventionFlow
from micro_contract.flow.payment import PaymentFlow
from micro_contract.transaction import Transaction
from the_3rd.gmail.email_sender import EMailSender
from the_3rd.zenvia.sms_sender import SMSSender


class MicroContractBase(object):
    """
    Classe base para codificar um micro contrato no âmbito de customização
    """

    def __init__(self, transaction: str or None):
        """
        Inicializa o objeto
        """
        self.__transaction = Transaction(transaction)
        super().__init__()

    @abstractmethod
    def after_finished(self):
        """
        Método a ser sobrescrito pelos contratos descendentes a fim de executar procedimentos após a
        *finalização* de uma transação.
        """
        pass

    def cancel(self):
        """

        :return:
        """
        self.feed_status(status='CANCELED')

    def feed_status(self, status: str or None = None, success: bool or None = None, reason: str or None = None, reason_code: int or None = None, stage: int or None = None):
        """

        :param status:
        :param success:
        :param reason:
        :param reason_code:
        :param stage:
        :return:
        """
        if status:
            self.transaction.status.status = status

        if success is not None:
            self.transaction.status.success = success

        if reason:
            self.transaction.status.reason = reason

        if reason_code:
            self.transaction.status.reason_code = reason_code

        if stage:
            self.transaction.status.set_stage_ok(stage)

        self.transaction.save_soul()

        # TODO: VERIFICAR SERVENTIA DESTE CACHE
        CachingStorage().storage.setex(f'MYSOFIE:TRANSACTION:{self.transaction.transaction}:STATUS#', 60 * 60 * 24, dumps(self.transaction.status.soul))

    def send_email_with_receipt(self):
        """
        Envia o email com o recibo da transação
        """
        email = EMailTemplate()
        email.template = 'receipt.html'
        email.subject = f'Seu recibo de transação na Sofie em {self.transaction.when.strftime("%d/%m/%Y")}'
        email.to = self.transaction.consumer.email
        email.data = {
            'transaction': self.transaction.transaction,
            'sofier_name': self.transaction.sofier.full_name,
            'when': self.transaction.when.strftime('%d/%m/%Y'),
            'description': self.transaction.card.formatted_title,
            'payment': f'{self.transaction.payment_condition.quotes} X de {currency(self.transaction.payment_condition.quote_value, grouping=True)}',
            'total_value': currency(self.transaction.payment_condition.price, grouping=True),
            'address': self.transaction.address.formated_address,
            'consumer_name': self.transaction.consumer.full_name
        }
        email.content_id = {
            'logo': 'logotipo_321X119.png',
            'star_regular': 'star_regular.png',
            'thank_you': 'thank_you.gif',
            'whatsapp': 'whatsapp.png',
            'sofier': SofierCRUD(PagingInfo(), DEVELOPER_SESSION).recover_image(self.transaction.sofier.sofier, 48, 48)[1]
        }

        email.enqueue()

    def clause_set_payment_condition(self, **kwargs):
        """
        Informa a condição de pagamento escolhida para a *Transação*

        :param kwargs:
            - `payment_condition`: Referência à condição de pagamento escolhida

        """
        self.__transaction.payment_condition = kwargs['payment_condition']

        self.__transaction.payment_info.method = self.__transaction.payment_condition.method

        self.__transaction.save_soul()

    def clause_set_consumer(self, **kwargs):
        """
        Definie o consumidor que estará associado à transação

        :param kwargs:
            - consumer: ID do Consumidor
        """
        consumer = kwargs['consumer']

        Consumer.exists(consumer)

        self.__transaction.consumer = consumer
        self.__transaction.save_soul()

    def clause_set_address(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        self.__transaction.address = kwargs['address']
        self.__transaction.save_soul()

    def clause_send_payment_link(self, **kwargs) -> dict:
        """
        Monta o link de pagamento, colocando a transação na fase de pagamento

        :param kwargs:
            Dicionário com as mídias relevantes ao chamador:

            >>> {
            ...     'via': {
            ...         'sms' : bool,
            ...         'email': bool,
            ...         'whatsapp': bool,
            ...         'web': bool
            ...      }
            ... }

        :return:
            Dicionário com links que são relevantes ao chamador (e.g. WhatsApp)
        """
        buffer = dict()

        url_base = f'https://mysofie.com/pay/?transaction={self.transaction.transaction}&media={{}}'

        #: VIA SMS
        try:
            if kwargs['via']['sms']:
                link_sms = url_base.format('sms')

                sms = SMSSender()
                sms(
                    self.transaction.consumer.phone,
                    f'{link_sms} - desconsidere se já foi pago.',
                    self.transaction.transaction
                )
        except KeyError:
            pass
        except Exception:
            raise

        #: VIA EMAIL
        try:
            if kwargs['via']['email']:
                link_email = url_base.format('email')

                email = EMailSender()
                email.subject = 'Sofie Pay | Pague com segurança e privacidade'
                email.to.append(self.transaction.consumer.email)
                email.msg = f"""
                            <strong>Parabéns pela sua aquisição!</strong><br/><br/>
            
                            Falta pouco para concluirmos. Clique no link abaixo para efetuar o pagamento:<br/><br/>
            
                            <strong>{link_email}</strong>
                            """
                email()
        except KeyError:
            pass
        except Exception:
            raise

        #: VIA WHATSAPP
        try:
            link_whatsapp = url_base.format('whatsapp')
            buffer['link_whatsapp'] = link_whatsapp
        except KeyError:
            pass
        except Exception:
            raise

        #: VIA WEB
        try:
            if kwargs['via']['web']:
                link_whatsapp = url_base.format('web')
                buffer['link_web'] = link_whatsapp
        except KeyError:
            pass
        except Exception:
            raise

        SessionStorage().storage.setex(f'MYSOFIE:TRANSACTION:{self.transaction.transaction}:PAYLINK#', 60 * 10, None)
        self.feed_status(stage=1)

        return buffer

    def clause_process_payment(self, **kwargs) -> dict:
        """
        Processa o pagamento do Card associado a esta transação

        :param kwargs:
            Parâmetros
        :return:
            `dict`
        """
        success, captured, reason, payment_id = False, False, '', None

        #: FOI CANCELADO?
        if self.transaction.status.status == 'CANCELED':
            raise TransactionCanceled(self.transaction.transaction)

        #: AINDA NÃO FOI PAGO?
        if self.transaction.status.status in ('PROCESSING', 'FINISHED'):
            raise DoubleSpend()

        #: TUDO CERTO?
        if self.transaction.payment_info.method != 'CREDIT_CARD':
            raise PaymentMethodNotSupported(self.transaction.payment_info.method)

        #: COLOCANDO A TRANSAÇÃO EM PROCESSAMENTO
        self.feed_status(status='PROCESSING')

        #: INSTANCIANDO FLUXO DE PGTO
        flow = PaymentFlow('CIELO', self)

        try:
            #: PRÉ VALIDAÇÃO DO CARTÃO
            provider = flow.pre_validation(kwargs['number'])

            credit_card = {
                'flag': {'VISA': 'Visa', 'MASTERCARD': 'Master'}.get(provider, provider),
                'value': self.transaction.payment_condition.price,
                'installments': self.transaction.payment_condition.quotes,
                'soft_description': self.transaction.card.description_on_invoice
            }
            credit_card.update(kwargs)

            #: PRÉ AUTORIZAÇÃO
            payment_id = flow.pre_authorization(credit_card)

            #: PREVENÇÃO À FRAUDE
            fraud = FraudPreventionFlow('CLEAR_SALE', self)
            approved = fraud.execute()

            #: CAPTURA
            if approved:
                captured = flow.capture(payment_id)

            if captured:
                #: CRÉDITO AO SOFIER
                info_data = {
                    'part_type': 'sofier',
                    'part_id': self.transaction.sofier.sofier,
                    'transaction': self.transaction.transaction,
                    'value': self.transaction.payment_condition.reward,
                    'description': f'{self.transaction.card.title} - {self.transaction.consumer.full_name.upper()}'
                }
                future = RPCByCortex().enqueue(
                    exchange='exchange_LEDGER',
                    routing_key='SOFIE.LEDGER.ENTRY',
                    body=to_json(info_data),
                )
                data = future.result()[1]

                #: DEFININDO O STATUS FINAL DA TRANSAÇÃO
                success = True
                self.feed_status(status='FINISHED', success=True, reason_code=0, stage=4)

                #: RECIBO AO CONSUMIDOR
                self.send_email_with_receipt()

            else:
                #: DEFININDO O STATUS FINAL DA TRANSAÇÃO
                self.feed_status(status='FINISHED', success=False, reason_code=2, stage=4)

            #: AFTER FINISHED
            self.after_finished()

        except Exception as err:
            #: DEFININDO O STATUS FINAL DA TRANSAÇÃO
            reason = str(err)
            self.feed_status(status='FINISHED', success=success, reason=reason, reason_code=3, stage=4)

        finally:
            if not success and payment_id:
                flow.cancel(payment_id)

        #: RESULTADO FINAL
        return {'success': success}

    @property
    def transaction(self) -> Transaction:
        """
        Expõe o atributo `transaction`

        :return:
            Intância de `Transaction`
        """
        return self.__transaction

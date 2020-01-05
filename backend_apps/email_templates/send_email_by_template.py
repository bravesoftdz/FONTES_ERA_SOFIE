# coding: utf-8

"""
A fim de facilitar o envio de email por parte do Assistente Sofie criou-se esta facilidade.

Espera-se que a cada novo __template__ de email seja criado um arquivo HTML em `./template` e que este arquivo seja aderente
ao recurso de interpolação ofereicido pelo Tornado.

Recursos de mídia, como uma imagem, devem ser localizados em `./media`.

# Exemplo de utilização

>>> worker = EMailTemplate() #: Instância o objetoi
>>> worker.to = 'jmarioguedes@gmail.com, mario.guedes@mysofie.com' #: Determina o destinatário
>>> worker.subject = 'e-Mail de teste' #: Determina o assunto do email
>>> worker.template = 'reset_password.html' #: Determina o template que será utilizado, que é o arquivo pré existente
>>> worker.data = {'link_to_recover': 'https://mysofie.com/reset_password/?token=1234567890'} #: Dados para a interpolação

# Para delegar o envio para o MS `email_sofie`

>>> worker.enqueue()

# Para efetivamente enviar o email

>>> worker() #: Envio do email propriamente dito
   
"""

from os import path
from pickle import dumps

from tornado.template import Template

from library.common.rpc_by_cortex import RPCByCortex
from the_3rd.gmail.email_sender import EMailSender


class EMailTemplate(object):
    """
    Classe facilitadora para confecção de um e-mail à partir do *Assistente Sofie*
    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        self.__template = None
        self.__subject = None
        self.__to = None
        self.__data = None
        self.__content_id = None

    def enqueue(self):
        """
        Se autoenfilera no Cortex para o MS `email_sofie`
        """
        RPCByCortex().enqueue(
            exchange='exchange_EMAIL_SOFIE',
            routing_key='SOFIE.ASSISTANT_SOFIE.EMAIL.SEND',
            body=dumps(self),
            wait=False
        )

    def __call__(self):
        """
        Executa a funcionalidade propriamente dita
        """
        file_name = path.join(path.dirname(path.realpath(__file__)), 'template', self.__template)
        with open(file_name, 'rt', encoding='utf-8') as file:
            content = file.read()

        template = Template(content)
        content = template.generate(**self.__data if self.__data else dict())

        email = EMailSender()
        email.subject = self.__subject
        email.to.append(self.__to)
        email.msg = content.decode()

        if self.__content_id:
            for cid, media_name in self.__content_id.items():

                if isinstance(media_name, bytes):
                    email.attachments[cid] = media_name
                else:
                    file_name = path.join(path.dirname(path.realpath(__file__)), 'media', media_name)
                    with open(file_name, 'rb') as file:
                        email.attachments[cid] = file.read()
        email()

    @property
    def template(self) -> str:
        """

        :return:
        """
        return self.__template

    @template.setter
    def template(self, value: str):
        """

        :param value:
        :return:
        """
        self.__template = value

    @property
    def subject(self) -> str:
        """

        :return:
        """
        return self.subject

    @subject.setter
    def subject(self, value: str):
        """

        :param value:
        :return:
        """
        self.__subject = value

    @property
    def to(self) -> str:
        """

        :return:
        """
        return self.__to

    @to.setter
    def to(self, value: str):
        """

        :param value:
        :return:
        """
        self.__to = value

    @property
    def data(self) -> dict:
        """

        :return:
        """
        return self.__data

    @data.setter
    def data(self, value: dict):
        """

        :param value:
        :return:
        """
        self.__data = value

    @property
    def content_id(self) -> dict:
        """

        :return:
        """
        return self.__content_id

    @content_id.setter
    def content_id(self, value: dict):
        """

        :param value:
        :return:
        """
        self.__content_id = value


if __name__ == '__main__':
    worker = EMailTemplate()
    worker.to = 'jmarioguedes@gmail.com'
    worker.subject = 'e-Mail de teste'
    worker.template = 'reset_password.html'
    worker.data = {'link_to_recover': 'https://mysofie.com/reset_password/?token=1234567890'}
    worker()

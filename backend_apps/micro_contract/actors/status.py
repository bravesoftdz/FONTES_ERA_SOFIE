# coding: utf-8

"""

"""


class StatusTransaction(object):
    """
    Representa o status de execução de uma transação
    """

    def __init__(self, soul: dict):
        """
        Inicializa o objeto

        :param soul:
             Dicionário que representa o status da transação
        """
        self.__soul = {
            'status': 'CREATED',
            'success': None,
            'reason': None,
            'processing_stages': {
                'stage_1': False,
                'stage_2': False,
                'stage_3': False,
                'stage_4': False
            }
        }
        self.__soul.update(soul)
        super().__init__()

    def set_stage_ok(self, stage: int):
        """
        Marca um determinado estágio como concluído (`True`)

        :param stage:
            Identificação ordinal do estágio (1, 2, 3 ...)
        """
        sub_key = 'stage_{}'.format(stage)
        self.__soul['processing_stages'][sub_key] = True

    @property
    def status(self) -> str:
        """
        Retorna o status de uma transação

        :return:
            `str`
        """
        return self.__soul['status']

    @status.setter
    def status(self, value: str):
        """
        Define o status de uma transação

        :param value:
            Novo status
        """
        assert value in ('CREATED', 'DATA_COLLECT', 'PROCESSING', 'FINISHED', 'CANCELED'), 'O status de transação [{}] não é reconhecido'.format(value)

        self.__soul['status'] = value

    @property
    def success(self) -> bool:
        """
        Retorna se a Transação foi finalizada com sucesso ou não

        :return:
            `bool`
        """
        return self.__soul['success']

    @success.setter
    def success(self, value: bool):
        """
        Define se a Transação foi finalizada com sucesso ou não

        :param value:
            `bool`
        """
        self.__soul['success'] = value

    @property
    def reason(self) -> str:
        """

        :return:
        """
        return self.__soul.get('reason', '')

    @reason.setter
    def reason(self, value: str):
        """

        :return:
        """
        self.__soul['reason'] = value

    @property
    def reason_code(self) -> int:
        """

        :return:
        """
        return self.__soul.get('reason_code', -1)

    @reason_code.setter
    def reason_code(self, value: int):
        """

        :param value:
        :return:
        """
        self.__soul['reason_code'] = value

    @property
    def soul(self) -> dict:
        """
        Expõe o dicionário dos dados que representam o status de uma transação

        :return:
            `dict`
        """
        return self.__soul

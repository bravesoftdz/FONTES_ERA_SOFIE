# coding: utf-8

"""

"""

from datetime import datetime
from decimal import Decimal

from library.crud.crud_base import CRUDBase, AllowedLevels
from library.storage.caching import apply_caching
from library.common.governance import LEVEL_DEVELOPER, LEVEL_SOFIER


def set_now(buffer) -> dict:
    """

    :param buffer:
    :return:
    """
    if buffer:
        buffer['balance']['date'] = datetime.utcnow()

    return buffer


class LedgerCRUD(CRUDBase):
    """

    """

    resource_class = 'ledger'

    scheme = None

    levels_permissions = AllowedLevels(
        listing=[LEVEL_SOFIER, LEVEL_DEVELOPER],
        item=[LEVEL_SOFIER, LEVEL_DEVELOPER],
        create=[LEVEL_SOFIER, LEVEL_DEVELOPER],
        archive=[LEVEL_DEVELOPER],
        modify=[LEVEL_DEVELOPER]
    )

    def get_keys_to_clear_cache(self, document: dict) -> list:
        """
        Método a ser sobrescrito nas classes descendentes com o propósito de devolver a lista de chaves para limpeza de
        cache

        :param document:
            Documento que engatilhou a limpeza do cache
        """
        return ['MYSOFIE:CACHE:SOFIER:{}:WALLET:BALANCE#'.format(document['part']['id'])]

    @apply_caching('MYSOFIE:CACHE:SOFIER:{2}:WALLET:BALANCE#', 60 * 60 * 24 * 7, callback=set_now)
    def balance(self, part_type: str, part_id: str):
        """

        :param part_type:
        :param part_id:
        :return:
        """
        list_movement: list = self.listing(**{'part.type': part_type, 'part.id': part_id})['data']
        list_movement.reverse()

        final_balance = sum([+Decimal(str(each['value'])) if each['type'] == 'Cr' else -Decimal(str(each['value'])) for each in list_movement])

        return {
            'part': {
                'type': part_type,
                'id': part_id
            },
            'balance': {
                'date': datetime.utcnow(),
                'final_balance': float(final_balance)
            },
            'movement': list_movement
        }

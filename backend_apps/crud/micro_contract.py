# coding: utf-8

"""
CRUD referente à classe de recurso Micro Serviço
"""

from library.crud.crud_base import CRUDBase
from scheme.micro_contract import SCHEME_MICROCONTRACT


class MicrocontractCRUD(CRUDBase):
    """
    CRUD referente à classe de recurso Micro Serviço
    """
    resource_class = 'micro_contract'

    scheme = SCHEME_MICROCONTRACT

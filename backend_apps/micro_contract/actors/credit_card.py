# coding: utf-8

from pyDes import triple_des


def descript(content: str) -> dict:
    """

    :return:
    """
    k = triple_des('32379386889', )
    buffer = k.decrypt(content)

    return buffer


if __name__ == '__main__':
    result = descript('U2FsdGVkX1/BlYR1F6oSThvMWKhARNSbSJZwbZRRmetP6cMmMW+blpRCs7F/imPRMBMmSPgnEhoXpSBevhoMn8YlnBGIKiDN')

    if result == '123456|THIAGO|112018|1234|ce56ee73a303675fb542c5f3d616f6b8':
        print('SUCESSO')
    else:
        print('INSUCESSO')

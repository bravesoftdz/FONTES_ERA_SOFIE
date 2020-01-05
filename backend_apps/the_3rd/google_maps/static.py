# coding: utf-8

from requests import get

API_KEY = 'AIzaSyBfBVcb9mozObQJI58bmvy-x2tpV_y-yM8'
URL = 'https://maps.googleapis.com/maps/api/staticmap'


def return_static_map(longitude: str, latitude: str, widthxheight: str = '851x310', zoom: str = '15') -> bytes:
    """

    :param longitude:
    :param latitude:
    :param widthxheight:
    :param zoom:
    :return:
    """
    params = {
        'key': API_KEY,
        'center': '{},{}'.format(latitude, longitude),
        'size': widthxheight,
        'zoom': zoom,
        'markers': 'color:red|label:S|{},{}'.format(latitude, longitude)
    }

    response = get(URL, params)

    return response.content


if __name__ == '__main__':
    buffer = return_static_map("-46.850293", "-23.5021638")
    print(buffer)

    with open(r'c:\caras\mapa.png', 'wb') as f:
        f.write(buffer)

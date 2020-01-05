# coding: utf-8


from requests import get

API_KEY = 'AIzaSyBfBVcb9mozObQJI58bmvy-x2tpV_y-yM8'
URL = 'https://maps.googleapis.com/maps/api/geocode/json'


def return_premise_address(longitude: str, latitude: str) -> str:
    """

    :param longitude:
    :param latitude:
    :return:
    """
    address = '** Não foi possível determinar **'
    try:
        params = {
            'key': API_KEY,
            'latlng': '{},{}'.format(latitude, longitude),
            'location_type': 'ROOFTOP',
            'result_type': 'street_address'
        }

        response = get(URL, params)

        if response.status_code == 200:
            data = response.json()

            if data['status'] == 'OK':
                address = data['results'][0]['formatted_address']
    finally:
        return address


if __name__ == '__main__':
    lon = '-46.84606891'
    lat = '-23.4967824'

    print(return_premise_address(lon, lat))

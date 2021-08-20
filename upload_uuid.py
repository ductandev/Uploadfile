#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Chương trình + up uuid xac dinh kios                                                @
#                                                                                     @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

'''	  
"id": 0,
"maNhanVien": "string",
"ngayGioChamCong": "2021-07-15T16:20:12.052Z",
"nhietDo": 0,
"idPhuongThucChamCong": 0,
"imageData": "string",
"maThietBi": "string"
'''

from csv import reader, DictWriter
from json import dumps, loads, dump

from requests import ConnectionError, HTTPError
from requests import get, post
import uuid


def post_data():
    url = 'https://api-vietthang-hr.systemkul.com/v1/'

    uuid = "f3df98bd-b430-39fd-8e1a-3b534f65a8fa"

    ID_ofMNV_recognite = "VT-011007"
    data_request = {'maNhanVien': ID_ofMNV_recognite, "maThietBi": str(uuid)}
    print(data_request)
    try:
        r = post(url + "ChamCong", data=dumps(data_request), headers={'Content-Type': 'application/json', })
        print(r.status_code)
    except ConnectionError:
        print("No internet connection available.")
        return


if __name__ == "__main__":
    post_data()



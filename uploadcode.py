import time
from csv import reader, DictWriter
from json import dumps, loads, dump

from requests import ConnectionError, HTTPError
from requests import get, post
from datetime import datetime

url = 'https://api-vietthang-hr.systemkul.com/v1/'


# {
#   "maNhanVien": "VT-011007",
#   "ngayGioChamCong": "2021-07-14T22:59:18.474Z",
#   "nhietDo": 36.6,
#   "idPhuongThucChamCong": 2,
#   "maThietBi": "a22049f1-0682-3c90-af23-dd497e2a063d"
# }

def post_data():
    print("hhht")

    with open('dataFace/recognization.csv', 'r') as read_obj:   # File đã chấm công
        csv_reader = reader(read_obj)
        for row in csv_reader:
            ID_ofMNV_recognite = "VT-011007"#row[0]                     # Mã nhân viên 
            date = "2021-07-14T22:59:18.474Z"#row[1]                    # Ngày giờ chấm công
            tempt_NV = 36.5 #row[2]                                     # Nhiệt độ của người đó 
            idptChamCong = 2                                            # Hình thức chấm công mặc định là  2
            uuid_device = "a22049f1-0682-3c90-af23-dd497e2a063d"        # UUID  của thiết bị 
            data_request = {'maNhanVien': ID_ofMNV_recognite, 'ngayGioChamCong': date, 'idPhuongThucChamCong': idptChamCong, "nhietDo": tempt_NV, "maThietBi": uuid_device}
            print(data_request)
            try:
                r = post(url + "ChamCong", timeout=10, data=dumps(data_request), headers={'Content-Type': 'application/json', })
                print(r.status_code)
            except ConnectionError:
                print("No internet connection available.")
                return
        # with open ("dataFace/recognization.csv", mode = "w") as re_csv_file: # Khởi tạo lại file lưu trữ
        #     fieldnames = ['ID', 'Date', 'Temperature']
        #     writer = DictWriter(re_csv_file, fieldnames=fieldnames)


if __name__ == "__main__":
    # timeconut = 30
    # start = datetime.now()
    # try:
    #     call_json()
    # except:
    #     print("dont't having internet")
    print("hello")
    while True:
        post_data()
        # time.sleep(5)
        # try:    
        #     now = datetime.now()
        #     if (now - start).total_seconds() > timeconut:
        #         # call_json()
        #         start = now
        # except:
        #     print("hello")
        #     pass

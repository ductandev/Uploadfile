#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Chương trình + Kiểm tra xem đủ zip chưa + unzip tất cả các file zip có được vào     @
# trong 1 thư mục + xóa zip đã giải nén + xuất file .txt danh sách mã số nhân viên    @
# đã lấy ảnh + xuất file .txt file zip thiếu và bị lỗi								  @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

from csv import reader, DictWriter
from json import dumps, loads, dump

from requests import ConnectionError, HTTPError
from requests import get, post



def post_data():
    url = 'https://api-vietthang-hr.systemkul.com/v1/' 

    with open('datacheck/dataTraning.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            id_nhanvien = row[1]                    # cột một  ID nhân viên trong file  recognization.csv
            feature = str(3)                        # Cột hai trạng thái của nhân viên đó 0,1,2 như ở trên
            data_request = [{"maNhanVien": str(id_nhanvien), "faceIdStatusEnum": int(feature)}]
            print(data_request)
            try:
                r = post(url + "NhanVien/UpdateFaceIdStatus", data=dumps(data_request), headers={'Content-Type': 'application/json', })
                print(r.status_code)
            except ConnectionError:
                print("No internet connection available.")
                return




if __name__ == "__main__":
    post_data()



#==========Xoa file=============
# for i in files:
#     if i.endswith('.zip'):
#         os.remove(path+ i)

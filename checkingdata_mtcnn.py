#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Chương trình + Kiểm tra xem đủ zip chưa + unzip tất cả các file zip có được vào     @
# trong 1 thư mục + xóa zip đã giải nén + xuất file .txt danh sách mã số nhân viên    @
# đã lấy ảnh + xuất file .txt file zip thiếu và bị lỗi								  @
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
from zipfile import ZipFile
import os
import shutil

from PIL import Image, ImageDraw
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder

from csv import reader, DictWriter
from json import dumps, loads, dump

from requests import ConnectionError, HTTPError
from requests import get, post

from model import detect_face
import tensorflow as tf
import cv2
import imutils

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

'''
#######################################################
#   0 : Chưa lấy khuôn mặt (mặc định server)
#   1 : Cần lấy lại khuôn mặt
#   2 : Đã lấy khuôn mặt
#   3 : Đã train xong, đã được nhận diện trong hệ thống
#######################################################
'''

## Sử dụng phương pháp check file và số lượng ảnh trong file.
### Tạo dictionary lưu trữ thông tin: mã nhân viên và trạng thái của nhân viên đó
dicerror = {}
### Tạo list để lưu trữ thông tin: mã nhân viên
listerror = []

### Kiểm tra có zip nào thiếu trong folder, nếu thiếu sẽ lưu vào biến "listerror" && "dicerror" sẽ báo trạng thái = 1"
def chatluong_file_zip(path):
    files = os.listdir(path)							
    files.sort()
    for filename in files:
        if  filename.endswith('.zip'):
            MNVfolder = filename.split('_')[1]           # Hàm tách chuỗi, cắt thông tin trong chuỗi string, và lấy phần tử thứ [1] trong mãng      VD: ['dev-hr.systemkul.com', '200010', '1.zip']
            if MNVfolder in listerror:
                continue
            varcheck = 0
            for i in range(1,4):
                namecheck = path + names_zip + MNVfolder + '_' + str(i)+'.zip'        
                if not os.path.exists(namecheck):
                    varcheck = 1
                    break 
            if varcheck > 0:
                listerror.append(str(MNVfolder))
                dicerror[str(MNVfolder)] = str(1)


## Giải nén tất cả các file zip ra các folder theo mã nhân viên, nếu có trong listerror sẽ ko unzip
def unzip_file(path , pathout):
    files = os.listdir(path)							
    files.sort()
    for filename in files:
        if  filename.endswith('.zip'):
            MNVfolder = filename.split('_')[1]          # Hàm tách chuỗi, cắt thông tin trong chuỗi string, và lấy phần tử thứ [1] trong mãng      VD: ['dev-hr.systemkul.com', '200010', '1.zip']
            if not MNVfolder in listerror:                          # lệnh này để phát hiện và chặn, Nếu thiếu zip của mã nhân viên đó, khỏi unzip ra
                with ZipFile(path + filename, 'r') as zipObj:		# ZipFile requires mode 'r', 'w', 'x', or 'a'
                    zipObj.extractall(pathout+ MNVfolder)           # trỏ đường dẫn ở đây, nếu không như này () nó sẽ ở thư mục hiện tại

## Kiêm tra số lượng ảnh trong folder: 
## Nếu không đạt được đủ số lượng 150 ảnh thì lưu vào biến "listerror" && "dicerror" và xóa folder đã unzip đó đi.
def number_folder(pathout):
    filesout = os.listdir(pathout)							
    filesout.sort()
    for filename in filesout:
        if len(os.listdir(pathout+filename)) != 150:                # Nếu trong folder không đủ 150 bức ảnh 
            listerror.append(str(filename))                         # lưu vào danh sách "listerror"
            dicerror[str(filename)] = str(1)                        # lưu vào danh sách "diceror" trạng thái = 1

    for fileremove in listerror:                                    # xóa folder ko đủ 150 ảnh đi
        shutil.rmtree(pathout + fileremove, ignore_errors=True)    

## Kiểm tra chất lượng ảnh và số lượng ảnh trong folder
## Sai số chất lượng của ảnh không được quá 5% (10 tấm). Vd: Quá nhiều khuôn mặt người, không có khuôn mặt.

def checking_ảnh(pathout):
    listfolder= []

    ## Một số hằng số được giữ mặc định từ facenet
    minsize = 20									# kích thước tối thiểu của khuôn mặt
    threshold = [0.2, 0.5, 0.5]						# ngưỡng của ba bước ||threshold = [0.2, 0.5, 0.5]với ngưỡng này phát hiện được 99%-100% khuôn mặt trong 1 bức ảnh, 
    factor = 0.709 #709								# scale factor : hệ số tỉ lệ

    sess = tf.Session()
    pnet, rnet, onet = detect_face.create_mtcnn(sess, 'model')         # read pnet, rnet, onet models from align directory and files are det1.npy, det2.npy, det3.npy

    for class_dir in os.listdir(pathout):
        # print( os.path.join(pathout, class_dir))                     # Hàm dùng để nối đường dẫn trong python
        # print( os.path.isdir())                                      # kiểm tra đường dẫn có trỏ tới một thư mục hay không => trả về TRUE hoặc FALL
        if not os.path.isdir(os.path.join(pathout, class_dir)):        # giải thích ở 2 dòng trên, nếu đường dẫn ko trỏ đến thư mục => trả về FALL => continue(thoát vòng lặp)                         
                continue                                               # Thoát vòng lặp
        count = 0
        for img_path in image_files_in_folder(os.path.join(pathout, class_dir)):        # vòng lặp chạy 150 bức ảnh mỗi thư mục Mã nhân viên
            try:                                                                        # trường hợp phát hiện khuôn mặt nếu chỉ 1 khuôn mặt quay lại vòng lặp kiểm tra ảnh tiếp theo, nếu khác 1 ==> count+=1
                #======= Detect face MTCNN =============================
                img = cv2.imread(img_path)						        # Đọc hình ảnh
                h,w = img.shape[:2]								        # Hàm shape:đọc thuộc tính ảnh, in ra gia tri buc anh tuong ung voi [cao,rong,kenhmau]), ở đây chỉ lấy 2 giá trị w,h
                if h > 800:
                    img = imutils.resize(img,height=800)
                if w > 800:
                    img = imutils.resize(img, width=800)

                #----face detection:
                bounding_boxes, _ = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)

                if bounding_boxes[0][4] < 0.95:
                    count +=1
                    print("anh loi-----------",img_path)
                    continue

                if len(bounding_boxes) != 1:                                             # 2 khuôn mặt trở lên
                    if bounding_boxes[0][4] > 0.95 and bounding_boxes[1][4] > 0.95:      # trường hợp xử lý bounding_boxes tùm bậy và nếu phát hiện ra 2 người có độ chính xác >0.95
                        count +=1
                        print("anh chua 2 khuon mat: ",img_path)
                        continue

                #======== Phát Hiện ảnh mờ + ảnh Đen ====================
                # Dinh nghia blur threshold
                blur_threshold = 110
                # Doc anh tu file
                image = cv2.imread(img_path)
                gray  = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
                # Tinh toan muc do focus cua anh
                focus_measure = cv2.Laplacian(gray, cv2.CV_64F).var()

                if focus_measure < blur_threshold:
                    count+=1
                    print("anh mo: ",img_path)                        

            except:                                                                     # trường hợp ko có face ==> count+=1
                count +=1
                print("anh den: ",img_path) 

        print("Folder {} : {}".format(class_dir, count))                                # class_dir: Mã nhân viên || count: Số ảnh lỗi
        calfeature = count/len(os.listdir(pathout+ class_dir))*100                      # Cách tính: số ảnh không đúng của 1 nhân viên / tổng số ảnh của nhân viên đó.
        if (100.0 - calfeature)< 95.0:                                                  # Nếu chất lượng ảnh  không được đạt được 95% thì báo không chất lượng
            listerror.append(str(class_dir))
            listfolder.append(str(class_dir))                                           # thêm vào "listfolder" thư mục ảnh bị lỗi
            dicerror[str(class_dir)] = str(1)
        else:
            # Chất lượng okie
            listerror.append(str(class_dir))
            dicerror[str(class_dir)] = str(2)
    # for removefoler in  listfolder:                                                     # xóa folder trong "listfolder" ko đạt chất lượng ảnh đi
    #     shutil.rmtree(pathout + removefoler, ignore_errors=True)                        # lệnh xóa cây thư mục
        
## Tổng hợp danh sách các nhân viên, đánh trạng thái được hay không (1 hoặc 2) và lưu vào file .csv
def tonghop_file():
    for i in listerror:                                                                     
        with open ("datacheck/recognization.csv", mode = "+a") as re_csv_file:          # Danh sách file lưu trử  chuẩn bị upload file
            fieldnames = ['ID', 'Feature']
            writer = DictWriter(re_csv_file, fieldnames=fieldnames)
            writer.writerow({'ID': str(i), 'Feature': dicerror[str(i)]})
        with open ("datacheck/recognization_backup.csv", mode = "+a") as re_csv_file:   # Danh sách backup lưu trữ khi có sự cố
            fieldnames = ['ID', 'Feature']
            writer = DictWriter(re_csv_file, fieldnames=fieldnames)
            writer.writerow({'ID': str(i), 'Feature': dicerror[str(i)]})

## post data lên cloud sever
def post_data():
    url = 'https://api-vietthang-hr.systemkul.com/v1/'                                  ############

    with open('datacheck/recognization.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            id_nhanvien = row[0]                                                        # cột thứ nhất ID nhân viên trong file recognization.csv
            feature = row[1]                                                            # Cột thứ hai trạng thái của nhân viên đó 0,1,2 như đặt ra ở trên đầu
            data_request = [{"maNhanVien": str(id_nhanvien), "faceIdStatusEnum": int(feature)}]
            print(data_request)
            try:
                r = post(url + "NhanVien/UpdateFaceIdStatus", data=dumps(data_request), headers={'Content-Type': 'application/json', })
                print(r.status_code)                                                    # 500: ko có mã nhân viên || 201 : up lên thành công
            except ConnectionError:
                print("No internet connection available.")
                return
        with open ("datacheck/recognization.csv", mode = "w") as re_csv_file:           # sau khi upload lên cloud xóa hết data cũ trong file recognization.csv
            fieldnames = ['ID', 'Feature']
            writer = DictWriter(re_csv_file, fieldnames=fieldnames)



if __name__ == "__main__":
    path = './test/store/'									                            # đường dẫn fonder lưu trữ file zip tải về

    pathout = './data/Vietthang/'                                                       # đường dẫn folder lưu trữ sau unzip
    
    names_zip = 'vietthang.systemkul.com_'			                                    # định dạng tên file zip    ######
    

    # os.system("sudo rm -r test/store/")                                                 # xóa folder store lưu trữ file zip cu~ di                        
    # os.system("sudo scp -r -i /home/tan/friday opc@168.138.208.83:/home/opc/store /home/tan/Uploadfile/test")     # tải về folder store

    if not os.path.isdir(pathout):                                                      # Kiểm trong folder có folder mong muốn chưa
        os.mkdir(pathout)

    # Chất lượng của file  .zip kiểm tra xem có thiếu file zip hay không ?
    # chatluong_file_zip(path)
    # # Giải nén file zip:
    # unzip_file(path, pathout)
    # # Số ảnh trong folder và xoá folder bị lỗi trước khí  chạy training:
    # number_folder(pathout)
    # Kiểm tra chất lượng của ảnh:
    checking_ảnh(pathout)
    # Tổng hợp thành file các dữ liệu  đã được tính toán.
    tonghop_file()
    # Upload thông tin lên hệ thống:
    print(listerror)
    print(dicerror)
    
    #post_data()


#==========Xoa tat ca file zip=============
#os.system("sudo rm -r test/store/")
#==========================================

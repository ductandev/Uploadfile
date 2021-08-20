import csv

with open("recognization.csv", mode = "w") as re_csv_file:           # sau khi upload lên cloud xóa hết data cũ trong file recognization.csv
    fieldnames = ['ID', 'Feature']
    writer = csv.DictWriter(re_csv_file, fieldnames=fieldnames)

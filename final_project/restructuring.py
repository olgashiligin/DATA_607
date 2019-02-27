import os

from utils import OlgasLibs
import csv
import re

# generate input csv file's path from company's name
def get_input_path(file_name):
    return "./data/" + file_name + ".csv"

# generate output csv file's path from company's name
def get_output_path(file_name):
    return "./data/" + file_name + "-results.csv"


# read csv file with a company's patents data
def readCsv(path2read_file, path2write_file):
    with open(path2read_file) as csvfile:
        row_values = csv.reader(csvfile, delimiter=',')
        rows = list(row_values)[1:]
        count = 0
        for row in rows:
            try:
                patent = row[0]
                date = row[1]
                year = row[2]
                inventors = row[3]
                us_class_list = row[4]
                # extra effort, because I opened file in excel and it corrupted some data
                if us_class_list == "01-Jan":
                    us_class_list = "1/1"
                assignee = row[5]
                title = row[6]
                link = row[7]
                us_classes = us_class_list.split(";")
                data = []
                for us_class in us_classes:
                    try:
                        classes = us_class.split("/")
                        us_class_left = classes[0]
                        us_class_right = classes[1]
                        data.append({"patent_number":patent,"date":date,"year":year,"us_cat":us_class_left,"us_subcat":us_class_right,"title":title})
                    except Exception as e:
                        print("Exception: " + str(e))
                        print("Cannot read us_class: " + us_class)
                        print("appending to errors file... ")
                        invalid = AssigneeData(patent, date, year, inventors, us_class, "", assignee,title, link)
                        path = path2read_file[:-4]+"-invalid_us_classes.csv"
                        # append info about failed record to dedicated csv file
                        OlgasLibs.append_objects_to_csv_file(path, [invalid])
                        print("Continue... ")
                        continue
                # append clensed data to csv file
                OlgasLibs.append_to_csv_file(path2write_file, data)
                count = count + 1
            except Exception as e:
                print("Exception: " + str(e))
                print("Count: " + str(count))

# read files from data directory. All files expected to be named as company
# name plus extension, e.g. facebook.csv, google.csv etc
input_files_names_list = os.listdir("./data")
for file_name in input_files_names_list:
        readCsv("./data/"+file_name, "./data/processed/"+file_name)

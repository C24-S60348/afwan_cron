#apps/utils/csv_helper.py
import csv

def af_getcsv(csvloc="tanam.csv"):
    result = []
    with open(csvloc, newline='', encoding='utf-8-sig') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            result.append(row)
    return result
    # result = af_getcsv("tanam.csv")
    #
    # for r in result:
    #     html += "<li>" + r[0] + "</li>"

def af_getcsvdict(csvloc="tanam.csv"):
    try:
        result = []
        with open(csvloc, newline='', encoding='utf-8-sig') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                result.append(row)
        return result
    except Exception as e:
        return ""
    # result = af_getcsvdict("tanam.csv")
    #
    # for r in result:
    #     html += "<li>" + r["id"] + "</li>"

def af_addcsv(file_path="tanam.csv", new_row=["ikan","ayam"]):
    # Open the CSV file in append mode
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the new row to the file
        writer.writerow(new_row)
    # file_path = 'tanam.csv'
    # new_row = [
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     af_requestpost("tanamtext"),
    #     ]
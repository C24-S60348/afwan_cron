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
        writer.writerow(new_row)

def af_replacecsv(file_path, username, new_data):
    try:
        # Read all rows into a list
        rows = af_getcsvdict(file_path)
        
        # Modify the row with the matching username
        modified = False
        for row in rows:
            if row['username'] == username:  # Assuming 'username' is a column
                for key in new_data:
                    row[key] = new_data[key]
                modified = True
                break
        
        # If a row was modified, write all rows back to the CSV
        if modified:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return True
        return False
    except Exception as e:
        print(f"Error replacing CSV row: {e}")
        return False
    
def af_replacecsv_withtoken(file_path, token, new_data):
    try:
        # Read all rows into a list
        rows = af_getcsvdict(file_path)
        
        # Modify the row with the matching token
        modified = False
        for row in rows:
            if row['token'] == token:  # Assuming 'token' is a column
                for key in new_data:
                    row[key] = new_data[key]
                modified = True
                break
        
        # If a row was modified, write all rows back to the CSV
        if modified:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return True
        return False
    except Exception as e:
        print(f"Error replacing CSV row: {e}")
        return False
from flask import Blueprint, request, jsonify, render_template, render_template_string, send_file
import pandas as pd, requests, json, variables, os, time, asyncio, aiomysql
from contextlib import asynccontextmanager

pelajar_data_bp = Blueprint('pelajar_data_bp', __name__)

@pelajar_data_bp.route("/pelajar_data")
def pelajar_data():
    
    
    export_pelajar_data()
    export_pelajar_data_2()

    template = """
        <!DOCTYPE html>
        <html>
        <head><title>Pelajar Data</title></head>
        <body>
            <div>
                Download pelajar data <a href='/pelajar_data_download'>Here pelajar_data_2.xlsx</a>
            </div>
        </body>
        </html>
    """
    return render_template_string(template)

def export_pelajar_data():
    def execute_query(query):
        """
        Sends a POST request to afwanproductions.pythonanywhere.com/api/executejsonv2
        with the given query as JSON payload.
        Returns the JSON response.
        """
        url = "https://afwanproductions.pythonanywhere.com/api/executejsonv2"
        payload = {"query": query, "password": variables.website_pass}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            return None

    def flatten_semester_data(semdata, sem_label, no_matric, sem_num, extra_fields=None):
        """
        Flattens the semester data JSON into a row for the DataFrame.
        Adds semester label, number, and no_matric.
        Optionally adds extra fields from the user row.
        """
        row = {}
        if isinstance(semdata, dict):
            row.update(semdata)
        else:
            # If semdata is a list or other, skip
            return None
        row["Semester"] = sem_label
        row["SemesterNum"] = sem_num
        row["No_Matric"] = no_matric
        if extra_fields:
            row.update(extra_fields)
        return row

    def extract_and_save_to_excel():
        # Query the data
        result = execute_query("SELECT no_matric, sem1, sem1data, sem2, sem2data, sem3, sem3data FROM pointer_calculator_user;")
        if not result or "results" not in result:
            print("No data found or error in response.")
            return

        rows = []
        for row in result["results"]:
            no_matric = row.get("no_matric", "")
            # Optionally, add more user-level fields here if needed
            for idx, (sem_key, sem_label) in enumerate([("sem1data", "Sem 1"), ("sem2data", "Sem 2"), ("sem3data", "Sem 3")], start=1):
                semdata = row.get(sem_key)
                if semdata:
                    try:
                        data = json.loads(semdata)
                        # If the semester data is a list (e.g. list of subjects), flatten each
                        if isinstance(data, list):
                            for item in data:
                                flat = flatten_semester_data(item, sem_label, no_matric, idx)
                                if flat:
                                    rows.append(flat)
                        elif isinstance(data, dict):
                            flat = flatten_semester_data(data, sem_label, no_matric, idx)
                            if flat:
                                rows.append(flat)
                        else:
                            print(f"Unexpected data type in {sem_key}: {type(data)}")
                    except Exception as e:
                        print(f"Error parsing {sem_key}: {e}")

        if not rows:
            print("No valid semester data found.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(rows)

        # Try to order columns: No_Matric, Semester, SemesterNum, then the rest
        cols = df.columns.tolist()
        order = [c for c in ["No_Matric", "Semester", "SemesterNum"] if c in cols]
        rest = [c for c in cols if c not in order]
        df = df[order + rest]

        # Save to Excel
        output_file = "pelajar_data.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Data saved to {output_file}")
    
    extract_and_save_to_excel()
    

def export_pelajar_data_2():
    df = pd.read_excel('pelajar_data.xlsx')

    # Define a function to extract Steel-related names and grades
    def extract_steel_data(row):
        # Split FlangeName and FlangeGred columns
        names = row['PrintNamaKursuss'].split(',')
        grades = row['PrintGreds'].split(',')
        
        # Prepare lists to hold Steel-related data
        steel_names = []
        steel_grades = []
        
        # Iterate through names and corresponding grades
        for name, grade in zip(names, grades):
            if name == "Science In Life I":
                name = "Science in Life I"
            elif name == "Science In Life II":
                name = "Science in Life II"
            elif name == "Science In Life III":
                name = "Science in Life III"
                
            steel_names.append(name)
            steel_grades.append(grade)
        
        return pd.Series({
            'NoMatric': row['No_Matric'],
            'Semester': row['Semester'],
            'Name': row['NamaPelajar'],
            'Mentor': row['Mentor'],
            'PNG': row['PrintPNGs'],
            steel_names[0] : steel_grades[0],
            steel_names[1] : steel_grades[1],
            steel_names[2] : steel_grades[2],
            steel_names[3] : steel_grades[3],
            steel_names[4] : steel_grades[4],
            steel_names[5] : steel_grades[5]
        })

    # Apply function and create new DataFrame
    steel_data_df = df.apply(extract_steel_data, axis=1)

    #ReOrder
    # columns = ['NoMatric', 'Semester', 'Name', 'Mentor', 'PNG'] + [col for col in steel_data_df.columns if col not in ['NoMatric', 'Semester', 'Name', 'Mentor', 'PNG']]
    columns = ['NoMatric', 'Semester', 'Name', 'Mentor', 'PNG', 
            'Biologi I', 'Fizik I', 'Kimia I', 'Matematik I', 'Science in Life I', 'English for Special Purposes', 'Kokurikulum',
            'Biologi II', 'Fizik II', 'Kimia II', 'Matematik II', 'Science in Life II', 'Pengenalan Kepada Pengaturcaraan', 'English for Communication',
            'Pengenalan Kepada Kejuruteraan & Teknologi', 'Sains Bumi', 'Keperibadian Ulul Albab'
            ] 
    steel_data_df = steel_data_df[columns]


    steel_data_df.to_excel('pelajar_data_2.xlsx', index=False)
    print("Data exported to 'pelajar_data_2.xlsx'.")

    # Display the resulting DataFrame
    print(steel_data_df)

@pelajar_data_bp.route("/pelajar_data_download")
def pelajar_data_download():
    return send_file("pelajar_data_2.xlsx", as_attachment=True, download_name="pelajar_data_2.xlsx")

#utils/mdb_helper.py
#for Microsoft access
import os
import pyodbc

def af_connectmdb(dbloc=""):
    if not os.path.isfile(dbloc):
        raise FileNotFoundError(f"The database file at '{dbloc}' does not exist.")
    
    conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={dbloc};'
    conn = pyodbc.connect(conn_str)
    return conn

def af_getmdb(dbloc="static/db/habit/mydb.accdb", query="SELECT * FROM users;", params=()):
    conn = af_connectmdb(dbloc)
    cursor = conn.cursor()
    if params == "":
        params = ()
    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            dbdata = cursor.fetchall()
            results = [dict(zip([column[0] for column in cursor.description], row)) for row in dbdata] if dbdata else []
            # print (results)
            return results
        else:
            conn.commit()  # Only required for non-SELECT queries
            return "Query executed successfully"
    except pyodbc.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def af_gettablemdb(dbloc="static/db/habit/mydb.accdb"):
    try:
        conn = af_connectmdb(dbloc)
        cursor = conn.cursor()

        table_metadata = cursor.tables() 
        
        table_names = []
        
        for table_info in table_metadata:
            if table_info[3] == 'TABLE': 
                table_names.append(table_info[2])
                
        # print("Database Tables Found:")
        # print(table_names)
        return table_names
        
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # print(f"Database Error occurred: {sqlstate} - {ex}")
        return ex

# Example usage
# try:
#     db_results = af_getmdb("path/to/your/database.accdb", "SELECT * FROM users WHERE name=?;", params=("ikan",))
#     print(db_results)
# except FileNotFoundError as e:
#     print(e)
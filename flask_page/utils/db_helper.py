#utils/db_helper.py
import os
from flask import jsonify
import sqlite3
from flask import Flask, g

"""
Example:

dbloc = "static/db/habit/mydb.db"

query - "SELECT * FROM habit where deleted_at IS NULL;"
params - ()

query - "INSERT INTO habit (name, value, created_at) VALUES (?, ?, ?)"
params - ("ayam","ikan", datetime.now())

query = "UPDATE habit SET username = ? WHERE id = ?"
params = ("ayam", 4)

query = "UPDATE habit SET deleted_at = ? WHERE id = ?"
params = (datetime.now(),)


query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
params = ()



"""

def af_connectdb(dbloc=""):
    if not os.path.isfile(dbloc):
        raise FileNotFoundError(f"The database file at '{dbloc}' does not exist.")
    
    conn = sqlite3.connect(dbloc)
    conn.row_factory = sqlite3.Row  # Optional: Returns results as dictionaries
    return conn

def af_getdb(dbloc="static/db/habit/mydb.db", query="SELECT * FROM users;", params=("ikan",)):
    conn = af_connectdb(dbloc)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("PRAGMA"):
            dbdata = cursor.fetchall()
            results = [dict(row) for row in dbdata] if dbdata else []
            return results
        else:
            conn.commit()  # Commit only if it's not a SELECT query
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except sqlite3.Error as e:
        #todo - telegram message here?
        return f"An error occurred: {e.args[0]}"
    finally:
        conn.close()

def convert_to_json(dbdata):
    if dbdata:
        # Create a list of dictionaries from the rows
        results = [dict(row) for row in dbdata]
        return jsonify(results)  # Directly use jsonify for proper JSON response in Flask
    else:
        return jsonify([])  # Return an empty list as JSON
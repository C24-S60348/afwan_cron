from flask import Blueprint, request, jsonify
from flask_page.connect_to_db import connect_to_db
import variables
import aiomysql

executejsonv2_bp = Blueprint('executejsonv2_bp', __name__)

# QUERY EXECUTER JSON V2
@executejsonv2_bp.route('/api/executejsonv2', methods=['GET', 'POST'])
async def execute_query_json_v2():
    try:
        # Synchronously read JSON data
        data = request.get_json()

        if 'query' not in data:
            return jsonify({"error": "query parameter is required"}), 400

        if 'password' not in data:
            return jsonify({"error": "password parameter is required"}), 400

        sql = data['query']
        password = data['password']

        if password == variables.website_pass:
            try:
                async with connect_to_db() as (cursor, connection):
                    # Execute the SQL query asynchronously
                    await cursor.execute(sql)

                    # Check if the query returns rows (SELECT query)
                    if sql.strip().lower().startswith("select"):
                        columns = [column[0] for column in cursor.description]
                        rows = await cursor.fetchall()  # Fetch all rows asynchronously
                        results = [dict(zip(columns, row)) for row in rows]
                        return jsonify({"results": results}), 200
                    else:
                        # Commit for insert, update, delete
                        await connection.commit()
                        return jsonify({"message": "Query executed successfully"}), 200
            except aiomysql.MySQLError as db_err:
                return jsonify({"error": f"Database error: {db_err}"}), 500
        else:
            return jsonify({"error": "Incorrect password"}), 401
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500



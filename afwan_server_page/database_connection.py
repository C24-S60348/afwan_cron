from quart import Blueprint, jsonify, request, Response
import asyncpg
import variables
from functools import wraps
from afwan_server_page.handle_exceptions import handle_exceptions

database_connection_bp = Blueprint("database_connection_bp", __name__)

# DB ==================================
DB_CONFIG = {
    "user": variables.db_user,
    "password": variables.db_pass,
    "database": variables.db_name,
    "host": variables.db_host,
    "port": variables.db_port,
}

@handle_exceptions("database-connection", type="raise")
async def get_connection():
    return await asyncpg.connect(**DB_CONFIG)



@database_connection_bp.route("/")
@handle_exceptions("db-test")
async def db_test():
    conn = await get_connection()
    result = await conn.fetchval("SELECT NOW()")
    await conn.close()
    return {"db_time": str(result)}
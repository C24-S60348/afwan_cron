
import asyncio
import aiomysql
from contextlib import asynccontextmanager

# Async context manager for MySQL connection
@asynccontextmanager
def connect_to_db():
    connection = aiomysql.connect(
        host="AfwanProductions.mysql.pythonanywhere-services.com",
        user="AfwanProductions",
        password="afwan987",
        db="AfwanProductions$afwan_db",
        loop=asyncio.get_event_loop()
    )
    try:
        with connection.cursor() as cursor:
            yield cursor, connection
    except aiomysql.MySQLError as err:
        print(f"Error connecting to database: {err}")
        raise
    finally:
        connection.close()
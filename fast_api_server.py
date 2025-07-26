#sudo nano /etc/systemd/system/quartapp.service

#edit then
#sudo systemctl daemon-reload
#sudo systemctl restart quartapp
#sudo systemctl status quartapp
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response, HTMLResponse
import requests
import asyncpg
import os
import datetime
import json
import variables
import traceback
import httpx  # async HTTP client
from functools import wraps
from pydantic import BaseModel
import secrets
import hashlib

class ModelResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class LoginRequest(BaseModel):
    type: str = "LOGIN"
    username: str
    password: str

class RegisterRequest(BaseModel):
    type: str = "REGISTER"
    username: str
    password: str

class DataRequest(BaseModel):
    type: str = "DATA"
    appname: str
    token: str

class UserData(BaseModel):
    calendar_tick: dict = {}
    habits: list = []
    notes: list = []

app = FastAPI(root_path="/api")

# Error handler ==================================
async def send_telegram_error(error_message):
    try:
        bot_token = variables.tb_token_server
        chat_id = "-4885373674"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🚨 ERROR ALERT 🚨\n\n{error_message}",
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)

        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# Universal exception handler ====================
def handle_exceptions(route_name="Unknown", type="exception"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error in {route_name}:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                await send_telegram_error(error_msg)
                
                if type == "raise":
                    raise  # Re-raise the exception
                else:
                    raise HTTPException(status_code=500, detail="Internal server error")
        return wrapper
    return decorator

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

# Authentication helper functions ====================
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

async def verify_token(token: str) -> int:
    """Verify token and return user_id if valid"""
    conn = await get_connection()
    try:
        user_id = await conn.fetchval(
            "SELECT id FROM users WHERE token = $1 AND token_expires_at > NOW()",
            token
        )
        return user_id
    finally:
        await conn.close()

# Database initialization ====================
async def init_database():
    """Initialize database tables"""
    conn = await get_connection()
    try:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                token VARCHAR(255),
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create user_data table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                appname VARCHAR(100) NOT NULL,
                calendar_tick JSONB DEFAULT '{}',
                habits JSONB DEFAULT '[]',
                notes JSONB DEFAULT '[]',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(user_id, appname)
            )
        """)
        
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        await conn.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()

@app.get(
    "/",
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"message": "Hello from FastAPI + Webdock!"}}}},
    }
)
async def home():
    return {"message": "Hello from FastAPI + Webdock!"}

@app.get(
    "/db-test",
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"db_time": "2025-07-07 21:21:52.703991+00:00"}}}},
        # 500: {"description": "Internal Server Error", "model": ErrorResponse, "content": {"application/json": {"example": {"detail": "Internal server error"}}}},
        # 400: {"description": "Bad Request", "model": ErrorResponse, "content": {"application/json": {"example": {"detail": "Bad request"}}}},
    }
)
@handle_exceptions("db-test")
async def db_test():
    conn = await get_connection()
    result = await conn.fetchval("SELECT NOW()")
    await conn.close()
    return {"db_time": str(result)}

# Authentication and Data Management Routes ====================
@app.post(
    "/app",
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"token": "abc123...", "message": "Login successful"}}}},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse},
    }
)
@handle_exceptions("app-auth")
async def app_endpoint(request: Request):
    """Handle LOGIN, REGISTER, and DATA requests"""
    try:
        body = await request.json()
        request_type = body.get("type", "").upper()
        
        if request_type == "LOGIN":
            return await handle_login(body)
        elif request_type == "REGISTER":
            return await handle_register(body)
        elif request_type == "DATA":
            return await handle_data(body)
        else:
            raise HTTPException(status_code=400, detail="Invalid request type")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

async def handle_login(body: dict):
    """Handle user login"""
    username = body.get("username")
    password = body.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    conn = await get_connection()
    try:
        # Check if user exists and password matches
        user = await conn.fetchrow(
            "SELECT id, password FROM users WHERE username = $1",
            username
        )
        
        if not user or user['password'] != hash_password(password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Generate new token
        token = generate_token()
        token_expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        
        # Update user token
        await conn.execute(
            "UPDATE users SET token = $1, token_expires_at = $2 WHERE id = $3",
            token, token_expires_at, user['id']
        )
        
        return {"token": token, "message": "Login successful"}
    finally:
        await conn.close()

async def handle_register(body: dict):
    """Handle user registration"""
    username = body.get("username")
    password = body.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    conn = await get_connection()
    try:
        # Check if username already exists
        existing_user = await conn.fetchval(
            "SELECT id FROM users WHERE username = $1",
            username
        )
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Generate token
        token = generate_token()
        token_expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        
        # Create new user
        user_id = await conn.fetchval(
            "INSERT INTO users (username, password, token, token_expires_at) VALUES ($1, $2, $3, $4) RETURNING id",
            username, hash_password(password), token, token_expires_at
        )
        
        return {"token": token, "message": "Registration successful", "user_id": user_id}
    finally:
        await conn.close()

async def handle_data(body: dict):
    """Handle data requests (GET and POST)"""
    appname = body.get("appname")
    token = body.get("token")
    method = body.get("method", "GET")  # GET or POST
    
    if not appname or not token:
        raise HTTPException(status_code=400, detail="Appname and token required")
    
    # Verify token
    user_id = await verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    conn = await get_connection()
    try:
        if method.upper() == "GET":
            # Get user data
            data = await conn.fetchrow(
                "SELECT calendar_tick, habits, notes FROM user_data WHERE user_id = $1 AND appname = $2",
                user_id, appname
            )
            
            if not data:
                # Return empty data if no record exists
                return {
                    "calendar_tick": {},
                    "habits": [],
                    "notes": []
                }
            
            return {
                "calendar_tick": data['calendar_tick'],
                "habits": data['habits'],
                "notes": data['notes']
            }
        
        elif method.upper() == "POST":
            # Update user data
            calendar_tick = body.get("calendar_tick", {})
            habits = body.get("habits", [])
            notes = body.get("notes", [])
            
            # Upsert data
            await conn.execute("""
                INSERT INTO user_data (user_id, appname, calendar_tick, habits, notes, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (user_id, appname)
                DO UPDATE SET
                    calendar_tick = $3,
                    habits = $4,
                    notes = $5,
                    updated_at = NOW()
            """, user_id, appname, calendar_tick, habits, notes)
            
            return {"message": "Data updated successfully"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid method. Use GET or POST")
    finally:
        await conn.close()

# Alternative GET endpoint for data retrieval ====================
@app.get("/app")
@handle_exceptions("app-get")
async def get_app_data(type: str = None, appname: str = None, token: str = None):
    """GET endpoint for retrieving data"""
    if type != "DATA" or not appname or not token:
        raise HTTPException(status_code=400, detail="Invalid parameters. Use type=DATA&appname=<appname>&token=<token>")
    
    # Verify token
    user_id = await verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    conn = await get_connection()
    try:
        data = await conn.fetchrow(
            "SELECT calendar_tick, habits, notes FROM user_data WHERE user_id = $1 AND appname = $2",
            user_id, appname
        )
        
        if not data:
            return {
                "calendar_tick": {},
                "habits": [],
                "notes": []
            }
        
        return {
            "calendar_tick": data['calendar_tick'],
            "habits": data['habits'],
            "notes": data['notes']
        }
    finally:
        await conn.close()

#======================ABAIKAN======================
#saje -----
@app.get(
    "/sara",
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"dari afwan": "HAI SARAAAA SAYANGGGGGSS"}}}},
    }
)
@handle_exceptions("sara")
async def sara():
    return {"dari afwan":"HAI SARAAAA SAYANGGGGGSS"}

@app.get(
    "/afwan",
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"dari sara": "HAI AFWAN"}}}},
    }
)
@handle_exceptions("afwan")
async def afwan():
    return {"dari sara":"HAI AFWAN"}

#proxy -----
@app.api_route(
    '/proxy',
    methods=["GET"],
    summary="Proxy a GET request to another URL",
    description="Parameter: url --- Fetches and returns the raw response of the given `url`. CORS headers are included. Returns the page content as-is.",
    response_class=HTMLResponse,
    responses={
        200: {
            "description": "HTML content from target URL",
            "content": {
                "text/html": {
                    "example": "<!DOCTYPE html><html><head><title>Example</title></head><body>Sample content</body></html>"
                }
            }
        },
        400: {"description": "Missing or invalid 'url' parameter"},
        500: {"description": "Error fetching from target URL"},
    }
)
@handle_exceptions("proxy")
async def proxy(request: Request):
    target_url = request.query_params.get('url')

    if not target_url:
        raise HTTPException(status_code=400, detail="Missing 'url' parameter")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(target_url, headers=headers)

    # Create a response with CORS headers
    proxy_response = Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/octet-stream")
    )
    proxy_response.headers["Access-Control-Allow-Origin"] = "*"
    proxy_response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    proxy_response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    return proxy_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

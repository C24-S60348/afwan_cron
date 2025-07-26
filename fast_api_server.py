#sudo nano /etc/systemd/system/quartapp.service

#edit then
"""
To Restart server:

sudo systemctl daemon-reload
sudo systemctl restart fastapi
sudo systemctl status fastapi
sudo systemctl enable fastapi

"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response, HTMLResponse, JSONResponse
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
        chat_id = "-1002864663247"

        if not bot_token:
            print("ERROR: Bot token is empty or None")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🚨 ERROR ALERT 🚨\n\n{error_message}",
            "parse_mode": "HTML"
        }

        print(f"Attempting to send Telegram message to {chat_id}")
        print(f"URL: {url}")
        print(f"Data: {data}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)

        print(f"Telegram API response status: {response.status_code}")
        print(f"Telegram API response: {response.text}")

        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
            return False
        else:
            print("Telegram message sent successfully")
            return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

# Universal exception handler ====================
def handle_exceptions(route_name="Unknown", type="exception"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPException as-is (don't catch it)
                raise
            except Exception as e:
                error_msg = f"Error in {route_name}:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                await send_telegram_error(error_msg)
                
                if type == "raise":
                    raise  # Re-raise the exception
                else:
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Internal server error", "message": error_msg}
                    )
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
        # Update last_used_at and get user_id
        user_id = await conn.fetchval("""
            UPDATE user_sessions 
            SET last_used_at = NOW() 
            WHERE token = $1 AND expires_at > NOW() AND is_active = TRUE
            RETURNING user_id
        """, token)
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
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create user_sessions table for multiple device tokens
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                device_info JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW(),
                last_used_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
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
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request type", "message": "Request type must be LOGIN, REGISTER, or DATA"}
            )
    except json.JSONDecodeError as e:
        error_msg = f"JSON decode error in app endpoint: {str(e)}"
        await send_telegram_error(error_msg)
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON body", "message": error_msg}
        )
    except Exception as e:
        error_msg = f"Unexpected error in app endpoint: {str(e)}"
        await send_telegram_error(error_msg)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": error_msg}
        )

async def handle_login(body: dict):
    """Handle user login"""
    username = body.get("username")
    password = body.get("password")
    device_info = body.get("device_info", {})  # Optional device information
    
    if not username or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing credentials", "message": "Username and password required"}
        )
    
    conn = await get_connection()
    try:
        # Check if user exists and password matches
        user = await conn.fetchrow(
            "SELECT id, password FROM users WHERE username = $1",
            username
        )
        
        if not user or user['password'] != hash_password(password):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication failed", "message": "Invalid username or password"}
            )
        
        # Generate new token
        token = generate_token()
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        
        # Create new session
        await conn.execute("""
            INSERT INTO user_sessions (user_id, token, device_info, expires_at)
            VALUES ($1, $2, $3, $4)
        """, user['id'], token, device_info, expires_at)
        
        return {
            "token": token, 
            "message": "Login successful",
            "expires_at": expires_at.isoformat(),
            "device_info": device_info
        }
    finally:
        await conn.close()

async def handle_register(body: dict):
    """Handle user registration"""
    username = body.get("username")
    password = body.get("password")
    device_info = body.get("device_info", {})  # Optional device information
    
    if not username or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing credentials", "message": "Username and password required"}
        )
    
    if len(password) < 6:
        return JSONResponse(
            status_code=400,
            content={"error": "Password too short", "message": "Password must be at least 6 characters"}
        )
    
    conn = await get_connection()
    try:
        # Check if username already exists
        existing_user = await conn.fetchval(
            "SELECT id FROM users WHERE username = $1",
            username
        )
        
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"error": "User exists", "message": "Username already exists"}
            )
        
        # Create new user
        user_id = await conn.fetchval(
            "INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id",
            username, hash_password(password)
        )
        
        # Generate token and create session
        token = generate_token()
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        
        await conn.execute("""
            INSERT INTO user_sessions (user_id, token, device_info, expires_at)
            VALUES ($1, $2, $3, $4)
        """, user_id, token, device_info, expires_at)
        
        return {
            "token": token, 
            "message": "Registration successful", 
            "user_id": user_id,
            "expires_at": expires_at.isoformat(),
            "device_info": device_info
        }
    finally:
        await conn.close()

async def handle_data(body: dict):
    """Handle data requests (GET and POST)"""
    appname = body.get("appname")
    token = body.get("token")
    method = body.get("method", "GET")  # GET or POST
    
    if not appname or not token:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing parameters", "message": "Appname and token required"}
        )
    
    # Verify token
    user_id = await verify_token(token)
    if not user_id:
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed", "message": "Invalid or expired token"}
        )
    
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
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid method", "message": "Invalid method. Use GET or POST"}
            )
    finally:
        await conn.close()

# Session Management Endpoints ====================
@app.post("/logout")
@handle_exceptions("logout")
async def logout(request: Request):
    """Logout from current session"""
    try:
        body = await request.json()
        token = body.get("token")
        
        if not token:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing token", "message": "Token is required"}
            )
        
        conn = await get_connection()
        try:
            # Deactivate the session
            result = await conn.execute(
                "UPDATE user_sessions SET is_active = FALSE WHERE token = $1",
                token
            )
            
            if result == "UPDATE 0":
                return JSONResponse(
                    status_code=404,
                    content={"error": "Session not found", "message": "Invalid or expired token"}
                )
            
            return {"message": "Logout successful"}
        finally:
            await conn.close()
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON", "message": "Invalid JSON body"}
        )

@app.get("/sessions")
@handle_exceptions("get-sessions")
async def get_sessions(token: str):
    """Get all active sessions for the user"""
    if not token:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing token", "message": "Token is required"}
        )
    
    # Verify token and get user_id
    user_id = await verify_token(token)
    if not user_id:
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed", "message": "Invalid or expired token"}
        )
    
    conn = await get_connection()
    try:
        sessions = await conn.fetch("""
            SELECT id, token, device_info, created_at, last_used_at, expires_at, is_active
            FROM user_sessions 
            WHERE user_id = $1 AND is_active = TRUE
            ORDER BY last_used_at DESC
        """, user_id)
        
        return {
            "sessions": [
                {
                    "id": session['id'],
                    "token": session['token'][:10] + "...",  # Show only first 10 chars for security
                    "device_info": session['device_info'],
                    "created_at": session['created_at'].isoformat(),
                    "last_used_at": session['last_used_at'].isoformat(),
                    "expires_at": session['expires_at'].isoformat() if session['expires_at'] else None,
                    "is_active": session['is_active']
                }
                for session in sessions
            ]
        }
    finally:
        await conn.close()

@app.post("/logout-other-sessions")
@handle_exceptions("logout-other-sessions")
async def logout_other_sessions(request: Request):
    """Logout from all other sessions except current one"""
    try:
        body = await request.json()
        token = body.get("token")
        
        if not token:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing token", "message": "Token is required"}
            )
        
        conn = await get_connection()
        try:
            # Get user_id from token
            user_id = await conn.fetchval(
                "SELECT user_id FROM user_sessions WHERE token = $1 AND is_active = TRUE",
                token
            )
            
            if not user_id:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Authentication failed", "message": "Invalid or expired token"}
                )
            
            # Deactivate all other sessions for this user
            result = await conn.execute("""
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE user_id = $1 AND token != $2 AND is_active = TRUE
            """, user_id, token)
            
            return {"message": "All other sessions logged out successfully"}
        finally:
            await conn.close()
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON", "message": "Invalid JSON body"}
        )

# Alternative GET endpoint for data retrieval ====================
@app.get("/app")
@handle_exceptions("app-get")
async def get_app_data(type: str = None, appname: str = None, token: str = None):
    """GET endpoint for retrieving data"""
    # If no parameters provided, return API documentation
    if not type and not appname and not token:
        return {
            "message": "API Documentation",
            "endpoints": {
                "POST /api/app": {
                    "description": "Main endpoint for authentication and data operations",
                    "operations": {
                        "LOGIN": {
                            "body": {
                                "type": "LOGIN",
                                "username": "string",
                                "password": "string"
                            },
                            "response": {
                                "token": "string",
                                "message": "Login successful"
                            }
                        },
                        "REGISTER": {
                            "body": {
                                "type": "REGISTER", 
                                "username": "string",
                                "password": "string"
                            },
                            "response": {
                                "token": "string",
                                "message": "Registration successful",
                                "user_id": "integer"
                            }
                        },
                        "DATA": {
                            "body": {
                                "type": "DATA",
                                "appname": "string",
                                "token": "string",
                                "method": "GET|POST",
                                "calendar_tick": "object (optional)",
                                "habits": "array (optional)",
                                "notes": "array (optional)"
                            }
                        }
                    }
                },
                "GET /api/app": {
                    "description": "Get data using query parameters",
                    "parameters": {
                        "type": "DATA (required)",
                        "appname": "string (required)",
                        "token": "string (required)"
                    },
                    "example": "/api/app?type=DATA&appname=habitmultiplayer&token=your_token"
                }
            }
        }
    
    if type != "DATA" or not appname or not token:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid parameters", "message": "Invalid parameters. Use type=DATA&appname=<appname>&token=<token>"}
        )
    
    # Verify token
    user_id = await verify_token(token)
    if not user_id:
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication failed", "message": "Invalid or expired token"}
        )
    
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
# Test endpoint for debugging ====================
@app.get("/test-error")
async def test_error():
    """Test endpoint to verify error handling and Telegram notifications"""
    try:
        # Debug information
        bot_token = variables.tb_token_server
        chat_id = "-1002864663247"
        
        # Test Telegram error sending
        await send_telegram_error("🧪 TEST: This is a test error message from the server")
        
        return {
            "message": "Test error sent to Telegram",
            "debug_info": {
                "bot_token": bot_token[:10] + "..." if bot_token else "None",
                "chat_id": chat_id,
                "token_length": len(bot_token) if bot_token else 0
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to send test error",
                "message": str(e),
                "debug_info": {
                    "bot_token": variables.tb_token_server[:10] + "..." if variables.tb_token_server else "None",
                    "chat_id": "-1002864663247"
                }
            }
        )

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
        return JSONResponse(
            status_code=400,
            content={"error": "Missing parameter", "message": "Missing 'url' parameter"}
        )

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

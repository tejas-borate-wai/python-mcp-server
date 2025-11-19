"""
FastAPI REST API Server
Exposes all MCP tools as HTTP endpoints for LLMs and applications that don't support MCP protocol.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import os
import platform
import psutil
import requests
import pyodbc

# Initialize FastAPI app
app = FastAPI(
    title="MCP Tools API",
    description="REST API exposing MCP server tools for database queries, weather, system info, and more",
    version="1.0.0"
)

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# DATABASE CONFIGURATION
# ---------------------------

DB_CONFIG = {
    "server": "localhost",
    "database": "IntimeProDB",
    "trusted_connection": "yes",
    "trust_server_certificate": "yes"
}

def get_db_connection():
    """Create and return a database connection."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        f"TrustServerCertificate={DB_CONFIG['trust_server_certificate']};"
    )
    return pyodbc.connect(conn_str)

# ---------------------------
# REQUEST/RESPONSE MODELS
# ---------------------------

class EchoRequest(BaseModel):
    message: str = Field(..., description="Message to echo back")

class AddRequest(BaseModel):
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")

class ReadFileRequest(BaseModel):
    path: str = Field(..., description="File path to read")

class WriteFileRequest(BaseModel):
    path: str = Field(..., description="File path to write")
    content: str = Field(..., description="Content to write to file")

class WebRequest(BaseModel):
    url: str = Field(..., description="URL to fetch")

class WeatherRequest(BaseModel):
    city: str = Field(..., description="City name (e.g., 'London', 'Mumbai')")

class SQLQueryRequest(BaseModel):
    query: str = Field(..., description="SQL SELECT query to execute")

class DescribeTableRequest(BaseModel):
    table_name: str = Field(..., description="Name of the table to describe")

class APIResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None

# ---------------------------
# API ENDPOINTS
# ---------------------------

@app.get("/")
async def root():
    """API information and available endpoints."""
    return {
        "name": "MCP Tools API",
        "version": "1.0.0",
        "description": "REST API exposing MCP server tools",
        "endpoints": {
            "echo": "POST /echo - Echo a message",
            "add": "POST /add - Add two numbers",
            "read_file": "POST /read-file - Read a local file",
            "write_file": "POST /write-file - Write to a local file",
            "system_info": "GET /system-info - Get system information",
            "web_request": "POST /web-request - Make HTTP GET request",
            "weather": "POST /weather - Get weather for a city",
            "sql_query": "POST /sql/query - Execute SQL SELECT query",
            "list_tables": "GET /sql/tables - List all database tables",
            "describe_table": "POST /sql/describe - Describe table structure"
        },
        "docs": "/docs - Interactive API documentation"
    }

@app.post("/echo", response_model=APIResponse)
async def echo(request: EchoRequest):
    """Echo back the input message."""
    try:
        return APIResponse(
            success=True,
            data=f"Echo: {request.message}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add", response_model=APIResponse)
async def add(request: AddRequest):
    """Add two numbers together."""
    try:
        result = request.a + request.b
        return APIResponse(
            success=True,
            data={"result": result, "calculation": f"{request.a} + {request.b} = {result}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/read-file", response_model=APIResponse)
async def read_file(request: ReadFileRequest):
    """Read the content of a local file."""
    try:
        if not os.path.exists(request.path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.path}")
        
        with open(request.path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return APIResponse(
            success=True,
            data={"path": request.path, "content": content}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/write-file", response_model=APIResponse)
async def write_file(request: WriteFileRequest):
    """Write content to a local file."""
    try:
        with open(request.path, "w", encoding="utf-8") as f:
            f.write(request.content)
        
        return APIResponse(
            success=True,
            data={"message": f"File written successfully to {request.path}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system-info", response_model=APIResponse)
async def system_info():
    """Get system and hardware information."""
    try:
        info = {
            "os": platform.platform(),
            "cpu": platform.processor(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "python_version": platform.python_version(),
            "working_directory": os.getcwd()
        }
        return APIResponse(success=True, data=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/web-request", response_model=APIResponse)
async def web_request(request: WebRequest):
    """Make an HTTP GET request to a URL."""
    try:
        response = requests.get(request.url, timeout=10)
        return APIResponse(
            success=True,
            data={
                "url": request.url,
                "status_code": response.status_code,
                "content": response.text[:5000]  # Limit to 5000 chars
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/weather", response_model=APIResponse)
async def get_weather(request: WeatherRequest):
    """Get current weather for a city."""
    try:
        # Geocode city name
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={request.city}&count=1&language=en&format=json"
        geo_response = requests.get(geocode_url)
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            raise HTTPException(status_code=404, detail=f"City '{request.city}' not found")
        
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")
        
        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=celsius"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        
        current = weather_data["current_weather"]
        
        # Weather code descriptions
        weather_desc = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
            82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        
        return APIResponse(
            success=True,
            data={
                "city": city_name,
                "country": country,
                "temperature_celsius": current["temperature"],
                "condition": weather_desc.get(current["weathercode"], "Unknown"),
                "wind_speed_kmh": current["windspeed"],
                "coordinates": {"latitude": lat, "longitude": lon}
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sql/query", response_model=APIResponse)
async def sql_query(request: SQLQueryRequest):
    """Execute a SELECT query on the SQL Server database."""
    try:
        query = request.query.strip()
        
        # Security: Only allow SELECT queries
        if not query.upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed for safety")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return APIResponse(
            success=True,
            data={
                "query": query,
                "row_count": len(results),
                "columns": columns,
                "results": results
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/sql/tables", response_model=APIResponse)
async def list_tables():
    """List all tables in the SQL Server database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        cursor.execute(query)
        tables = cursor.fetchall()
        
        table_list = [
            {
                "schema": schema,
                "name": name,
                "type": table_type,
                "full_name": f"{schema}.{name}"
            }
            for schema, name, table_type in tables
        ]
        
        cursor.close()
        conn.close()
        
        return APIResponse(
            success=True,
            data={
                "database": DB_CONFIG["database"],
                "table_count": len(table_list),
                "tables": table_list
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/sql/describe", response_model=APIResponse)
async def describe_table(request: DescribeTableRequest):
    """Get the schema/structure of a specific table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """
        cursor.execute(query, request.table_name)
        columns = cursor.fetchall()
        
        if not columns:
            raise HTTPException(status_code=404, detail=f"Table '{request.table_name}' not found")
        
        column_list = []
        for col_name, data_type, max_length, nullable, default in columns:
            type_str = data_type
            if max_length:
                type_str += f"({max_length})"
            
            column_list.append({
                "name": col_name,
                "type": type_str,
                "nullable": nullable == "YES",
                "default": default
            })
        
        cursor.close()
        conn.close()
        
        return APIResponse(
            success=True,
            data={
                "table_name": request.table_name,
                "column_count": len(column_list),
                "columns": column_list
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---------------------------
# SERVER STARTUP
# ---------------------------

def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║     MCP Tools REST API Server Started       ║
    ╚══════════════════════════════════════════════╝
    
    🌐 Server running at: http://{host}:{port}
    📚 API Documentation: http://{host}:{port}/docs
    📊 Alternative Docs: http://{host}:{port}/redoc
    
    Available Endpoints:
    ✅ POST /echo - Echo messages
    ✅ POST /add - Add numbers
    ✅ POST /read-file - Read files
    ✅ POST /write-file - Write files
    ✅ GET  /system-info - System information
    ✅ POST /web-request - HTTP requests
    ✅ POST /weather - Weather data
    ✅ POST /sql/query - SQL queries
    ✅ GET  /sql/tables - List tables
    ✅ POST /sql/describe - Table structure
    
    Press CTRL+C to stop the server
    """)
    
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_api_server()

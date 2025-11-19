import asyncio
import os
import platform
import psutil
import requests
import pyodbc
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

app = Server("supercharged-server")

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
# TOOL LIST
# ---------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # Existing tools
        Tool(
            name="echo",
            description="Echoes back the input message",
            inputSchema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"]
            }
        ),
        Tool(
            name="add",
            description="Adds two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        ),

        # NEW: Read file
        Tool(
            name="read_file",
            description="Reads the content of a local file",
            inputSchema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        ),

        # NEW: Write file
        Tool(
            name="write_file",
            description="Writes content to a local file (overwrites existing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        ),

        # NEW: System info
        Tool(
            name="system_info",
            description="Returns system/OS/hardware info",
            inputSchema={"type": "object"}  # no input
        ),

        # NEW: Web request
        Tool(
            name="web_request",
            description="Makes a GET request to a URL and returns the response text",
            inputSchema={
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"]
            }
        ),

        # NEW: Weather check
        Tool(
            name="get_weather",
            description="Gets current weather for a city using Open-Meteo API",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'London', 'New York', 'Mumbai')"
                    }
                },
                "required": ["city"]
            }
        ),
        # SQL Server Database Tools
        Tool(
            name="sql_query",
            description="Execute a SELECT query on the SQL Server database (IntimeProDB) and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute (read-only)"
                    },
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the SQL Server database (IntimeProDB)",
            inputSchema={"type": "object"}  # no input required
        ),
        Tool(
            name="describe_table",
            description="Get the schema/structure of a specific table (column names, types, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            }
        )

    ]


# ---------------------------
# TOOL IMPLEMENTATIONS
# ---------------------------

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    if name == "echo":
        msg = arguments.get("message", "")
        return [TextContent(type="text", text=f"Echo: {msg}")]

    elif name == "add":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=f"Result: {result}")]

    elif name == "read_file":
        path = arguments["path"]
        if not os.path.exists(path):
            return [TextContent(type="text", text=f"❌ File not found: {path}")]
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            return [TextContent(type="text", text=data)]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {e}")]

    elif name == "write_file":
        path = arguments["path"]
        content = arguments["content"]
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return [TextContent(type="text", text=f"✔ File written to {path}")]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {e}")]

    elif name == "system_info":
        info = {
            "OS": platform.platform(),
            "CPU": platform.processor(),
            "RAM_GB": round(psutil.virtual_memory().total / (1024**3), 2),
            "Python": platform.python_version(),
            "CWD": os.getcwd()
        }
        return [TextContent(type="text", text=str(info))]

    elif name == "web_request":
        url = arguments["url"]
        try:
            r = requests.get(url)
            return [TextContent(type="text", text=r.text[:5000])]  # limit size
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {e}")]

    elif name == "get_weather":
        city = arguments["city"]
        try:
            # First, geocode the city name to get coordinates
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            geo_response = requests.get(geocode_url)
            geo_data = geo_response.json()
            
            if not geo_data.get("results"):
                return [TextContent(type="text", text=f"❌ City '{city}' not found")]
            
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
            temp = current["temperature"]
            windspeed = current["windspeed"]
            weathercode = current["weathercode"]
            
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
            
            condition = weather_desc.get(weathercode, "Unknown")
            
            result = f"🌤️ Weather in {city_name}, {country}:\n"
            result += f"Temperature: {temp}°C\n"
            result += f"Condition: {condition}\n"
            result += f"Wind Speed: {windspeed} km/h"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error getting weather: {e}")]

    elif name == "sql_query":
        query = arguments["query"].strip()
        
        # Security: Only allow SELECT queries
        if not query.upper().startswith("SELECT"):
            return [TextContent(type="text", text="❌ Only SELECT queries are allowed for safety")]
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch results
            rows = cursor.fetchall()
            
            if not rows:
                result = "📊 Query executed successfully but returned no results."
            else:
                # Format results as a table
                result = f"📊 Query Results ({len(rows)} rows):\n\n"
                
                # Header
                result += "| " + " | ".join(columns) + " |\n"
                result += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                
                # Rows (limit to 100 for readability)
                for i, row in enumerate(rows[:100]):
                    row_values = [str(val) if val is not None else "NULL" for val in row]
                    result += "| " + " | ".join(row_values) + " |\n"
                
                if len(rows) > 100:
                    result += f"\n... and {len(rows) - 100} more rows"
            
            cursor.close()
            conn.close()
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Database error: {str(e)}")]
    
    elif name == "list_tables":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query to get all user tables
            query = """
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            cursor.execute(query)
            tables = cursor.fetchall()
            
            if not tables:
                result = "📋 No tables found in the database."
            else:
                result = f"📋 Tables in IntimeProDB ({len(tables)} tables):\n\n"
                for schema, table_name, table_type in tables:
                    result += f"  • {schema}.{table_name}\n"
            
            cursor.close()
            conn.close()
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Database error: {str(e)}")]
    
    elif name == "describe_table":
        table_name = arguments["table_name"]
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query to get column information
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
            cursor.execute(query, table_name)
            columns = cursor.fetchall()
            
            if not columns:
                result = f"❌ Table '{table_name}' not found or has no columns."
            else:
                result = f"📊 Structure of table '{table_name}':\n\n"
                result += "| Column | Type | Nullable | Default |\n"
                result += "| --- | --- | --- | --- |\n"
                
                for col_name, data_type, max_length, nullable, default in columns:
                    type_str = data_type
                    if max_length:
                        type_str += f"({max_length})"
                    
                    default_str = str(default) if default else ""
                    result += f"| {col_name} | {type_str} | {nullable} | {default_str} |\n"
            
            cursor.close()
            conn.close()
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Database error: {str(e)}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ---------------------------
# RUNNER
# ---------------------------

async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def run() -> None:
    asyncio.run(main())

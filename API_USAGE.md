# MCP Tools REST API - Usage Guide

## 🚀 Quick Start

### Start the API Server

```powershell
uv run mcp-api
```

The server will start at: **http://localhost:8000**

### Interactive Documentation

Visit these URLs in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 Available Endpoints

### 1. **Echo** - Test endpoint
**POST** `/echo`

```json
{
  "message": "Hello World"
}
```

**Response:**
```json
{
  "success": true,
  "data": "Echo: Hello World",
  "error": null
}
```

### 2. **Add Numbers**
**POST** `/add`

```json
{
  "a": 25,
  "b": 17
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "result": 42,
    "calculation": "25 + 17 = 42"
  }
}
```

### 3. **Read File**
**POST** `/read-file`

```json
{
  "path": "C:\\Users\\YourName\\Desktop\\test.txt"
}
```

### 4. **Write File**
**POST** `/write-file`

```json
{
  "path": "C:\\Users\\YourName\\Desktop\\output.txt",
  "content": "This is the file content"
}
```

### 5. **System Information**
**GET** `/system-info`

No request body needed.

**Response:**
```json
{
  "success": true,
  "data": {
    "os": "Windows-10-10.0.19045-SP0",
    "cpu": "Intel64 Family 6 Model 140 Stepping 1, GenuineIntel",
    "ram_gb": 16.0,
    "ram_available_gb": 8.5,
    "python_version": "3.10.0",
    "working_directory": "C:\\Users\\..."
  }
}
```

### 6. **Weather**
**POST** `/weather`

```json
{
  "city": "Mumbai"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "city": "Mumbai",
    "country": "India",
    "temperature_celsius": 28.5,
    "condition": "Partly cloudy",
    "wind_speed_kmh": 15.2,
    "coordinates": {
      "latitude": 19.0761,
      "longitude": 72.8775
    }
  }
}
```

### 7. **SQL Query** (Execute SELECT)
**POST** `/sql/query`

```json
{
  "query": "SELECT TOP 10 * FROM YourTableName"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "SELECT TOP 10 * FROM YourTableName",
    "row_count": 10,
    "columns": ["id", "name", "email"],
    "results": [
      {"id": 1, "name": "John", "email": "john@example.com"},
      {"id": 2, "name": "Jane", "email": "jane@example.com"}
    ]
  }
}
```

### 8. **List Database Tables**
**GET** `/sql/tables`

No request body needed.

**Response:**
```json
{
  "success": true,
  "data": {
    "database": "IntimeProDB",
    "table_count": 15,
    "tables": [
      {
        "schema": "dbo",
        "name": "Users",
        "type": "BASE TABLE",
        "full_name": "dbo.Users"
      }
    ]
  }
}
```

### 9. **Describe Table Structure**
**POST** `/sql/describe`

```json
{
  "table_name": "Users"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "table_name": "Users",
    "column_count": 5,
    "columns": [
      {
        "name": "id",
        "type": "int",
        "nullable": false,
        "default": null
      },
      {
        "name": "username",
        "type": "varchar(50)",
        "nullable": false,
        "default": null
      }
    ]
  }
}
```

### 10. **Web Request**
**POST** `/web-request`

```json
{
  "url": "https://api.github.com/users/github"
}
```

## 🔧 Usage Examples

### PowerShell (Windows)

```powershell
# Test echo endpoint
Invoke-RestMethod -Uri "http://localhost:8000/echo" -Method POST -Body '{"message":"Hello"}' -ContentType "application/json"

# Get system info
Invoke-RestMethod -Uri "http://localhost:8000/system-info" -Method GET

# Check weather
Invoke-RestMethod -Uri "http://localhost:8000/weather" -Method POST -Body '{"city":"London"}' -ContentType "application/json"

# List database tables
Invoke-RestMethod -Uri "http://localhost:8000/sql/tables" -Method GET

# Run SQL query
$body = @{query = "SELECT TOP 5 * FROM YourTable"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/sql/query" -Method POST -Body $body -ContentType "application/json"
```

### Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Echo test
response = requests.post(f"{BASE_URL}/echo", json={"message": "Hello"})
print(response.json())

# Get weather
response = requests.post(f"{BASE_URL}/weather", json={"city": "Mumbai"})
print(response.json())

# List tables
response = requests.get(f"{BASE_URL}/sql/tables")
print(response.json())

# SQL query
response = requests.post(
    f"{BASE_URL}/sql/query",
    json={"query": "SELECT TOP 10 * FROM YourTable"}
)
print(response.json())
```

### cURL

```bash
# Echo
curl -X POST http://localhost:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello World"}'

# Weather
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"Mumbai"}'

# List tables
curl http://localhost:8000/sql/tables

# SQL query
curl -X POST http://localhost:8000/sql/query \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT TOP 5 * FROM YourTable"}'
```

### JavaScript/Fetch

```javascript
// Echo
fetch('http://localhost:8000/echo', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello' })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Weather
fetch('http://localhost:8000/weather', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ city: 'London' })
})
  .then(res => res.json())
  .then(data => console.log(data));

// SQL Query
fetch('http://localhost:8000/sql/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'SELECT TOP 10 * FROM Users' })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## 🤖 Using with LLMs

### OpenAI Function Calling

```python
import openai

# Define functions for OpenAI
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "sql_query",
        "description": "Execute SQL query on database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL SELECT query"}
            },
            "required": ["query"]
        }
    }
]

# When OpenAI requests a function call, make API request
def execute_function(function_name, arguments):
    if function_name == "get_weather":
        response = requests.post(
            "http://localhost:8000/weather",
            json=arguments
        )
    elif function_name == "sql_query":
        response = requests.post(
            "http://localhost:8000/sql/query",
            json=arguments
        )
    return response.json()
```

## 🔒 Security Notes

1. **SQL Queries**: Only SELECT queries are allowed (no INSERT, UPDATE, DELETE)
2. **CORS**: Currently allows all origins (`*`) - restrict in production
3. **Authentication**: No authentication implemented - add API keys for production
4. **File Access**: Can read/write any files the process has access to - add path restrictions if needed

## 🌐 Production Deployment

To run in production:

```powershell
# Change the start_api_server call in api_server.py
# Or run directly with uvicorn
uvicorn mcp_server.api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 Response Format

All endpoints return a consistent response structure:

```json
{
  "success": true/false,
  "data": {...},
  "error": "error message" // only if success is false
}
```

## 🛑 Stopping the Server

Press **CTRL+C** in the terminal where the server is running.

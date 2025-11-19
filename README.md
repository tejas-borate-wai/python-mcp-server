# MCP Server

A powerful Model Context Protocol (MCP) server AND REST API in Python that provides:
- 🗄️ SQL Server database operations
- 🌤️ Weather information
- 📁 File operations
- 🌐 Web requests
- 💻 System information
- ➕ Utility tools

## 🚀 Two Ways to Use

### 1️⃣ MCP Protocol (For Claude Desktop & MCP-compatible LLMs)
Traditional MCP server for direct integration with Claude Desktop

### 2️⃣ REST API (For Any LLM or Application)
FastAPI REST server that exposes all MCP tools as HTTP endpoints
Perfect for LLMs that don't support MCP protocol (ChatGPT, Gemini, etc.)

## Installation

This project uses `uv` for package management. If you haven't installed `uv` yet:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Then add it to your PATH:
```powershell
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"
```

## Setup

Install dependencies:
```powershell
uv sync
```

## Running the Server

### Option 1: MCP Server (for Claude Desktop)

Run the MCP server:
```powershell
uv run mcp-server
```

### Option 2: REST API Server (for any LLM)

Run the FastAPI REST API server:
```powershell
uv run mcp-api
```

Server will start at: **http://localhost:8000**
- 📚 Interactive API docs: http://localhost:8000/docs
- 📊 Alternative docs: http://localhost:8000/redoc

See **[API_USAGE.md](API_USAGE.md)** for complete API documentation and examples.

Or activate the virtual environment and run directly:
```powershell
.venv\Scripts\activate
python -m mcp_server
```

## Available Tools

### MCP Server Tools:
1. **echo** - Echoes back the input message
2. **add** - Adds two numbers together
3. **read_file** - Reads content from a local file
4. **write_file** - Writes content to a local file
5. **system_info** - Returns system/OS/hardware information
6. **web_request** - Makes HTTP GET requests to URLs
7. **get_weather** - Gets current weather for any city
8. **sql_query** - Executes SELECT queries on SQL Server database
9. **list_tables** - Lists all tables in the database
10. **describe_table** - Shows table structure (columns, types, etc.)

### REST API Endpoints:
All MCP tools are also available as HTTP endpoints:
- `POST /echo` - Echo messages
- `POST /add` - Add numbers
- `POST /read-file` - Read files
- `POST /write-file` - Write files
- `GET /system-info` - System information
- `POST /web-request` - HTTP requests
- `POST /weather` - Weather data
- `POST /sql/query` - SQL queries
- `GET /sql/tables` - List tables
- `POST /sql/describe` - Table structure

See **[API_USAGE.md](API_USAGE.md)** for detailed API documentation.

## Project Structure

```
python-mcp-server/
├── src/
│   └── mcp_server/
│       └── __init__.py    # Main server implementation
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lock file
└── README.md             # This file
```

## Connecting to Claude Desktop

To use this MCP server with Claude Desktop:

1. **Locate your Claude config file** at:
   ```
   C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json
   ```

2. **Add this server configuration**:
   ```json
   {
     "mcpServers": {
       "python-mcp-server": {
         "command": "C:\\Users\\TejasBorate\\.local\\bin\\uv.exe",
         "args": [
           "--directory",
           "C:\\Users\\TejasBorate\\Desktop\\python-mcp-server",
           "run",
           "mcp-server"
         ]
       }
     }
   }
   ```
   
   **Note**: Use the full path to `uv.exe` so Claude Desktop can find it.

3. **Restart Claude Desktop** completely (quit and reopen)

4. **Verify connection**: In Claude Desktop, you should see a 🔨 (hammer) icon indicating MCP tools are available. Click it to see your `echo` and `add` tools.

### Quick Setup Script

Run this in PowerShell to automatically configure Claude Desktop:

```powershell
$config = @{
    mcpServers = @{
        "python-mcp-server" = @{
            command = "C:\Users\TejasBorate\.local\bin\uv.exe"
            args = @(
                "--directory"
                "C:\Users\TejasBorate\Desktop\python-mcp-server"
                "run"
                "mcp-server"
            )
        }
    }
}
$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "$env:APPDATA\Claude\claude_desktop_config.json" -Encoding ASCII
Write-Host "✅ Configuration updated! Please restart Claude Desktop."
```

## Development

To add new tools, edit `src/mcp_server/__init__.py` and:
1. Add the tool definition in `list_tools()`
2. Add the tool handler in `call_tool()`
3. Restart Claude Desktop to reload the server

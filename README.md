# MCP Server

A simple Model Context Protocol (MCP) server implementation in Python.

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

Run the MCP server:
```powershell
uv run mcp-server
```

Or activate the virtual environment and run directly:
```powershell
.venv\Scripts\activate
python -m mcp_server
```

## Available Tools

This server provides two example tools:

1. **echo** - Echoes back the input message
2. **add** - Adds two numbers together

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

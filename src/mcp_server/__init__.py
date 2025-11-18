import asyncio
import os
import platform
import psutil
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

app = Server("supercharged-server")


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

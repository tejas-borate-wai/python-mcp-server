# 🚀 Quick Start Guide

## Start the REST API Server

```powershell
uv run mcp-api
```

✅ Server running at: **http://localhost:8000**

## Test It Now!

### 1. Open Interactive Documentation
Visit in your browser: **http://localhost:8000/docs**

### 2. Test with PowerShell

```powershell
# Get system info
Invoke-RestMethod -Uri "http://localhost:8000/system-info" -Method GET

# Check weather
$body = @{city = "Mumbai"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/weather" -Method POST -Body $body -ContentType "application/json"

# List database tables
Invoke-RestMethod -Uri "http://localhost:8000/sql/tables" -Method GET

# Query database
$body = @{query = "SELECT TOP 5 * FROM YourTableName"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/sql/query" -Method POST -Body $body -ContentType "application/json"
```

## For Claude Desktop (MCP Protocol)

Already configured! Just restart Claude Desktop.

## Next Steps

1. ✅ Test the API with your database
2. ✅ Read [API_USAGE.md](API_USAGE.md) for all endpoints
3. ✅ Integrate with your LLM of choice
4. ✅ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture details

## Need Help?

- Interactive docs: http://localhost:8000/docs
- API documentation: [API_USAGE.md](API_USAGE.md)
- Project overview: [README.md](README.md)

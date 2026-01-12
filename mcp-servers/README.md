# MCP Servers Directory Structure

This directory contains all Model Context Protocol (MCP) servers for JARVIS.
Each server runs independently and exposes tools that the agent can use.

## Server List

1. **mcp-memory-db** (Port 8001)
   - Conversation storage
   - User preferences
   - Interaction logging
   - Task history

2. **mcp-vector-db** (Port 8002)
   - Semantic search
   - Embedding storage
   - RAG context retrieval

3. **mcp-telegram** (Port 8003)
   - Send messages
   - Get updates
   - Send notifications

4. **mcp-calendar-google** (Port 8004)
   - List events
   - Create/update/delete events
   - Natural language scheduling

5. **mcp-gmail** (Port 8005)
   - List/read emails
   - Create drafts
   - Send emails

6. **mcp-windows-os** (Port 8006)
   - Open/close applications
   - Run PowerShell commands
   - File management

7. **mcp-voice** (Port 8007)
   - Speech-to-text
   - Text-to-speech

## Running Servers

Each server can be run independently:

```bash
cd mcp-servers/mcp-memory-db
uv run python server.py
```

Or use the provided startup scripts.

## Architecture

```
Agent (MCP Client)
    ↓
HTTP/JSON
    ↓
MCP Server
    ↓
Tool Execution
    ↓
External System/Database
```

## Development

See individual server README files for specific implementation details.

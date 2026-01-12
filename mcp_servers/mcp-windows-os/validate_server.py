"""
Test script for Windows OS MCP Server
"""
import asyncio
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from server import WindowsOSServer


async def test_windows_server():
    """Test Windows OS MCP Server"""
    print("=" * 60)
    print("Testing Windows OS MCP Server")
    print("=" * 60)
    
    server = WindowsOSServer()
    server.setup_tools()
    
    print(f"\n✅ Server initialized: {server.name}")
    print(f"📝 Tools registered: {len(server.tools)}")
    print(f"🔧 Available tools:")
    for tool in server.tool_definitions:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test 1: Get system info
    print("\n" + "=" * 60)
    print("Test 1: Get System Info")
    print("=" * 60)
    result = await server.get_system_info({})
    if result.get("success"):
        print("✅ System info retrieved:")
        info = result.get("system_info", {})
        for key, value in info.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: List directory
    print("\n" + "=" * 60)
    print("Test 2: List Current Directory")
    print("=" * 60)
    result = await server.list_directory({"path": "."})
    if result.get("success"):
        print(f"✅ Found {result.get('count')} items:")
        for item in result.get("items", [])[:5]:  # Show first 5
            item_type = "📁" if item["is_directory"] else "📄"
            print(f"   {item_type} {item['name']}")
        if result.get('count', 0) > 5:
            print(f"   ... and {result.get('count') - 5} more")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 3: Get clipboard (safe, read-only)
    print("\n" + "=" * 60)
    print("Test 3: Get Clipboard Content")
    print("=" * 60)
    result = await server.get_clipboard({})
    if result.get("success"):
        content = result.get("content", "")
        if content:
            print(f"✅ Clipboard content (first 100 chars): {content[:100]}")
        else:
            print("✅ Clipboard is empty")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 4: List running processes (filtered)
    print("\n" + "=" * 60)
    print("Test 4: List Running Processes (filtered: 'python')")
    print("=" * 60)
    result = await server.list_processes({"filter": "python"})
    if result.get("success"):
        processes = result.get("processes", [])
        print(f"✅ Found {len(processes)} Python processes:")
        for proc in processes[:3]:  # Show first 3
            print(f"   - {proc.get('Name')} (PID: {proc.get('Id')})")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 5: Run simple PowerShell command
    print("\n" + "=" * 60)
    print("Test 5: Run PowerShell Command (Get-Date)")
    print("=" * 60)
    result = await server.run_powershell({"command": "Get-Date"})
    if result.get("success"):
        print(f"✅ Command executed:")
        print(f"   Output: {result.get('stdout', '').strip()}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_windows_server())

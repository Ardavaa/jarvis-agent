"""
Test script for Gmail MCP Server
"""
import asyncio
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from server import GmailServer


async def test_gmail_server():
    """Test Gmail MCP Server"""
    print("=" * 60)
    print("Testing Gmail MCP Server")
    print("=" * 60)
    
    server = GmailServer()
    server.setup_tools()
    
    print(f"\n✅ Server initialized: {server.name}")
    print(f"📝 Tools registered: {len(server.tools)}")
    print(f"🔧 Available tools:")
    for tool in server.tool_definitions:
        print(f"   - {tool.name}: {tool.description}")
    
    # Check authentication
    if not server.service:
        print("\n❌ Gmail not authenticated")
        print("Please check your credentials and try again")
        return
    
    print("\n✅ Gmail authenticated successfully")
    
    # Test 1: List recent messages
    print("\n" + "=" * 60)
    print("Test 1: List Recent Messages")
    print("=" * 60)
    result = await server.list_messages({"max_results": 5})
    if result.get("success"):
        messages = result.get("messages", [])
        print(f"✅ Found {len(messages)} recent messages:")
        for msg in messages:
            print(f"   📧 From: {msg['from']}")
            print(f"      Subject: {msg['subject']}")
            print(f"      Date: {msg['date']}")
            print(f"      Snippet: {msg['snippet'][:60]}...")
            print()
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: Search messages
    print("\n" + "=" * 60)
    print("Test 2: Search Messages (query: 'is:unread')")
    print("=" * 60)
    result = await server.search_messages({
        "query": "is:unread",
        "max_results": 3
    })
    if result.get("success"):
        messages = result.get("messages", [])
        print(f"✅ Found {len(messages)} unread messages:")
        for msg in messages:
            print(f"   📧 {msg['subject']} - {msg['from']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 3: Read a specific message (if available)
    if result.get("success") and result.get("messages"):
        print("\n" + "=" * 60)
        print("Test 3: Read Message Details")
        print("=" * 60)
        first_msg = result["messages"][0]
        read_result = await server.read_message({"message_id": first_msg["id"]})
        if read_result.get("success"):
            print(f"✅ Message details:")
            print(f"   From: {read_result['from']}")
            print(f"   To: {read_result['to']}")
            print(f"   Subject: {read_result['subject']}")
            print(f"   Body (first 200 chars): {read_result['body'][:200]}...")
        else:
            print(f"❌ Failed: {read_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ Gmail tests completed!")
    print("=" * 60)
    print("\nNote: Send/Draft tests skipped to avoid sending emails")
    print("You can test those manually if needed")


if __name__ == "__main__":
    asyncio.run(test_gmail_server())

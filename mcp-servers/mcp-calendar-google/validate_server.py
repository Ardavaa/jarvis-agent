"""
Test script for Google Calendar MCP Server
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from server import GoogleCalendarServer


async def test_calendar_server():
    """Test Google Calendar MCP Server"""
    print("=" * 60)
    print("Testing Google Calendar MCP Server")
    print("=" * 60)
    
    server = GoogleCalendarServer()
    server.setup_tools()
    
    print(f"\n✅ Server initialized: {server.name}")
    print(f"📝 Tools registered: {len(server.tools)}")
    print(f"🔧 Available tools:")
    for tool in server.tool_definitions:
        print(f"   - {tool.name}: {tool.description}")
    
    # Check authentication
    if not server.service:
        print("\n❌ Google Calendar not authenticated")
        print("Please check your credentials and try again")
        return
    
    print("\n✅ Google Calendar authenticated successfully")
    
    # Test 1: List upcoming events
    print("\n" + "=" * 60)
    print("Test 1: List Upcoming Events")
    print("=" * 60)
    result = await server.list_events({"max_results": 5})
    if result.get("success"):
        events = result.get("events", [])
        print(f"✅ Found {len(events)} upcoming events:")
        for event in events:
            print(f"   📅 {event['summary']}")
            print(f"      Start: {event['start']}")
            print(f"      End: {event['end']}")
            if event.get('description'):
                print(f"      Description: {event['description'][:50]}...")
            print()
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: Search events
    print("\n" + "=" * 60)
    print("Test 2: Search Events (query: 'meeting')")
    print("=" * 60)
    result = await server.search_events({
        "query": "meeting",
        "max_results": 3
    })
    if result.get("success"):
        events = result.get("events", [])
        print(f"✅ Found {len(events)} events matching 'meeting':")
        for event in events:
            print(f"   📅 {event['summary']} - {event['start']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ Calendar tests completed!")
    print("=" * 60)
    print("\nNote: Create/Update/Delete tests skipped to avoid modifying your calendar")
    print("You can test those manually if needed")


if __name__ == "__main__":
    asyncio.run(test_calendar_server())

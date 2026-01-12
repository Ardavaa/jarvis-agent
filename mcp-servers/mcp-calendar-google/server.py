"""
MCP Google Calendar Server
Provides tools for Google Calendar integration
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_server import BaseMCPServer

# Google Calendar API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarServer(BaseMCPServer):
    """
    MCP server for Google Calendar operations
    """
    
    def __init__(self):
        super().__init__(
            name="MCP Google Calendar Server",
            description="Provides Google Calendar integration",
            version="1.0.0",
            port=8004
        )
        
        # Get project root (2 levels up from this file)
        project_root = os.path.join(os.path.dirname(__file__), '../..')
        
        self.credentials_path = os.getenv(
            "GOOGLE_CREDENTIALS_PATH", 
            os.path.join(project_root, "credentials/google_credentials.json")
        )
        self.token_path = os.getenv(
            "GOOGLE_TOKEN_PATH", 
            os.path.join(project_root, "credentials/google_token.json")
        )
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        
        self.service = None
        
        if not GOOGLE_AVAILABLE:
            print("⚠️  Warning: Google API libraries not installed")
            print("   Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
        else:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif os.path.exists(self.credentials_path):
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            else:
                print(f"⚠️  Warning: Credentials file not found at {self.credentials_path}")
                return
            
            # Save credentials
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar authenticated")
    
    def setup_tools(self):
        """Register all Google Calendar tools"""
        
        self.register_tool(
            name="list_calendar_events",
            description="List upcoming calendar events",
            parameters=[
                {"name": "max_results", "type": "integer", "required": False},
                {"name": "time_min", "type": "string", "required": False},
                {"name": "time_max", "type": "string", "required": False}
            ],
            handler=self.list_events
        )
        
        self.register_tool(
            name="create_calendar_event",
            description="Create a new calendar event",
            parameters=[
                {"name": "summary", "type": "string", "required": True},
                {"name": "start_time", "type": "string", "required": True},
                {"name": "end_time", "type": "string", "required": True},
                {"name": "description", "type": "string", "required": False},
                {"name": "location", "type": "string", "required": False}
            ],
            handler=self.create_event
        )
        
        self.register_tool(
            name="update_calendar_event",
            description="Update an existing calendar event",
            parameters=[
                {"name": "event_id", "type": "string", "required": True},
                {"name": "summary", "type": "string", "required": False},
                {"name": "start_time", "type": "string", "required": False},
                {"name": "end_time", "type": "string", "required": False},
                {"name": "description", "type": "string", "required": False}
            ],
            handler=self.update_event
        )
        
        self.register_tool(
            name="delete_calendar_event",
            description="Delete a calendar event",
            parameters=[
                {"name": "event_id", "type": "string", "required": True}
            ],
            handler=self.delete_event
        )
        
        self.register_tool(
            name="search_calendar_events",
            description="Search for calendar events by query",
            parameters=[
                {"name": "query", "type": "string", "required": True},
                {"name": "max_results", "type": "integer", "required": False}
            ],
            handler=self.search_events
        )
    
    # Tool handlers
    
    async def list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List upcoming calendar events"""
        if not self.service:
            return {"success": False, "error": "Google Calendar not authenticated"}
        
        max_results = params.get("max_results", 10)
        time_min = params.get("time_min", datetime.utcnow().isoformat() + 'Z')
        time_max = params.get("time_max")
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                formatted_events.append({
                    "id": event['id'],
                    "summary": event.get('summary', 'No title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "description": event.get('description', ''),
                    "location": event.get('location', '')
                })
            
            return {
                "success": True,
                "events": formatted_events,
                "count": len(formatted_events)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        if not self.service:
            return {"success": False, "error": "Google Calendar not authenticated"}
        
        event = {
            'summary': params['summary'],
            'start': {'dateTime': params['start_time'], 'timeZone': 'UTC'},
            'end': {'dateTime': params['end_time'], 'timeZone': 'UTC'},
        }
        
        if 'description' in params:
            event['description'] = params['description']
        if 'location' in params:
            event['location'] = params['location']
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "link": created_event.get('htmlLink'),
                "summary": created_event['summary']
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event"""
        if not self.service:
            return {"success": False, "error": "Google Calendar not authenticated"}
        
        event_id = params['event_id']
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'summary' in params:
                event['summary'] = params['summary']
            if 'description' in params:
                event['description'] = params['description']
            if 'start_time' in params:
                event['start'] = {'dateTime': params['start_time'], 'timeZone': 'UTC'}
            if 'end_time' in params:
                event['end'] = {'dateTime': params['end_time'], 'timeZone': 'UTC'}
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": updated_event['id'],
                "summary": updated_event['summary']
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event"""
        if not self.service:
            return {"success": False, "error": "Google Calendar not authenticated"}
        
        event_id = params['event_id']
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                "success": True,
                "event_id": event_id,
                "status": "deleted"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for calendar events by query"""
        if not self.service:
            return {"success": False, "error": "Google Calendar not authenticated"}
        
        query = params['query']
        max_results = params.get("max_results", 10)
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                formatted_events.append({
                    "id": event['id'],
                    "summary": event.get('summary', 'No title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "description": event.get('description', '')
                })
            
            return {
                "success": True,
                "query": query,
                "events": formatted_events,
                "count": len(formatted_events)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    server = GoogleCalendarServer()
    server.run()

"""
MCP Gmail Server
Provides tools for Gmail integration
"""
import sys
import os
import base64
from email.mime.text import MIMEText
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_server import BaseMCPServer

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailServer(BaseMCPServer):
    """
    MCP server for Gmail operations
    """
    
    def __init__(self):
        super().__init__(
            name="MCP Gmail Server",
            description="Provides Gmail integration",
            version="1.0.0",
            port=8005
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
        self.user_email = os.getenv("GMAIL_USER_EMAIL", "me")
        
        self.service = None
        
        if not GOOGLE_AVAILABLE:
            print("⚠️  Warning: Google API libraries not installed")
        else:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
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
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail authenticated")
    
    def setup_tools(self):
        """Register all Gmail tools"""
        
        self.register_tool(
            name="list_gmail_messages",
            description="List Gmail messages",
            parameters=[
                {"name": "query", "type": "string", "required": False},
                {"name": "max_results", "type": "integer", "required": False},
                {"name": "label_ids", "type": "array", "required": False}
            ],
            handler=self.list_messages
        )
        
        self.register_tool(
            name="read_gmail_message",
            description="Read a specific Gmail message",
            parameters=[
                {"name": "message_id", "type": "string", "required": True}
            ],
            handler=self.read_message
        )
        
        self.register_tool(
            name="send_gmail_message",
            description="Send an email via Gmail",
            parameters=[
                {"name": "to", "type": "string", "required": True},
                {"name": "subject", "type": "string", "required": True},
                {"name": "body", "type": "string", "required": True},
                {"name": "cc", "type": "string", "required": False},
                {"name": "bcc", "type": "string", "required": False}
            ],
            handler=self.send_message
        )
        
        self.register_tool(
            name="create_gmail_draft",
            description="Create a draft email",
            parameters=[
                {"name": "to", "type": "string", "required": True},
                {"name": "subject", "type": "string", "required": True},
                {"name": "body", "type": "string", "required": True}
            ],
            handler=self.create_draft
        )
        
        self.register_tool(
            name="search_gmail",
            description="Search Gmail messages",
            parameters=[
                {"name": "query", "type": "string", "required": True},
                {"name": "max_results", "type": "integer", "required": False}
            ],
            handler=self.search_messages
        )
        
        self.register_tool(
            name="mark_as_read",
            description="Mark message as read",
            parameters=[
                {"name": "message_id", "type": "string", "required": True}
            ],
            handler=self.mark_as_read
        )
        
        self.register_tool(
            name="mark_as_unread",
            description="Mark message as unread",
            parameters=[
                {"name": "message_id", "type": "string", "required": True}
            ],
            handler=self.mark_as_unread
        )
    
    # Tool handlers
    
    async def list_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Gmail messages"""
        if not self.service:
            return {"success": False, "error": "Gmail not authenticated"}
        
        query = params.get("query", "")
        max_results = params.get("max_results", 10)
        label_ids = params.get("label_ids", [])
        
        try:
            results = self.service.users().messages().list(
                userId=self.user_email,
                q=query,
                maxResults=max_results,
                labelIds=label_ids
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get message details
            detailed_messages = []
            for msg in messages[:max_results]:
                message = self.service.users().messages().get(
                    userId=self.user_email,
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                
                detailed_messages.append({
                    "id": message['id'],
                    "from": headers.get('From', ''),
                    "subject": headers.get('Subject', ''),
                    "date": headers.get('Date', ''),
                    "snippet": message.get('snippet', '')
                })
            
            return {
                "success": True,
                "messages": detailed_messages,
                "count": len(detailed_messages)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def read_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a specific Gmail message"""
        if not self.service:
            return {"success": False, "error": "Gmail not authenticated"}
        
        message_id = params['message_id']
        
        try:
            message = self.service.users().messages().get(
                userId=self.user_email,
                id=message_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Get body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(
                    message['payload']['body']['data']
                ).decode('utf-8')
            
            return {
                "success": True,
                "id": message['id'],
                "from": headers.get('From', ''),
                "to": headers.get('To', ''),
                "subject": headers.get('Subject', ''),
                "date": headers.get('Date', ''),
                "body": body,
                "snippet": message.get('snippet', '')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email via Gmail"""
        if not self.service:
            return {"success": False, "error": "Gmail not authenticated"}
        
        message = MIMEText(params['body'])
        message['to'] = params['to']
        message['subject'] = params['subject']
        
        if 'cc' in params:
            message['cc'] = params['cc']
        if 'bcc' in params:
            message['bcc'] = params['bcc']
        
        try:
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            sent_message = self.service.users().messages().send(
                userId=self.user_email,
                body={'raw': raw}
            ).execute()
            
            return {
                "success": True,
                "message_id": sent_message['id'],
                "to": params['to'],
                "subject": params['subject'],
                "status": "sent"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a draft email"""
        if not self.service:
            return {"success": False, "error": "Gmail not authenticated"}
        
        message = MIMEText(params['body'])
        message['to'] = params['to']
        message['subject'] = params['subject']
        
        try:
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            draft = self.service.users().drafts().create(
                userId=self.user_email,
                body={'message': {'raw': raw}}
            ).execute()
            
            return {
                "success": True,
                "draft_id": draft['id'],
                "message_id": draft['message']['id'],
                "to": params['to'],
                "subject": params['subject'],
                "status": "draft_created"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search Gmail messages"""
        return await self.list_messages({
            "query": params['query'],
            "max_results": params.get("max_results", 10)
        })
    
    async def mark_as_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mark message as read"""
        if not self.service:
            return {"success": False, "error": "Gmail not authenticated"}
        
        message_id = params['message_id']
        
        try:
            self.service.users().messages().modify(
                userId=self.user_email,
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return {
                "success": True,
                "message_id": message_id,
                "status": "marked_as_read"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def mark_as_unread(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mark message as unread"""
        if not self.service:
            return {"success": False, "error": "Gmail not authenticated"}
        
        message_id = params['message_id']
        
        try:
            self.service.users().messages().modify(
                userId=self.user_email,
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            
            return {
                "success": True,
                "message_id": message_id,
                "status": "marked_as_unread"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    server = GmailServer()
    server.run()

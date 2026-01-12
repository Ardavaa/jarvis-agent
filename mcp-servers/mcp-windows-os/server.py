"""
MCP Windows OS Server
Provides tools for Windows automation and system control
"""
import sys
import os
import subprocess
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_server import BaseMCPServer


class WindowsOSServer(BaseMCPServer):
    """
    MCP server for Windows OS operations
    """
    
    def __init__(self):
        super().__init__(
            name="MCP Windows OS Server",
            description="Provides Windows automation and system control",
            version="1.0.0",
            port=8006
        )
        
        # Check if running on Windows
        if os.name != 'nt':
            print("⚠️  Warning: This server is designed for Windows OS")
    
    def setup_tools(self):
        """Register all Windows OS tools"""
        
        self.register_tool(
            name="run_powershell_command",
            description="Execute a PowerShell command",
            parameters=[
                {"name": "command", "type": "string", "required": True},
                {"name": "timeout", "type": "integer", "required": False}
            ],
            handler=self.run_powershell
        )
        
        self.register_tool(
            name="run_cmd_command",
            description="Execute a CMD command",
            parameters=[
                {"name": "command", "type": "string", "required": True},
                {"name": "timeout", "type": "integer", "required": False}
            ],
            handler=self.run_cmd
        )
        
        self.register_tool(
            name="open_application",
            description="Open a Windows application",
            parameters=[
                {"name": "app_name", "type": "string", "required": True},
                {"name": "args", "type": "string", "required": False}
            ],
            handler=self.open_application
        )
        
        self.register_tool(
            name="close_application",
            description="Close a Windows application by name",
            parameters=[
                {"name": "app_name", "type": "string", "required": True}
            ],
            handler=self.close_application
        )
        
        self.register_tool(
            name="list_running_processes",
            description="List currently running processes",
            parameters=[
                {"name": "filter", "type": "string", "required": False}
            ],
            handler=self.list_processes
        )
        
        self.register_tool(
            name="get_system_info",
            description="Get Windows system information",
            parameters=[],
            handler=self.get_system_info
        )
        
        self.register_tool(
            name="create_file",
            description="Create a file with content",
            parameters=[
                {"name": "path", "type": "string", "required": True},
                {"name": "content", "type": "string", "required": True}
            ],
            handler=self.create_file
        )
        
        self.register_tool(
            name="read_file",
            description="Read file content",
            parameters=[
                {"name": "path", "type": "string", "required": True}
            ],
            handler=self.read_file
        )
        
        self.register_tool(
            name="list_directory",
            description="List directory contents",
            parameters=[
                {"name": "path", "type": "string", "required": True}
            ],
            handler=self.list_directory
        )
        
        self.register_tool(
            name="get_clipboard",
            description="Get clipboard content",
            parameters=[],
            handler=self.get_clipboard
        )
        
        self.register_tool(
            name="set_clipboard",
            description="Set clipboard content",
            parameters=[
                {"name": "text", "type": "string", "required": True}
            ],
            handler=self.set_clipboard
        )
    
    # Tool handlers
    
    async def run_powershell(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a PowerShell command"""
        command = params['command']
        timeout = params.get("timeout", 30)
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_cmd(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CMD command"""
        command = params['command']
        timeout = params.get("timeout", 30)
        
        try:
            result = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def open_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open a Windows application"""
        app_name = params['app_name']
        args = params.get("args", "")
        
        try:
            command = f'Start-Process "{app_name}"'
            if args:
                command += f' -ArgumentList "{args}"'
            
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "app_name": app_name,
                "status": "opened" if result.returncode == 0 else "failed",
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close a Windows application by name"""
        app_name = params['app_name']
        
        try:
            # Try to close gracefully first
            command = f'Stop-Process -Name "{app_name}" -ErrorAction SilentlyContinue'
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": True,
                "app_name": app_name,
                "status": "closed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_processes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List currently running processes"""
        filter_name = params.get("filter", "")
        
        try:
            command = "Get-Process"
            if filter_name:
                command += f' | Where-Object {{$_.Name -like "*{filter_name}*"}}'
            command += ' | Select-Object Name, Id, CPU, WorkingSet | ConvertTo-Json'
            
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                processes = json.loads(result.stdout) if result.stdout.strip() else []
                
                # Ensure it's a list
                if isinstance(processes, dict):
                    processes = [processes]
                
                return {
                    "success": True,
                    "processes": processes,
                    "count": len(processes)
                }
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Windows system information"""
        try:
            command = """
            $info = @{
                ComputerName = $env:COMPUTERNAME
                UserName = $env:USERNAME
                OS = (Get-CimInstance Win32_OperatingSystem).Caption
                Version = (Get-CimInstance Win32_OperatingSystem).Version
                Architecture = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
                TotalMemoryGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
                Processor = (Get-CimInstance Win32_Processor).Name
            }
            $info | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                return {
                    "success": True,
                    "system_info": info
                }
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a file with content"""
        path = params['path']
        content = params['content']
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": path,
                "size": len(content),
                "status": "created"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file content"""
        path = params['path']
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "path": path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents"""
        path = params['path']
        
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                items.append({
                    "name": item,
                    "path": item_path,
                    "is_directory": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            return {
                "success": True,
                "path": path,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_clipboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get clipboard content"""
        try:
            command = "Get-Clipboard"
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "content": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def set_clipboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set clipboard content"""
        text = params['text']
        
        try:
            command = f'Set-Clipboard -Value "{text}"'
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "status": "clipboard_set" if result.returncode == 0 else "failed",
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    server = WindowsOSServer()
    server.run()

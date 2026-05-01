import subprocess
import os
import logging
from typing import Optional
from .claude_client import ClaudeClient
from .security import SecureCommandExecutor, SecurityError

class ConversationalCommandHandler:
    def __init__(self, watch_folder: str):
        self.watch_folder = watch_folder
        self.claude_client = ClaudeClient()
        self.secure_executor = SecureCommandExecutor(work_directory=watch_folder, allowed_sudo=False)
        self.logger = logging.getLogger(__name__)
    
    def execute_conversational_command(self, natural_command: str) -> Optional[str]:
        """Convert natural language to shell command and execute it"""
        try:
            # Prompt Claude to convert natural language to shell command
            prompt = f"""Convert this natural language command to a shell command:
"{natural_command}"

Context: Working directory is {self.watch_folder}

Return ONLY the shell command, no explanation. Examples:
"find the number of images in the images folder" -> find Images -type f \\( -iname "*.jpg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" \\) | wc -l
"check disk usage" -> du -sh
"list recent files" -> ls -lt | head -10
"show folder sizes" -> du -h --max-depth=1 | sort -hr

Shell command:"""

            shell_command = self.claude_client.call(prompt, sanitize=False)
            if not shell_command:
                return "Error: Could not interpret command - AI API call failed"
            
            # Clean the response
            shell_command = shell_command.strip().replace('```', '').replace('bash', '').strip()
            
            # Execute the shell command securely
            try:
                result = self.secure_executor.execute_command(shell_command, timeout=30)
                
                if result['success']:
                    output = result['stdout'].strip()
                    return f"Command: {shell_command}\nResult:\n{output}" if output else f"Command executed: {shell_command}"
                else:
                    return f"Command failed: {shell_command}\nError: {result['stderr'].strip()}"
                    
            except SecurityError as e:
                self.logger.warning(f"Security violation blocked: {e}")
                return f"Command blocked for security reasons: {e}"
                
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return f"Error executing command: {e}"
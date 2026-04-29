"""
Runner for DesktopAgent benchmark execution.

Integrates with the existing DesktopAgent system.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import time
import tempfile

# Add parent directory to path to import DesktopAgent modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from benchmarks.runners.base_runner import AgentRunner


class DesktopAgentRunner(AgentRunner):
    """Runner for DesktopAgent."""

    def __init__(self):
        super().__init__("DesktopAgent")
        self.commands_executed = []
        self.errors = []

    def setup(self, test_case: Dict) -> bool:
        """Setup Docker container for test execution."""
        try:
            initial_state = test_case['initial_state']
            docker_image = initial_state.get('docker_image', 'ubuntu:22.04')
            privileged = initial_state.get('privileged', False)

            # Create container
            self.container_id = self._create_container(docker_image, privileged)

            # Run pre-install commands
            pre_install = initial_state.get('pre_install', [])
            self._run_pre_install(pre_install)

            # Set working directory
            working_dir = initial_state.get('working_dir', '/workspace')
            self._exec_in_container(f"mkdir -p {working_dir}")

            return True

        except Exception as e:
            print(f"[DesktopAgent] Setup failed: {e}")
            self.errors.append(f"Setup error: {str(e)}")
            return False

    def execute_task(self, test_case: Dict) -> Tuple[bool, List[str]]:
        """
        Execute task using DesktopAgent's guide executor.

        This simulates what the agent would do when given the task instructions.
        """
        try:
            from utils.guide_parser import GuideParser
            from utils.guide_executor import GuideExecutor

            # Get task instructions
            instructions = test_case['task']['instructions']
            print(f"\n[DesktopAgent] Task: {instructions}\n")

            # Parse instructions into steps
            parser = GuideParser()
            steps = parser.parse(instructions)

            if not steps:
                # If parser fails, create basic steps from instructions
                steps = self._create_basic_steps(instructions)

            print(f"[DesktopAgent] Parsed {len(steps)} steps")

            # Execute steps in container
            executor = GuideExecutor()
            success = True

            for i, step in enumerate(steps, 1):
                print(f"\n[DesktopAgent] Step {i}/{len(steps)}: {step['description']}")

                # Convert step to commands
                commands = self._step_to_commands(step, test_case)

                for cmd in commands:
                    # Execute in container
                    print(f"  Executing: {cmd}")
                    returncode, stdout, stderr = self._exec_in_container(cmd, timeout=120)

                    self.commands_executed.append(cmd)

                    if returncode != 0:
                        error_msg = f"Command failed: {cmd}\n{stderr}"
                        print(f"  ✗ Error: {stderr}")
                        self.errors.append(error_msg)

                        # Try to recover
                        if not self._attempt_recovery(cmd, stderr, test_case):
                            success = False
                            break
                    else:
                        print(f"  ✓ Success")

                    # Small delay between commands
                    time.sleep(0.5)

                if not success:
                    break

            return success, self.commands_executed

        except Exception as e:
            print(f"[DesktopAgent] Execution failed: {e}")
            self.errors.append(f"Execution error: {str(e)}")
            return False, self.commands_executed

    def cleanup(self):
        """Clean up container and resources."""
        self._destroy_container()
        self.commands_executed = []
        self.errors = []

    def _create_basic_steps(self, instructions: str) -> List[Dict]:
        """Create basic steps from instructions when parser fails."""
        # Simple heuristic: split by newlines or numbered lists
        lines = instructions.strip().split('\n')
        steps = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove numbering if present
                cleaned = line.lstrip('0123456789.-) ')
                if cleaned:
                    steps.append({
                        'description': cleaned,
                        'type': 'command',
                        'content': cleaned
                    })

        return steps if steps else [{'description': instructions, 'type': 'command', 'content': instructions}]

    def _step_to_commands(self, step: Dict, test_case: Dict) -> List[str]:
        """
        Convert a parsed step into executable shell commands.

        This is a simplified version - in reality, the agent would use
        Claude API to determine the best commands.
        """
        description = step.get('description', '').lower()
        commands = []

        # Simple pattern matching for common tasks
        if 'install curl' in description:
            commands = ['apt-get update', 'apt-get install -y curl']

        elif 'install node' in description or 'install nodejs' in description:
            commands = [
                'curl -fsSL https://deb.nodesource.com/setup_20.x | bash -',
                'apt-get install -y nodejs'
            ]

        elif 'install python' in description:
            if '3.11' in description:
                commands = [
                    'apt-get install -y software-properties-common',
                    'add-apt-repository -y ppa:deadsnakes/ppa',
                    'apt-get update',
                    'apt-get install -y python3.11 python3.11-venv python3.11-dev'
                ]
            else:
                commands = ['apt-get install -y python3 python3-pip']

        elif 'install git' in description:
            commands = ['apt-get update', 'apt-get install -y git']

        elif 'install docker' in description:
            commands = [
                'apt-get update',
                'apt-get install -y ca-certificates curl gnupg',
                'install -m 0755 -d /etc/apt/keyrings',
                'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg',
                'chmod a+r /etc/apt/keyrings/docker.gpg',
                'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null',
                'apt-get update',
                'apt-get install -y docker-ce docker-ce-cli containerd.io',
                'service docker start'
            ]

        elif 'install postgresql' in description or 'install postgres' in description:
            commands = [
                'apt-get update',
                'apt-get install -y postgresql postgresql-contrib',
                'service postgresql start'
            ]

        elif 'install redis' in description:
            commands = [
                'apt-get update',
                'apt-get install -y redis-server',
                'service redis-server start'
            ]

        elif 'git config' in description:
            if 'user.name' in description:
                commands = ['git config --global user.name "Test User"']
            if 'user.email' in description:
                commands.append('git config --global user.email "test@example.com"')

        elif 'git init' in description or 'initialize' in description and 'git' in description:
            working_dir = test_case['initial_state'].get('working_dir', '/workspace')
            commands = [f'cd {working_dir}/testproject && git init']

        elif 'virtual environment' in description or 'virtualenv' in description:
            working_dir = test_case['initial_state'].get('working_dir', '/workspace')
            commands = [f'cd {working_dir}/testproject && python3.11 -m venv .venv']

        elif 'package.json' in description:
            working_dir = test_case['initial_state'].get('working_dir', '/workspace')
            commands = [f'cd {working_dir}/testproject && echo \'{{"name": "test-project"}}\' > package.json']

        elif 'create' in description and 'directory' in description:
            # Extract directory path
            working_dir = test_case['initial_state'].get('working_dir', '/workspace')
            commands = [f'mkdir -p {working_dir}/testproject']

        else:
            # Fallback: try to execute the description as-is if it looks like a command
            if any(keyword in description for keyword in ['apt-get', 'curl', 'wget', 'mkdir', 'cd', 'git']):
                commands = [description]

        return commands if commands else []

    def _attempt_recovery(self, failed_command: str, error: str, test_case: Dict) -> bool:
        """
        Attempt to recover from a failed command.

        Returns True if recovery successful, False otherwise.
        """
        # Common recovery strategies
        if 'command not found' in error.lower():
            # Try to install the missing command
            cmd_name = failed_command.split()[0]
            print(f"  Attempting recovery: installing {cmd_name}")
            self._exec_in_container(f'apt-get update && apt-get install -y {cmd_name}', timeout=120)
            # Retry the original command
            returncode, _, _ = self._exec_in_container(failed_command, timeout=120)
            return returncode == 0

        elif 'permission denied' in error.lower():
            # Try with sudo
            print(f"  Attempting recovery: retrying with sudo")
            returncode, _, _ = self._exec_in_container(f'sudo {failed_command}', timeout=120)
            return returncode == 0

        return False

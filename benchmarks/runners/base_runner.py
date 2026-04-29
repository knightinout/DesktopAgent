"""
Base runner interface for benchmark agents.

All agent runners should inherit from AgentRunner.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from pathlib import Path
import subprocess
import time


class AgentRunner(ABC):
    """Abstract base class for agent runners."""

    def __init__(self, name: str):
        self.name = name
        self.container_id = None

    @abstractmethod
    def setup(self, test_case: Dict) -> bool:
        """
        Setup the environment for a test case.

        Args:
            test_case: Test case configuration

        Returns:
            True if setup successful, False otherwise
        """
        pass

    @abstractmethod
    def execute_task(self, test_case: Dict) -> Tuple[bool, List[str]]:
        """
        Execute the task using the agent.

        Args:
            test_case: Test case configuration

        Returns:
            Tuple of (success, list of commands executed)
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up resources after task execution."""
        pass

    def _create_container(self, docker_image: str, privileged: bool = False) -> str:
        """
        Create a Docker container for testing.

        Args:
            docker_image: Base Docker image to use
            privileged: Whether to run in privileged mode

        Returns:
            Container ID
        """
        privileged_flag = "--privileged" if privileged else ""
        cmd = f"docker run -d {privileged_flag} --rm {docker_image} tail -f /dev/null"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create container: {result.stderr}")

        container_id = result.stdout.strip()
        print(f"[Runner] Created container: {container_id[:12]}")
        return container_id

    def _exec_in_container(self, command: str, timeout: int = 60) -> Tuple[int, str, str]:
        """
        Execute a command in the container.

        Args:
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.container_id:
            raise RuntimeError("No container running")

        cmd = f"docker exec {self.container_id} bash -c '{command}'"

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"

    def _run_pre_install(self, pre_install_commands: List[str]):
        """Run pre-installation commands."""
        for cmd in pre_install_commands:
            print(f"[Runner] Pre-install: {cmd}")
            returncode, stdout, stderr = self._exec_in_container(cmd, timeout=300)
            if returncode != 0:
                print(f"[Runner] Warning: Pre-install command failed: {stderr}")

    def _destroy_container(self):
        """Destroy the test container."""
        if self.container_id:
            subprocess.run(f"docker stop {self.container_id}", shell=True, capture_output=True)
            print(f"[Runner] Destroyed container: {self.container_id[:12]}")
            self.container_id = None

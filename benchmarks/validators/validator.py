"""
Validation system for benchmark test cases.

Runs validation commands and checks success criteria.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
import os


class TaskValidator:
    """Validates task completion against defined criteria."""

    def __init__(self, container_id: str = None):
        """
        Initialize validator.

        Args:
            container_id: Docker container ID to run validation commands in.
                         If None, runs commands locally.
        """
        self.container_id = container_id

    def validate_task(self, validation_config: Dict) -> Tuple[bool, Dict[str, bool], List[str]]:
        """
        Validate a completed task against its validation criteria.

        Args:
            validation_config: Validation configuration from test case JSON

        Returns:
            Tuple of (overall_success, validation_results, failure_reasons)
        """
        results = {}
        failures = []

        # Validate commands
        if 'commands' in validation_config:
            for i, cmd in enumerate(validation_config['commands']):
                expected = validation_config.get('expected_outputs', [])[i] if i < len(validation_config.get('expected_outputs', [])) else None
                success, output = self._run_validation_command(cmd, expected)
                results[f"command_{i}_{cmd[:30]}"] = success
                if not success:
                    failures.append(f"Command failed: {cmd}")

        # Validate files exist
        if 'files_must_exist' in validation_config:
            for file_path in validation_config['files_must_exist']:
                exists = self._check_file_exists(file_path)
                results[f"file_exists_{file_path}"] = exists
                if not exists:
                    failures.append(f"Required file missing: {file_path}")

        # Validate services running
        if 'services_running' in validation_config:
            for service in validation_config['services_running']:
                running = self._check_service_running(service)
                results[f"service_{service}"] = running
                if not running:
                    failures.append(f"Service not running: {service}")

        overall_success = all(results.values()) if results else False
        return overall_success, results, failures

    def _run_validation_command(self, command: str, expected_output: str = None) -> Tuple[bool, str]:
        """
        Run a validation command and check its output.

        Args:
            command: Shell command to execute
            expected_output: Expected substring in output (optional)

        Returns:
            Tuple of (success, output)
        """
        try:
            if self.container_id:
                full_cmd = f"docker exec {self.container_id} bash -c '{command}'"
            else:
                full_cmd = command

            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            # Check expected output if provided
            if success and expected_output:
                success = expected_output in output

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        cmd = f"test -f {file_path} || test -d {file_path}"
        success, _ = self._run_validation_command(cmd)
        return success

    def _check_service_running(self, service_name: str) -> bool:
        """Check if a service is running."""
        # Try systemctl first, then service command
        cmd = f"systemctl is-active {service_name} 2>/dev/null || service {service_name} status 2>/dev/null"
        success, output = self._run_validation_command(cmd)
        return success or 'running' in output.lower()


def load_test_case(test_case_path: Path) -> Dict:
    """Load a test case from JSON file."""
    with open(test_case_path, 'r') as f:
        return json.load(f)


def validate_test_case_format(test_case: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that a test case has all required fields.

    Args:
        test_case: Test case dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    required_fields = {
        'id': str,
        'name': str,
        'difficulty': str,
        'category': str,
        'description': str,
        'initial_state': dict,
        'task': dict,
        'validation': dict,
        'metrics': dict,
        'metadata': dict
    }

    errors = []

    for field, expected_type in required_fields.items():
        if field not in test_case:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(test_case[field], expected_type):
            errors.append(f"Field '{field}' must be of type {expected_type.__name__}")

    # Validate difficulty level
    if test_case.get('difficulty') not in ['basic', 'intermediate', 'advanced']:
        errors.append("Difficulty must be 'basic', 'intermediate', or 'advanced'")

    # Validate category
    valid_categories = ['installation', 'configuration', 'debugging', 'workflow']
    if test_case.get('category') not in valid_categories:
        errors.append(f"Category must be one of: {', '.join(valid_categories)}")

    return len(errors) == 0, errors

"""
Metrics collection for DesktopAgent benchmark suite.

Tracks and records performance metrics during agent execution.
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class TaskMetrics:
    """Metrics for a single task execution."""
    task_id: str
    task_name: str
    difficulty: str

    # Execution metrics
    success: bool
    execution_time_seconds: float
    commands_executed: int
    errors_encountered: int
    retries_attempted: int

    # Safety metrics
    dangerous_commands_blocked: int
    validation_failures: List[str]

    # Efficiency metrics
    expected_commands_range: List[int]
    efficiency_score: float  # ratio of commands used vs expected

    # Timestamps
    start_time: str
    end_time: str

    # Additional context
    error_messages: List[str]
    validation_results: Dict[str, bool]
    agent_name: str


@dataclass
class BenchmarkRun:
    """Complete benchmark run results."""
    run_id: str
    agent_name: str
    start_time: str
    end_time: str
    total_duration_seconds: float

    # Overall metrics
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float

    # Aggregated metrics
    avg_execution_time: float
    avg_commands_per_task: float
    avg_efficiency_score: float
    total_errors: int
    total_retries: int

    # Per-difficulty breakdown
    difficulty_breakdown: Dict[str, Dict[str, Any]]

    # Individual task results
    task_results: List[TaskMetrics]

    # Configuration
    test_cases_used: List[str]
    environment: Dict[str, str]


class MetricsCollector:
    """Collects and aggregates metrics during benchmark execution."""

    def __init__(self, agent_name: str, run_id: Optional[str] = None):
        self.agent_name = agent_name
        self.run_id = run_id or f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.task_results: List[TaskMetrics] = []
        self.start_time = None
        self.current_task_start = None
        self.current_task_metrics = {}

    def start_benchmark(self):
        """Mark the start of a benchmark run."""
        self.start_time = datetime.now()
        print(f"[Metrics] Starting benchmark run: {self.run_id}")

    def start_task(self, task_id: str, task_name: str, difficulty: str,
                   expected_commands_range: List[int]):
        """Start tracking a new task."""
        self.current_task_start = time.time()
        self.current_task_metrics = {
            'task_id': task_id,
            'task_name': task_name,
            'difficulty': difficulty,
            'expected_commands_range': expected_commands_range,
            'commands_executed': 0,
            'errors_encountered': 0,
            'retries_attempted': 0,
            'dangerous_commands_blocked': 0,
            'validation_failures': [],
            'error_messages': [],
            'validation_results': {},
            'start_time': datetime.now().isoformat()
        }
        print(f"[Metrics] Starting task: {task_id} ({difficulty})")

    def record_command(self):
        """Increment command counter."""
        self.current_task_metrics['commands_executed'] += 1

    def record_error(self, error_message: str):
        """Record an error during task execution."""
        self.current_task_metrics['errors_encountered'] += 1
        self.current_task_metrics['error_messages'].append(error_message)

    def record_retry(self):
        """Record a retry attempt."""
        self.current_task_metrics['retries_attempted'] += 1

    def record_blocked_command(self):
        """Record a dangerous command that was blocked."""
        self.current_task_metrics['dangerous_commands_blocked'] += 1

    def record_validation_failure(self, failure_reason: str):
        """Record a validation failure."""
        self.current_task_metrics['validation_failures'].append(failure_reason)

    def end_task(self, success: bool, validation_results: Dict[str, bool]):
        """Complete tracking for current task."""
        if self.current_task_start is None:
            raise ValueError("No task in progress")

        execution_time = time.time() - self.current_task_start
        self.current_task_metrics['execution_time_seconds'] = execution_time
        self.current_task_metrics['success'] = success
        self.current_task_metrics['validation_results'] = validation_results
        self.current_task_metrics['end_time'] = datetime.now().isoformat()
        self.current_task_metrics['agent_name'] = self.agent_name

        # Calculate efficiency score
        commands = self.current_task_metrics['commands_executed']
        expected_range = self.current_task_metrics['expected_commands_range']
        expected_avg = sum(expected_range) / len(expected_range)
        efficiency = expected_avg / max(commands, 1) if commands > 0 else 0
        self.current_task_metrics['efficiency_score'] = min(efficiency, 1.0)

        # Create TaskMetrics object
        task_metrics = TaskMetrics(**self.current_task_metrics)
        self.task_results.append(task_metrics)

        status = "✓ PASS" if success else "✗ FAIL"
        print(f"[Metrics] Task completed: {task_metrics.task_id} {status} "
              f"({execution_time:.2f}s, {commands} commands)")

        self.current_task_start = None
        self.current_task_metrics = {}

    def generate_report(self, output_dir: Path) -> BenchmarkRun:
        """Generate final benchmark report."""
        if self.start_time is None:
            raise ValueError("Benchmark not started")

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # Calculate overall metrics
        total_tasks = len(self.task_results)
        successful_tasks = sum(1 for t in self.task_results if t.success)
        failed_tasks = total_tasks - successful_tasks
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0

        # Calculate averages
        avg_execution_time = sum(t.execution_time_seconds for t in self.task_results) / total_tasks if total_tasks > 0 else 0
        avg_commands = sum(t.commands_executed for t in self.task_results) / total_tasks if total_tasks > 0 else 0
        avg_efficiency = sum(t.efficiency_score for t in self.task_results) / total_tasks if total_tasks > 0 else 0
        total_errors = sum(t.errors_encountered for t in self.task_results)
        total_retries = sum(t.retries_attempted for t in self.task_results)

        # Breakdown by difficulty
        difficulty_breakdown = {}
        for difficulty in ['basic', 'intermediate', 'advanced']:
            tasks = [t for t in self.task_results if t.difficulty == difficulty]
            if tasks:
                difficulty_breakdown[difficulty] = {
                    'total': len(tasks),
                    'successful': sum(1 for t in tasks if t.success),
                    'success_rate': sum(1 for t in tasks if t.success) / len(tasks),
                    'avg_time': sum(t.execution_time_seconds for t in tasks) / len(tasks),
                    'avg_commands': sum(t.commands_executed for t in tasks) / len(tasks)
                }

        # Create benchmark run report
        benchmark_run = BenchmarkRun(
            run_id=self.run_id,
            agent_name=self.agent_name,
            start_time=self.start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration_seconds=duration,
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            success_rate=success_rate,
            avg_execution_time=avg_execution_time,
            avg_commands_per_task=avg_commands,
            avg_efficiency_score=avg_efficiency,
            total_errors=total_errors,
            total_retries=total_retries,
            difficulty_breakdown=difficulty_breakdown,
            task_results=self.task_results,
            test_cases_used=[t.task_id for t in self.task_results],
            environment={
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
        )

        # Save to file
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{self.run_id}_report.json"

        with open(report_path, 'w') as f:
            json.dump(asdict(benchmark_run), f, indent=2)

        print(f"\n[Metrics] Benchmark complete: {self.run_id}")
        print(f"  Total tasks: {total_tasks}")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Avg execution time: {avg_execution_time:.2f}s")
        print(f"  Report saved: {report_path}")

        return benchmark_run

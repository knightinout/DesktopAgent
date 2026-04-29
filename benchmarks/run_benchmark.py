#!/usr/bin/env python3
"""
Main benchmark execution script.

Usage:
    python benchmarks/run_benchmark.py --agent desktopagent
    python benchmarks/run_benchmark.py --agent desktopagent --level basic
    python benchmarks/run_benchmark.py --agent desktopagent --test-case basic/install_curl.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.runners.desktop_agent_runner import DesktopAgentRunner
from benchmarks.metrics.collector import MetricsCollector
from benchmarks.validators.validator import TaskValidator, load_test_case, validate_test_case_format


def find_test_cases(level: str = None, test_case: str = None) -> List[Path]:
    """
    Find test cases to run.

    Args:
        level: Difficulty level (basic, intermediate, advanced) or None for all
        test_case: Specific test case path or None for all in level

    Returns:
        List of test case file paths
    """
    base_dir = Path(__file__).parent / 'test_cases'

    if test_case:
        # Specific test case
        path = base_dir / test_case
        if not path.exists():
            print(f"Error: Test case not found: {path}")
            return []
        return [path]

    # Find all test cases for level(s)
    test_cases = []
    levels = [level] if level else ['basic', 'intermediate', 'advanced']

    for lvl in levels:
        level_dir = base_dir / lvl
        if level_dir.exists():
            test_cases.extend(level_dir.glob('*.json'))

    return sorted(test_cases)


def run_benchmark(agent_name: str, test_cases: List[Path], verbose: bool = False):
    """
    Run benchmark suite.

    Args:
        agent_name: Name of agent to test
        test_cases: List of test case files
        verbose: Whether to print verbose output
    """
    # Initialize components
    if agent_name.lower() == 'desktopagent':
        runner = DesktopAgentRunner()
    else:
        print(f"Error: Unknown agent '{agent_name}'")
        print("Supported agents: desktopagent")
        return

    metrics = MetricsCollector(agent_name)
    metrics.start_benchmark()

    print(f"\n{'='*70}")
    print(f"  DesktopAgent Benchmark Suite")
    print(f"  Agent: {agent_name}")
    print(f"  Test cases: {len(test_cases)}")
    print(f"{'='*70}\n")

    # Run each test case
    for i, test_case_path in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Running: {test_case_path.name}")
        print("-" * 70)

        try:
            # Load and validate test case
            test_case = load_test_case(test_case_path)
            is_valid, errors = validate_test_case_format(test_case)

            if not is_valid:
                print(f"✗ Invalid test case format:")
                for error in errors:
                    print(f"  - {error}")
                continue

            # Start metrics tracking
            metrics.start_task(
                test_case['id'],
                test_case['name'],
                test_case['difficulty'],
                test_case['metrics']['expected_commands_range']
            )

            # Setup environment
            print(f"Setting up environment...")
            if not runner.setup(test_case):
                print(f"✗ Setup failed")
                metrics.record_error("Setup failed")
                metrics.end_task(False, {})
                runner.cleanup()
                continue

            # Execute task
            print(f"Executing task...")
            success, commands = runner.execute_task(test_case)

            # Record commands
            for _ in commands:
                metrics.record_command()

            # Validate results
            print(f"Validating results...")
            validator = TaskValidator(runner.container_id)
            validation_success, validation_results, failures = validator.validate_task(
                test_case['validation']
            )

            # Record failures
            for failure in failures:
                metrics.record_validation_failure(failure)

            # Determine overall success
            overall_success = success and validation_success

            if overall_success:
                print(f"✓ PASS: {test_case['name']}")
            else:
                print(f"✗ FAIL: {test_case['name']}")
                if failures:
                    print(f"  Validation failures:")
                    for failure in failures:
                        print(f"    - {failure}")

            # End task metrics
            metrics.end_task(overall_success, validation_results)

        except Exception as e:
            print(f"✗ ERROR: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            metrics.record_error(str(e))
            metrics.end_task(False, {})

        finally:
            # Cleanup
            runner.cleanup()

    # Generate report
    print(f"\n{'='*70}")
    print(f"  Generating Report")
    print(f"{'='*70}\n")

    results_dir = Path(__file__).parent / 'results'
    report = metrics.generate_report(results_dir)

    # Print summary
    print_summary(report)


def print_summary(report):
    """Print benchmark summary."""
    print(f"\n{'='*70}")
    print(f"  BENCHMARK SUMMARY")
    print(f"{'='*70}\n")

    print(f"Agent: {report.agent_name}")
    print(f"Run ID: {report.run_id}")
    print(f"Duration: {report.total_duration_seconds:.2f}s\n")

    print(f"Overall Results:")
    print(f"  Total tasks: {report.total_tasks}")
    print(f"  Successful: {report.successful_tasks} ({report.success_rate:.1%})")
    print(f"  Failed: {report.failed_tasks}")
    print(f"  Avg time: {report.avg_execution_time:.2f}s")
    print(f"  Avg commands: {report.avg_commands_per_task:.1f}")
    print(f"  Efficiency score: {report.avg_efficiency_score:.2f}")
    print(f"  Total errors: {report.total_errors}")
    print(f"  Total retries: {report.total_retries}\n")

    if report.difficulty_breakdown:
        print(f"By Difficulty:")
        for difficulty, stats in report.difficulty_breakdown.items():
            print(f"  {difficulty.capitalize()}:")
            print(f"    Success rate: {stats['success_rate']:.1%} ({stats['successful']}/{stats['total']})")
            print(f"    Avg time: {stats['avg_time']:.2f}s")
            print(f"    Avg commands: {stats['avg_commands']:.1f}")

    print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description='Run DesktopAgent benchmark suite')
    parser.add_argument('--agent', required=True, help='Agent to test (desktopagent)')
    parser.add_argument('--level', choices=['basic', 'intermediate', 'advanced'],
                       help='Difficulty level to test')
    parser.add_argument('--test-case', help='Specific test case to run (e.g., basic/install_curl.json)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Find test cases
    test_cases = find_test_cases(args.level, args.test_case)

    if not test_cases:
        print("No test cases found!")
        sys.exit(1)

    # Run benchmark
    run_benchmark(args.agent, test_cases, args.verbose)


if __name__ == '__main__':
    main()

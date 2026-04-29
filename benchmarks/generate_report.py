#!/usr/bin/env python3
"""
Generate comparative reports from benchmark results.

Usage:
    python benchmarks/generate_report.py --results results/desktopagent_20260127_120000_report.json
    python benchmarks/generate_report.py --compare results/agent1.json results/agent2.json
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def load_report(report_path: Path) -> Dict:
    """Load a benchmark report from JSON."""
    with open(report_path, 'r') as f:
        return json.load(f)


def generate_single_report(report: Dict, output_format: str = 'text'):
    """Generate a detailed report for a single benchmark run."""
    if output_format == 'text':
        return _generate_text_report(report)
    elif output_format == 'markdown':
        return _generate_markdown_report(report)
    elif output_format == 'html':
        return _generate_html_report(report)
    else:
        raise ValueError(f"Unknown format: {output_format}")


def _generate_text_report(report: Dict) -> str:
    """Generate a text format report."""
    lines = []
    lines.append("="*80)
    lines.append(f"  DESKTOP AGENT BENCHMARK REPORT")
    lines.append("="*80)
    lines.append("")
    lines.append(f"Agent: {report['agent_name']}")
    lines.append(f"Run ID: {report['run_id']}")
    lines.append(f"Start Time: {report['start_time']}")
    lines.append(f"Duration: {report['total_duration_seconds']:.2f}s")
    lines.append("")
    lines.append("-"*80)
    lines.append("OVERALL RESULTS")
    lines.append("-"*80)
    lines.append(f"Total Tasks: {report['total_tasks']}")
    lines.append(f"Successful: {report['successful_tasks']} ({report['success_rate']*100:.1f}%)")
    lines.append(f"Failed: {report['failed_tasks']}")
    lines.append(f"Average Execution Time: {report['avg_execution_time']:.2f}s")
    lines.append(f"Average Commands per Task: {report['avg_commands_per_task']:.1f}")
    lines.append(f"Average Efficiency Score: {report['avg_efficiency_score']:.2f}")
    lines.append(f"Total Errors: {report['total_errors']}")
    lines.append(f"Total Retries: {report['total_retries']}")
    lines.append("")

    if report['difficulty_breakdown']:
        lines.append("-"*80)
        lines.append("BREAKDOWN BY DIFFICULTY")
        lines.append("-"*80)
        for difficulty, stats in report['difficulty_breakdown'].items():
            lines.append(f"\n{difficulty.upper()}:")
            lines.append(f"  Tasks: {stats['total']}")
            lines.append(f"  Success Rate: {stats['success_rate']*100:.1f}% ({stats['successful']}/{stats['total']})")
            lines.append(f"  Avg Time: {stats['avg_time']:.2f}s")
            lines.append(f"  Avg Commands: {stats['avg_commands']:.1f}")

    lines.append("")
    lines.append("-"*80)
    lines.append("DETAILED TASK RESULTS")
    lines.append("-"*80)

    for task in report['task_results']:
        status = "✓ PASS" if task['success'] else "✗ FAIL"
        lines.append(f"\n{status} {task['task_name']} ({task['difficulty']})")
        lines.append(f"  Task ID: {task['task_id']}")
        lines.append(f"  Time: {task['execution_time_seconds']:.2f}s")
        lines.append(f"  Commands: {task['commands_executed']}")
        lines.append(f"  Efficiency: {task['efficiency_score']:.2f}")

        if task['errors_encountered'] > 0:
            lines.append(f"  Errors: {task['errors_encountered']}")
            if task['error_messages']:
                for error in task['error_messages'][:3]:  # Show first 3 errors
                    lines.append(f"    - {error[:100]}")

        if task['validation_failures']:
            lines.append(f"  Validation Failures:")
            for failure in task['validation_failures']:
                lines.append(f"    - {failure}")

    lines.append("")
    lines.append("="*80)

    return "\n".join(lines)


def _generate_markdown_report(report: Dict) -> str:
    """Generate a markdown format report."""
    lines = []
    lines.append(f"# Desktop Agent Benchmark Report")
    lines.append(f"")
    lines.append(f"**Agent:** {report['agent_name']}  ")
    lines.append(f"**Run ID:** `{report['run_id']}`  ")
    lines.append(f"**Start Time:** {report['start_time']}  ")
    lines.append(f"**Duration:** {report['total_duration_seconds']:.2f}s  ")
    lines.append(f"")
    lines.append(f"## Overall Results")
    lines.append(f"")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Tasks | {report['total_tasks']} |")
    lines.append(f"| Successful | {report['successful_tasks']} ({report['success_rate']*100:.1f}%) |")
    lines.append(f"| Failed | {report['failed_tasks']} |")
    lines.append(f"| Avg Execution Time | {report['avg_execution_time']:.2f}s |")
    lines.append(f"| Avg Commands/Task | {report['avg_commands_per_task']:.1f} |")
    lines.append(f"| Avg Efficiency Score | {report['avg_efficiency_score']:.2f} |")
    lines.append(f"| Total Errors | {report['total_errors']} |")
    lines.append(f"| Total Retries | {report['total_retries']} |")
    lines.append(f"")

    if report['difficulty_breakdown']:
        lines.append(f"## Breakdown by Difficulty")
        lines.append(f"")
        lines.append(f"| Difficulty | Tasks | Success Rate | Avg Time | Avg Commands |")
        lines.append(f"|------------|-------|--------------|----------|--------------|")
        for difficulty, stats in report['difficulty_breakdown'].items():
            lines.append(f"| {difficulty.capitalize()} | {stats['total']} | {stats['success_rate']*100:.1f}% | {stats['avg_time']:.2f}s | {stats['avg_commands']:.1f} |")

    lines.append(f"")
    lines.append(f"## Detailed Task Results")
    lines.append(f"")

    for task in report['task_results']:
        status_icon = "✅" if task['success'] else "❌"
        lines.append(f"### {status_icon} {task['task_name']}")
        lines.append(f"")
        lines.append(f"- **Difficulty:** {task['difficulty']}")
        lines.append(f"- **Time:** {task['execution_time_seconds']:.2f}s")
        lines.append(f"- **Commands:** {task['commands_executed']}")
        lines.append(f"- **Efficiency:** {task['efficiency_score']:.2f}")

        if task['errors_encountered'] > 0:
            lines.append(f"- **Errors:** {task['errors_encountered']}")

        if task['validation_failures']:
            lines.append(f"- **Validation Failures:**")
            for failure in task['validation_failures']:
                lines.append(f"  - {failure}")

        lines.append(f"")

    return "\n".join(lines)


def _generate_html_report(report: Dict) -> str:
    """Generate an HTML format report."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Benchmark Report - {report['agent_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .metric {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Desktop Agent Benchmark Report</h1>

    <h2>Run Information</h2>
    <table>
        <tr><td><strong>Agent</strong></td><td>{report['agent_name']}</td></tr>
        <tr><td><strong>Run ID</strong></td><td>{report['run_id']}</td></tr>
        <tr><td><strong>Start Time</strong></td><td>{report['start_time']}</td></tr>
        <tr><td><strong>Duration</strong></td><td>{report['total_duration_seconds']:.2f}s</td></tr>
    </table>

    <h2>Overall Results</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total Tasks</td><td>{report['total_tasks']}</td></tr>
        <tr><td>Successful</td><td class="success">{report['successful_tasks']} ({report['success_rate']*100:.1f}%)</td></tr>
        <tr><td>Failed</td><td class="failure">{report['failed_tasks']}</td></tr>
        <tr><td>Avg Execution Time</td><td>{report['avg_execution_time']:.2f}s</td></tr>
        <tr><td>Avg Commands/Task</td><td>{report['avg_commands_per_task']:.1f}</td></tr>
        <tr><td>Avg Efficiency Score</td><td>{report['avg_efficiency_score']:.2f}</td></tr>
    </table>

    <h2>Task Results</h2>
    <table>
        <tr><th>Status</th><th>Task</th><th>Difficulty</th><th>Time</th><th>Commands</th><th>Efficiency</th></tr>
"""

    for task in report['task_results']:
        status_class = "success" if task['success'] else "failure"
        status_text = "✓ PASS" if task['success'] else "✗ FAIL"
        html += f"""
        <tr>
            <td class="{status_class}">{status_text}</td>
            <td>{task['task_name']}</td>
            <td>{task['difficulty']}</td>
            <td>{task['execution_time_seconds']:.2f}s</td>
            <td>{task['commands_executed']}</td>
            <td>{task['efficiency_score']:.2f}</td>
        </tr>
"""

    html += """
    </table>
</body>
</html>
"""
    return html


def generate_comparison_report(reports: List[Dict], output_format: str = 'text') -> str:
    """Generate a comparative report for multiple agents."""
    if output_format == 'markdown':
        return _generate_comparison_markdown(reports)
    else:
        return _generate_comparison_text(reports)


def _generate_comparison_text(reports: List[Dict]) -> str:
    """Generate text comparison report."""
    lines = []
    lines.append("="*80)
    lines.append("  AGENT COMPARISON REPORT")
    lines.append("="*80)
    lines.append("")

    # Header
    agent_names = [r['agent_name'] for r in reports]
    lines.append(f"Comparing {len(reports)} agents: {', '.join(agent_names)}")
    lines.append("")

    # Overall comparison
    lines.append("-"*80)
    lines.append("OVERALL METRICS COMPARISON")
    lines.append("-"*80)
    lines.append(f"{'Metric':<30} " + " ".join(f"{name:>15}" for name in agent_names))
    lines.append("-"*80)

    metrics_to_compare = [
        ('Success Rate', lambda r: f"{r['success_rate']*100:.1f}%"),
        ('Avg Execution Time', lambda r: f"{r['avg_execution_time']:.2f}s"),
        ('Avg Commands/Task', lambda r: f"{r['avg_commands_per_task']:.1f}"),
        ('Avg Efficiency', lambda r: f"{r['avg_efficiency_score']:.2f}"),
        ('Total Errors', lambda r: str(r['total_errors'])),
        ('Total Retries', lambda r: str(r['total_retries']))
    ]

    for metric_name, formatter in metrics_to_compare:
        values = [formatter(r) for r in reports]
        lines.append(f"{metric_name:<30} " + " ".join(f"{v:>15}" for v in values))

    lines.append("")

    # Per-difficulty comparison
    for difficulty in ['basic', 'intermediate', 'advanced']:
        has_data = any(difficulty in r.get('difficulty_breakdown', {}) for r in reports)
        if has_data:
            lines.append(f"\n{difficulty.upper()} TASKS")
            lines.append("-"*80)
            lines.append(f"{'Metric':<30} " + " ".join(f"{name:>15}" for name in agent_names))
            lines.append("-"*80)

            # Success rate
            values = []
            for r in reports:
                if difficulty in r.get('difficulty_breakdown', {}):
                    sr = r['difficulty_breakdown'][difficulty]['success_rate']
                    values.append(f"{sr*100:.1f}%")
                else:
                    values.append("N/A")
            lines.append(f"{'Success Rate':<30} " + " ".join(f"{v:>15}" for v in values))

            # Avg time
            values = []
            for r in reports:
                if difficulty in r.get('difficulty_breakdown', {}):
                    t = r['difficulty_breakdown'][difficulty]['avg_time']
                    values.append(f"{t:.2f}s")
                else:
                    values.append("N/A")
            lines.append(f"{'Avg Time':<30} " + " ".join(f"{v:>15}" for v in values))

    lines.append("")
    lines.append("="*80)

    return "\n".join(lines)


def _generate_comparison_markdown(reports: List[Dict]) -> str:
    """Generate markdown comparison report."""
    lines = []
    lines.append("# Agent Comparison Report")
    lines.append("")

    agent_names = [r['agent_name'] for r in reports]
    lines.append(f"Comparing **{len(reports)}** agents: {', '.join(f'`{name}`' for name in agent_names)}")
    lines.append("")

    # Overall comparison table
    lines.append("## Overall Metrics Comparison")
    lines.append("")
    lines.append("| Metric | " + " | ".join(agent_names) + " |")
    lines.append("|--------|" + "|".join(["--------"] * len(reports)) + "|")

    metrics = [
        ('Success Rate', lambda r: f"{r['success_rate']*100:.1f}%"),
        ('Avg Time', lambda r: f"{r['avg_execution_time']:.2f}s"),
        ('Avg Commands', lambda r: f"{r['avg_commands_per_task']:.1f}"),
        ('Efficiency', lambda r: f"{r['avg_efficiency_score']:.2f}"),
        ('Errors', lambda r: str(r['total_errors'])),
        ('Retries', lambda r: str(r['total_retries']))
    ]

    for metric_name, formatter in metrics:
        values = [formatter(r) for r in reports]
        lines.append(f"| {metric_name} | " + " | ".join(values) + " |")

    lines.append("")

    # Winner summary
    lines.append("## Summary")
    lines.append("")
    best_success_rate = max(reports, key=lambda r: r['success_rate'])
    best_speed = min(reports, key=lambda r: r['avg_execution_time'])
    best_efficiency = max(reports, key=lambda r: r['avg_efficiency_score'])

    lines.append(f"- **Highest Success Rate:** `{best_success_rate['agent_name']}` ({best_success_rate['success_rate']*100:.1f}%)")
    lines.append(f"- **Fastest Execution:** `{best_speed['agent_name']}` ({best_speed['avg_execution_time']:.2f}s avg)")
    lines.append(f"- **Most Efficient:** `{best_efficiency['agent_name']}` ({best_efficiency['avg_efficiency_score']:.2f})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate benchmark reports')
    parser.add_argument('--results', nargs='+', required=True, help='Path(s) to benchmark result JSON files')
    parser.add_argument('--format', choices=['text', 'markdown', 'html'], default='text',
                       help='Output format')
    parser.add_argument('--output', help='Output file (default: stdout)')
    parser.add_argument('--compare', action='store_true',
                       help='Generate comparison report (requires multiple result files)')

    args = parser.parse_args()

    # Load reports
    reports = [load_report(Path(r)) for r in args.results]

    # Generate report
    if args.compare and len(reports) > 1:
        output = generate_comparison_report(reports, args.format)
    elif len(reports) == 1:
        output = generate_single_report(reports[0], args.format)
    else:
        print("Error: Need at least 2 reports for comparison or 1 report for single report")
        return

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()

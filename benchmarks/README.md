# DesktopAgent Benchmark Suite

SWE-bench-inspired evaluation framework for desktop automation agents.

## Overview

This benchmark suite evaluates AI agents on real-world software installation and configuration tasks. Inspired by SWE-bench, it provides:

- **Reproducible test environments** (Docker-based)
- **Measurable success criteria** (automated validation)
- **Difficulty tiers** (basic → intermediate → advanced)
- **Comparative metrics** (vs Claude Code, Comet, BrowserOS)

## Structure

```
benchmarks/
├── test_cases/          # Task definitions in JSON format
│   ├── basic/           # Simple installations (10-15 tasks)
│   ├── intermediate/    # Multi-step setups (15-20 tasks)
│   └── advanced/        # Complex environments (10-15 tasks)
├── validators/          # Automated validation scripts
├── runners/             # Agent execution wrappers
├── metrics/             # Metrics collection & analysis
└── results/             # Test run outputs
```

## Quick Start

```bash
# Run full benchmark suite
python benchmarks/run_benchmark.py --agent desktopagent

# Run specific difficulty level
python benchmarks/run_benchmark.py --agent desktopagent --level basic

# Compare against baseline
python benchmarks/run_benchmark.py --agent desktopagent --compare-baseline

# Generate report
python benchmarks/generate_report.py --results results/latest
```

## Test Case Format

Each test case defines:
- **Task description**: Natural language instructions
- **Initial state**: Starting environment (Docker image)
- **Success criteria**: Automated validation commands
- **Expected artifacts**: Files/services that should exist
- **Time limit**: Maximum execution time

## Metrics Tracked

- **Success Rate**: % of tasks completed successfully
- **Time to Completion**: Avg time per task
- **Commands Executed**: Efficiency metric
- **Error Recovery**: Ability to self-correct
- **Safety Score**: Avoidance of dangerous operations

## Adding New Test Cases

See `test_cases/TEMPLATE.json` for the format.

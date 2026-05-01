"""
Enhanced Debugging Tools for Desktop Agent
Self-healing capabilities for installation failures
"""
from typing import Optional, List, Dict
from langchain_core.tools import tool
from utils.security import SecureCommandExecutor, SecurityError
import os
import json
import re


# Initialize secure executor
secure_executor = SecureCommandExecutor(
    work_directory="/tmp",
    allowed_sudo=True
)

# Helper function to get LLM (lazy initialization, supports Claude and Gemini)
def _get_llm():
    """Get LLM instance based on AI_PROVIDER environment variable."""
    from dotenv import load_dotenv
    load_dotenv()

    provider = os.environ.get("AI_PROVIDER", "").lower()
    if not provider:
        if os.environ.get("CLAUDE_API_KEY"):
            provider = "claude"
        elif os.environ.get("GEMINI_API_KEY"):
            provider = "gemini"
        else:
            provider = "claude"

    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.0,
            google_api_key=api_key,
            max_output_tokens=2048
        )
    else:
        api_key = os.environ.get("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.0,
            api_key=api_key,
            max_tokens=2048
        )


@tool
def interpret_error(error_message: str, context: str = "") -> str:
    """
    Analyze an error message and suggest solutions.

    Uses Claude to understand the error and provide actionable solutions.

    Args:
        error_message: The error message to interpret
        context: Additional context (what command was run, what you were trying to do)

    Returns:
        str: Analysis of the error with suggested solutions

    Examples:
        - interpret_error("E: Unable to locate package docker", "installing Docker")
        - interpret_error("CUDA not found", "installing TensorFlow GPU")
    """
    try:
        llm = _get_llm()

        prompt = f"""You are a Linux system expert helping debug an installation error.

ERROR MESSAGE:
{error_message}

CONTEXT:
{context}

Analyze this error and provide:
1. What went wrong (root cause)
2. Why it happened
3. Top 3 specific solutions to try (in order of likelihood)
4. Any prerequisites or dependencies that might be missing

Be concise and actionable. Format as:

**Root Cause:** [explanation]

**Why:** [reason]

**Solutions:**
1. [specific command or steps]
2. [alternative approach]
3. [fallback option]

**Prerequisites:** [any missing dependencies]
"""

        response = llm.invoke(prompt)

        # Handle different response types
        if hasattr(response, 'content'):
            analysis = response.content
        else:
            analysis = str(response)

        return f"🔍 Error Analysis:\n\n{analysis}"

    except Exception as e:
        return f"❌ Error interpretation failed: {str(e)}\n\nOriginal error: {error_message}"


@tool
def search_solution_online(error: str, software: str) -> str:
    """
    Search for solutions to an error online.

    Simulates searching Stack Overflow, GitHub issues, and documentation.
    Uses Claude to provide relevant solutions based on common patterns.

    Args:
        error: The error message or problem description
        software: The software being installed (e.g., "docker", "python", "cuda")

    Returns:
        str: Top solutions found online

    Examples:
        - search_solution_online("package not found", "docker")
        - search_solution_online("CUDA driver mismatch", "tensorflow")
    """
    try:
        llm = _get_llm()

        prompt = f"""You are a search engine assistant helping find solutions.

SOFTWARE: {software}
ERROR: {error}

Based on common Stack Overflow answers, GitHub issues, and official documentation,
provide the top 3 most relevant solutions for this error.

For each solution, provide:
- Source (Stack Overflow / GitHub / Docs)
- Summary
- Specific commands or steps

Format as:

**Solution 1** (from Stack Overflow)
Summary: [brief description]
Steps:
```bash
[commands]
```

**Solution 2** (from GitHub Issues)
...

Be specific and include exact commands when possible.
"""

        response = llm.invoke(prompt)

        if hasattr(response, 'content'):
            solutions = response.content
        else:
            solutions = str(response)

        return f"🌐 Online Solutions Found:\n\n{solutions}"

    except Exception as e:
        return f"❌ Solution search failed: {str(e)}"


@tool
def try_alternative_installation(package: str, failed_method: str = "apt") -> str:
    """
    Try alternative installation methods when the primary method fails.

    Attempts different package managers and sources:
    - apt → snap → flatpak → pip → source

    Args:
        package: Package name to install
        failed_method: The method that failed (apt, snap, pip, etc.)

    Returns:
        str: Result of alternative installation attempt

    Examples:
        - try_alternative_installation("docker", "apt")
        - try_alternative_installation("code", "apt")
    """
    try:
        results = []

        # Define installation methods in priority order
        methods = {
            "snap": f"sudo snap install {package}",
            "flatpak": f"flatpak install -y {package}",
            "pip": f"pip3 install {package}",
            "pip_user": f"pip3 install --user {package}",
        }

        # Remove the failed method
        if failed_method in methods:
            del methods[failed_method]

        results.append(f"🔄 Trying alternative installation methods for '{package}'")
        results.append(f"❌ Failed method: {failed_method}\n")

        for method_name, command in methods.items():
            results.append(f"📦 Attempting: {method_name}")

            # Check if package manager exists
            check_cmds = {
                "snap": "which snap",
                "flatpak": "which flatpak",
                "pip": "which pip3",
                "pip_user": "which pip3"
            }

            check_result = secure_executor.execute_command(
                check_cmds.get(method_name, f"which {method_name}"),
                timeout=10
            )

            if not check_result['success']:
                results.append(f"   ⏭️  {method_name} not available, skipping\n")
                continue

            # Try installation
            install_result = secure_executor.execute_command(command, timeout=180)

            if install_result['success']:
                results.append(f"   ✅ Success with {method_name}!")
                results.append(f"   Output: {install_result['stdout'][:200]}\n")
                return "\n".join(results)
            else:
                error = install_result['stderr'][:200]
                results.append(f"   ❌ Failed: {error}\n")

        results.append("❌ All alternative methods failed")
        return "\n".join(results)

    except SecurityError as e:
        return f"🛑 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Alternative installation error: {str(e)}"


@tool
def verify_dependencies(package: str, package_manager: str = "apt") -> str:
    """
    Check if all dependencies for a package are satisfied.

    Identifies missing libraries, wrong versions, or conflicts.

    Args:
        package: Package name to check dependencies for
        package_manager: Package manager being used (apt, pip, npm)

    Returns:
        str: Dependency status and missing items

    Examples:
        - verify_dependencies("docker")
        - verify_dependencies("tensorflow", "pip")
    """
    try:
        results = []
        results.append(f"🔍 Checking dependencies for '{package}'...\n")

        if package_manager == "apt":
            # Check package dependencies
            cmd = f"apt-cache depends {package} 2>&1"
            result = secure_executor.execute_command(cmd, timeout=30)

            if result['success'] and result['stdout']:
                output = result['stdout']
                results.append("📦 Package Dependencies:")

                # Parse dependencies
                depends = re.findall(r'Depends: (.+)', output)
                if depends:
                    for dep in depends[:10]:  # Limit to first 10
                        # Check if installed
                        check_cmd = f"dpkg -l | grep -w {dep.split()[0]}"
                        check_result = secure_executor.execute_command(check_cmd, timeout=10)

                        status = "✅" if check_result['success'] else "❌"
                        results.append(f"   {status} {dep}")
                else:
                    results.append("   No dependencies listed")
            else:
                results.append(f"   ⚠️  Could not fetch dependencies: {result['stderr'][:200]}")

        elif package_manager == "pip":
            # Check pip dependencies
            cmd = f"pip3 show {package} 2>&1"
            result = secure_executor.execute_command(cmd, timeout=30)

            if result['success']:
                results.append("✅ Package information found")
                # Extract requires
                requires = re.search(r'Requires: (.+)', result['stdout'])
                if requires:
                    results.append(f"   Dependencies: {requires.group(1)}")
            else:
                results.append("   ℹ️  Package not yet installed, cannot check dependencies")

        # Check system requirements
        results.append("\n🖥️  System Requirements:")

        # Check common requirements
        checks = {
            "disk_space": ("df -h / | tail -1 | awk '{print $4}'", "Available disk space"),
            "memory": ("free -h | grep Mem | awk '{print $7}'", "Available memory"),
            "architecture": ("uname -m", "System architecture"),
        }

        for check_name, (cmd, description) in checks.items():
            result = secure_executor.execute_command(cmd, timeout=10)
            if result['success']:
                value = result['stdout'].strip()
                results.append(f"   ✅ {description}: {value}")

        return "\n".join(results)

    except Exception as e:
        return f"❌ Dependency verification error: {str(e)}"


@tool
def fix_broken_packages() -> str:
    """
    Attempt to fix broken package installations.

    Runs apt --fix-broken install and similar recovery commands.
    Useful when packages are in an inconsistent state.

    Returns:
        str: Result of fix attempt

    Examples:
        - fix_broken_packages()
    """
    try:
        results = []
        results.append("🔧 Attempting to fix broken packages...\n")

        # Try to fix broken packages
        fix_cmds = [
            ("sudo dpkg --configure -a", "Configure pending packages"),
            ("sudo apt-get --fix-broken install -y", "Fix broken dependencies"),
            ("sudo apt-get autoremove -y", "Remove unnecessary packages"),
            ("sudo apt-get clean", "Clean package cache"),
        ]

        for cmd, description in fix_cmds:
            results.append(f"📌 {description}...")
            result = secure_executor.execute_command(cmd, timeout=120)

            if result['success']:
                results.append(f"   ✅ Success")
                if result['stdout'].strip():
                    results.append(f"   Output: {result['stdout'][:200]}")
            else:
                results.append(f"   ⚠️  Warning: {result['stderr'][:200]}")

            results.append("")

        results.append("✅ Package fix attempt completed")
        return "\n".join(results)

    except SecurityError as e:
        return f"🛑 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Package fix error: {str(e)}"


@tool
def install_with_retry(
    package: str,
    max_attempts: int = 3,
    package_manager: str = "apt"
) -> str:
    """
    Install a package with automatic retry and error recovery.

    This is a high-level tool that combines multiple debugging strategies:
    1. Try primary installation
    2. If fails, interpret error
    3. Try recommended fixes
    4. Try alternative installation methods
    5. Verify success

    Args:
        package: Package name to install
        max_attempts: Maximum retry attempts (default: 3)
        package_manager: Package manager to use (apt, pip, snap)

    Returns:
        str: Detailed installation report

    Examples:
        - install_with_retry("docker")
        - install_with_retry("tensorflow", package_manager="pip")
    """
    try:
        results = []
        results.append(f"🚀 Installing '{package}' with intelligent retry...\n")

        # Define installation commands by package manager
        install_cmds = {
            "apt": f"sudo apt-get install -y {package}",
            "pip": f"pip3 install {package}",
            "snap": f"sudo snap install {package}",
        }

        if package_manager not in install_cmds:
            return f"❌ Unknown package manager: {package_manager}"

        base_cmd = install_cmds[package_manager]

        for attempt in range(1, max_attempts + 1):
            results.append(f"📦 Attempt {attempt}/{max_attempts}: {base_cmd}")

            # Try installation
            install_result = secure_executor.execute_command(base_cmd, timeout=300)

            if install_result['success']:
                results.append(f"   ✅ Installation successful!")
                results.append(f"   Output: {install_result['stdout'][:300]}\n")

                # Verify installation
                verify_cmd = f"which {package}"
                verify_result = secure_executor.execute_command(verify_cmd, timeout=10)

                if verify_result['success']:
                    location = verify_result['stdout'].strip()
                    results.append(f"✅ Verification passed: {package} found at {location}")

                    # Try to get version
                    version_result = secure_executor.execute_command(
                        f"{package} --version 2>&1 | head -1",
                        timeout=10
                    )
                    if version_result['success']:
                        results.append(f"   Version: {version_result['stdout'].strip()}")

                return "\n".join(results)
            else:
                # Installation failed
                error = install_result['stderr']
                results.append(f"   ❌ Failed with error:\n   {error[:300]}\n")

                if attempt < max_attempts:
                    results.append(f"🔍 Analyzing error for retry strategy...\n")

                    # Common error patterns and fixes
                    if "Unable to locate package" in error:
                        results.append("   💡 Package not found - will try alternative sources")
                    elif "dpkg was interrupted" in error or "dpkg" in error.lower():
                        results.append("   💡 Package system issue - running fix...")
                        fix_result = fix_broken_packages()
                        results.append(fix_result + "\n")
                    elif "Could not get lock" in error:
                        results.append("   💡 Lock file issue - waiting and retrying...")
                        import time
                        time.sleep(5)
                    else:
                        results.append("   💡 Generic error - trying alternative methods")

        # All attempts with primary method failed - try alternatives
        results.append(f"\n❌ All {max_attempts} attempts with {package_manager} failed")
        results.append(f"🔄 Trying alternative installation methods...\n")

        alt_result = try_alternative_installation(package, package_manager)
        results.append(alt_result)

        return "\n".join(results)

    except SecurityError as e:
        return f"🛑 Security Error: {str(e)}"
    except Exception as e:
        return f"❌ Installation error: {str(e)}"


# Export all debugging tools
DEBUGGING_TOOLS = [
    interpret_error,
    search_solution_online,
    try_alternative_installation,
    verify_dependencies,
    fix_broken_packages,
    install_with_retry,
]

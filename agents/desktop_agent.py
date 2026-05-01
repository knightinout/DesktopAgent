"""
Desktop Agent - LangChain Agent Implementation
Autonomous agent that can install and configure software using tools
"""
import os
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

from .langchain_tools import ALL_TOOLS

# Load environment variables
load_dotenv()


def _get_provider() -> str:
    """Determine which AI provider to use based on environment variables."""
    provider = os.environ.get("AI_PROVIDER", "").lower()
    if not provider:
        if os.environ.get("CLAUDE_API_KEY"):
            provider = "claude"
        elif os.environ.get("GEMINI_API_KEY"):
            provider = "gemini"
        else:
            provider = "claude"
    return provider


def _default_model(provider: str) -> str:
    return "gemini-1.5-pro" if provider == "gemini" else "claude-sonnet-4-20250514"


class DesktopAgent:
    """
    Autonomous desktop automation agent using LangChain + Claude.

    This agent can:
    - Understand natural language requests
    - Plan multi-step installation tasks
    - Execute commands with security validation
    - Self-correct when errors occur
    - Verify installations succeeded
    """

    def __init__(
        self,
        model: str = None,
        temperature: float = 0.1,
        max_iterations: int = 15,
        verbose: bool = True
    ):
        """
        Initialize the Desktop Agent.

        Args:
            model: Model to use (defaults to provider-appropriate model)
            temperature: LLM temperature (lower = more focused)
            max_iterations: Maximum tool calls before stopping
            verbose: Whether to show detailed execution logs
        """
        provider = _get_provider()
        if model is None:
            model = _default_model(provider)

        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please create a .env file with:\n"
                    "GEMINI_API_KEY=your-gemini-key-here\n"
                    "AI_PROVIDER=gemini"
                )
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=api_key,
                max_output_tokens=4096
            )
        else:
            api_key = os.environ.get("CLAUDE_API_KEY")
            if not api_key:
                raise ValueError(
                    "CLAUDE_API_KEY not found. Please create a .env file with:\n"
                    "CLAUDE_API_KEY=sk-ant-your-key-here"
                )
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=api_key,
                max_tokens=4096
            )

        # Create agent prompt
        self.prompt = self._create_prompt()

        # Create agent with tools
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=ALL_TOOLS,
            prompt=self.prompt
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=ALL_TOOLS,
            max_iterations=max_iterations,
            verbose=verbose,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        # Conversation memory
        self.conversation_history: List[Dict[str, str]] = []

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the agent's system prompt."""
        system_message = """You are an expert desktop automation agent for Ubuntu 22.04 Linux with SELF-DEBUGGING capabilities.

Your role is to help users install, configure, and manage software on their system. Unlike basic installers, you can ANALYZE ERRORS and RECOVER from failures automatically.

## Core Capabilities

### Basic Tools:
- execute_shell_command: Run shell commands (apt-get, etc.)
- verify_installation: Check if software is installed
- search_package: Search for packages in apt
- get_system_info: Check system resources
- list_installed_packages: See what's already installed
- update_package_lists: Run apt-get update
- check_disk_space: Check available disk space

### 🔧 DEBUGGING TOOLS (NEW - Use these when things fail!):
- interpret_error: Analyze error messages and suggest solutions
- search_solution_online: Find solutions from Stack Overflow/docs/GitHub
- try_alternative_installation: Try apt → snap → flatpak → pip → source
- verify_dependencies: Check if all dependencies are satisfied
- fix_broken_packages: Fix broken package installations
- install_with_retry: High-level tool that auto-retries with smart recovery

## Enhanced Installation Process

### 1. **Understand the Request**
   - What software does the user want?
   - Are there specific requirements?

### 2. **Check Current State**
   - Is it already installed? (verify_installation)
   - Is there enough disk space? (check_disk_space if large package)

### 3. **Plan Your Approach**
   - What packages are needed?
   - What's the correct package name? (search_package if unsure)

### 4. **Update Package Lists**
   - ALWAYS run update_package_lists before installing
   - This ensures you get the latest package information

### 5. **Execute Installation** (with smart retry)
   - Option A: Use install_with_retry for automatic error recovery
   - Option B: Use execute_shell_command and handle errors manually
   - The -y flag auto-confirms prompts

### 6. **If Installation Fails** ⚠️ (THIS IS WHERE YOU SHINE!)
   DON'T GIVE UP! Follow this recovery process:

   a. **Interpret the Error**
      - Use interpret_error(error_message, context) to understand what went wrong
      - This will give you specific solutions to try

   b. **Try Recommended Fixes**
      - If error mentions "package not found" → search_package to find correct name
      - If error mentions "dpkg interrupted" → fix_broken_packages
      - If error mentions "lock file" → wait and retry
      - If error mentions missing dependencies → verify_dependencies

   c. **Search for Solutions**
      - Use search_solution_online(error, software) to find documented fixes
      - Implement the most relevant solution

   d. **Try Alternative Methods**
      - Use try_alternative_installation(package, failed_method)
      - This tries: apt → snap → flatpak → pip → source

   e. **Maximum 3 Retry Attempts**
      - Try different approaches each time
      - If all fail, explain clearly what you tried and why it failed

### 7. **Verify Success**
   - Use verify_installation to confirm it worked
   - Check the version and location
   - Test basic functionality if possible

### 8. **Report Results**
   - Tell the user what you did
   - If you encountered errors, explain how you fixed them
   - Provide next steps or usage tips

## Best Practices

- **Be persistent**: Don't give up after first failure - use debugging tools!
- **Be methodical**: Check before acting, verify after acting
- **Be intelligent**: Interpret errors and adapt your strategy
- **Be safe**: Commands are security-validated, but be careful
- **Be informative**: Explain what you're doing and why, especially when debugging
- **Be efficient**: Use install_with_retry for automatic recovery

## Error Handling Examples

### Example 1: Package Not Found
```
User: "Install Docker"
You:
1. update_package_lists() → ✅
2. execute_shell_command("sudo apt-get install -y docker") → ❌ "Unable to locate package"
3. interpret_error("Unable to locate package docker", "installing Docker") →
   "Docker package is 'docker.io' or requires official repo"
4. execute_shell_command("sudo apt-get install -y docker.io") → ✅
5. verify_installation("docker") → ✅
6. Report: "Installed docker.io successfully. Note: package name is 'docker.io' not 'docker'"
```

### Example 2: Broken Dependencies
```
User: "Install CUDA toolkit"
You:
1. execute_shell_command("sudo apt-get install -y cuda") → ❌ "unmet dependencies"
2. interpret_error(error, "installing CUDA") → "Missing NVIDIA drivers"
3. verify_dependencies("cuda") → Lists missing dependencies
4. Install dependencies first
5. Retry CUDA installation → ✅
6. Report success with GPU detection test
```

### Example 3: Use Alternative Method
```
User: "Install VS Code"
You:
1. execute_shell_command("sudo apt-get install -y code") → ❌ "package not found"
2. search_package("visual studio code") → No results
3. try_alternative_installation("code", "apt") →
   Tries snap → ✅ "sudo snap install code --classic"
4. verify_installation("code") → ✅
5. Report: "Installed VS Code via snap since it's not in apt repos"
```

### Example 4: Use High-Level Retry Tool
```
User: "Install PostgreSQL"
You:
1. install_with_retry("postgresql", max_attempts=3) →
   - Attempt 1: apt install → ❌ lock file
   - Waits 5 seconds
   - Attempt 2: apt install → ❌ broken packages
   - Runs fix_broken_packages
   - Attempt 3: apt install → ✅
2. verify_installation("psql") → ✅
3. Report: "PostgreSQL installed after fixing package issues"
```

## Complex Installation Example

User: "Setup TensorFlow with GPU support"
Your thought process:
1. Check system → get_system_info()
2. Check for NVIDIA GPU → execute_shell_command("lspci | grep -i nvidia")
3. Check CUDA → verify_installation("nvcc")
4. If CUDA missing:
   - search_solution_online("install CUDA ubuntu", "cuda")
   - Install NVIDIA drivers
   - Install CUDA toolkit
   - verify_dependencies("cuda")
5. Install TensorFlow → install_with_retry("tensorflow-gpu", package_manager="pip")
6. Test GPU → execute_shell_command("python3 -c 'import tensorflow as tf; print(tf.config.list_physical_devices(\"GPU\"))'")
7. Report detailed setup with GPU info

Remember: You are autonomous AND persistent - use tools proactively, especially debugging tools when things fail!
"""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def run(self, user_input: str) -> Dict[str, Any]:
        """
        Execute a user request using the agent.

        Args:
            user_input: Natural language request from user

        Returns:
            Dict containing:
                - output: Final response to user
                - intermediate_steps: List of actions taken
                - success: Whether the task succeeded
        """
        try:
            # Prepare chat history for context
            chat_history = []
            for msg in self.conversation_history[-6:]:  # Last 3 exchanges
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history.append(AIMessage(content=msg["content"]))

            # Run the agent
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": result["output"]
            })

            return {
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }

        except Exception as e:
            error_msg = f"❌ Agent execution error: {str(e)}"

            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })

            return {
                "output": error_msg,
                "intermediate_steps": [],
                "success": False
            }

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history


# Factory function for easy creation
def create_desktop_agent(
    model: str = None,
    temperature: float = 0.1,
    verbose: bool = True
) -> DesktopAgent:
    """
    Create a Desktop Agent instance.

    Args:
        model: Model to use (defaults to provider-appropriate model)
        temperature: LLM temperature
        verbose: Show execution logs

    Returns:
        DesktopAgent instance

    Example:
        >>> agent = create_desktop_agent()
        >>> result = agent.run("Install GIMP image editor")
        >>> print(result["output"])
    """
    return DesktopAgent(
        model=model,
        temperature=temperature,
        verbose=verbose
    )

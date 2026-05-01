import os
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _get_provider() -> str:
    """Determine which AI provider to use based on environment variables."""
    provider = os.getenv("AI_PROVIDER", "").lower()
    if not provider:
        if os.getenv("CLAUDE_API_KEY"):
            provider = "claude"
        elif os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        else:
            provider = "claude"
    return provider


class AIClient:
    def __init__(self):
        self.provider = _get_provider()

        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or len(api_key.strip()) < 10:
                raise ValueError("Valid GEMINI_API_KEY required in .env")
            try:
                from google import genai
                from google.genai import types
                self._gemini_client = genai.Client(api_key=api_key.strip())
                self._gemini_config = types.GenerateContentConfig(
                    max_output_tokens=300,
                    temperature=0.1
                )
            except Exception as e:
                raise ValueError(f"Failed to initialize Gemini client: {e}")
        else:
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key or len(api_key.strip()) < 10:
                raise ValueError("Valid CLAUDE_API_KEY required in .env")
            try:
                from anthropic import Anthropic
                self._claude_client = Anthropic(api_key=api_key.strip())
            except Exception as e:
                raise ValueError(f"Failed to initialize Claude client: {e}")

    def call(self, prompt: str, sanitize: bool = True) -> Optional[str]:
        if not prompt or len(prompt.strip()) == 0:
            return None

        try:
            if self.provider == "gemini":
                response = self._gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt.strip(),
                    config=self._gemini_config
                )
                text = response.text
            else:
                message = self._claude_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt.strip()}]
                )
                text = message.content[0].text

            if sanitize:
                return self._sanitize_response(text)
            else:
                return text.strip()

        except Exception as e:
            print(f"AI API error ({self.provider}): {e}")
            return None

    def _sanitize_response(self, response: str) -> str:
        """Sanitize AI response to prevent path traversal attacks."""
        if not response:
            return ""

        lines = []
        for line in response.strip().split('\n'):
            if '->' in line or (' - ' in line and not line.strip().startswith('-')):
                if ' - ' in line and '->' not in line:
                    line = line.replace(' - ', ' -> ')
                clean_line = re.sub(r'[.]{2,}|[<>:"|?*]', '', line)
                clean_line = re.sub(r'^[/\\]', '', clean_line)
                lines.append(clean_line)

        return '\n'.join(lines)


# Backward compatibility alias
ClaudeClient = AIClient

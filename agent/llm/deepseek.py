"""DeepSeek LLM client for the agent."""

from typing import Any, Optional

import httpx


class DeepSeekClient:
    """LLM client for DeepSeek API (OpenAI-compatible format)."""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        api_base: str = "https://api.deepseek.com",
    ):
        self.api_key = api_key
        self.model = model
        self.api_base = api_base.rstrip("/")
        self._client = httpx.Client(timeout=120.0)

    def chat(self, messages: list[dict[str, Any]]) -> str:
        """
        Send a chat completion request to DeepSeek.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            The assistant's response text.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }

        response = self._client.post(
            f"{self.api_base}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

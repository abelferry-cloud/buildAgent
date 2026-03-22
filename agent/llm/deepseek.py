"""DeepSeek LLM client for the agent."""

from typing import Any, AsyncIterator, Optional

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
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def chat(
        self, messages: list[dict[str, Any]], stream: bool = False
    ) -> str | AsyncIterator[str]:
        """
        Send a chat completion request to DeepSeek.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            stream: If True, returns an async iterator yielding response chunks.

        Returns:
            The assistant's response text, or an async iterator if stream=True.
        """
        if stream:
            return self._chat_stream(messages)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }

        client = self._get_client()
        response = await client.post(
            f"{self.api_base}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code != 200:
            print(f"[DEBUG] API Error: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text[:500]}")
            print(f"[DEBUG] Request payload: {payload}")
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _chat_stream(self, messages: list[dict[str, Any]]) -> AsyncIterator[str]:
        """
        Streaming chat completion - yields response chunks.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Yields:
            Response text chunks as they arrive from the API.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "stream": True,
        }

        client = self._get_client()
        async with client.stream(
            "POST",
            f"{self.api_base}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        break
                    import json

                    data = json.loads(data_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

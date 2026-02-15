"""Bytez API client wrapper with OpenAI-compatible interface."""
import httpx
import json
from typing import Optional, Dict, Any, AsyncGenerator
from services.key_manager import get_key_manager


class BytezClient:
    """OpenAI-compatible client for Bytez API."""

    BASE_URL = "https://api.bytez.com/models/v2/openai/v1"

    def __init__(self):
        """Initialize Bytez client."""
        self.key_manager = get_key_manager()
        self.client = self._create_client()

    def _create_client(self) -> httpx.AsyncClient:
        """Create a new async HTTP client with current API key."""
        key = self.key_manager.get_current_key()
        return httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def _refresh_client(self) -> None:
        """Refresh the HTTP client with a new API key after rotation."""
        if self.client:
            await self.client.aclose()
        self.client = self._create_client()

    async def _handle_error_and_retry(
        self, status_code: int, error_detail: str
    ) -> bool:
        """Handle API errors and determine if we should retry with a new key.

        Args:
            status_code: HTTP status code
            error_detail: Error message from API

        Returns:
            True if we rotated to a new key and should retry, False otherwise.
        """
        if status_code in (401, 403):
            # Auth error - mark key as failed and rotate
            reason = f"{status_code} Unauthorized/Forbidden"
            self.key_manager.mark_current_key_failed(reason)
            if self.key_manager.rotate_key():
                await self._refresh_client()
                return True
            return False

        elif status_code == 429:
            # Rate limit - rotate key
            reason = "429 Rate Limited"
            self.key_manager.mark_current_key_failed(reason)
            if self.key_manager.rotate_key():
                await self._refresh_client()
                return True
            return False

        elif status_code >= 500:
            # Server error - might be temporary, but rotate anyway
            reason = f"{status_code} Server Error"
            self.key_manager.mark_current_key_failed(reason)
            if self.key_manager.rotate_key():
                await self._refresh_client()
                return True
            return False

        return False

    async def chat_completions(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[list] = None,
        stream: bool = False,
    ) -> Any:
        """Call Bytez chat completions API.

        Args:
            model: Model ID (e.g., "gpt-4", "claude-3-sonnet")
            messages: List of message dicts with "role" and "content"
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            tools: Optional list of tool definitions (OpenAI format)
            stream: Whether to stream the response

        Returns:
            Response dict or async generator if streaming.

        Raises:
            RuntimeError: If all keys are exhausted or API call fails.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools

        if stream:
            payload["stream"] = True

        max_retries = len(self.key_manager.keys)
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = await self.client.post("/chat/completions", json=payload)

                if response.status_code == 200:
                    self.key_manager.record_success()
                    if stream:
                        return self._stream_response(response)
                    else:
                        return response.json()
                else:
                    error_detail = response.text
                    should_retry = await self._handle_error_and_retry(
                        response.status_code, error_detail
                    )
                    if should_retry:
                        retry_count += 1
                        continue
                    else:
                        raise RuntimeError(
                            f"Bytez API error {response.status_code}: {error_detail}"
                        )

            except httpx.RequestError as e:
                raise RuntimeError(f"Bytez API request failed: {str(e)}")

        raise RuntimeError("All API keys exhausted after retries")

    async def _stream_response(self, response: httpx.Response) -> AsyncGenerator:
        """Stream response from Bytez API.

        Args:
            response: The HTTP response object

        Yields:
            Parsed JSON chunks from the stream.
        """
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    yield chunk
                except json.JSONDecodeError:
                    continue

    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


# Global singleton instance
_bytez_client: Optional[BytezClient] = None


async def get_bytez_client() -> BytezClient:
    """Get or create the global BytezClient singleton."""
    global _bytez_client
    if _bytez_client is None:
        _bytez_client = BytezClient()
    return _bytez_client

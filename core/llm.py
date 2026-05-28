"""
core/llm.py — Free LLM via Groq API
Groq provides free API access to LLaMA3, Mixtral, Gemma models.
Get your free API key: https://console.groq.com
"""
import os
from typing import Generator
from utils.logger import get_logger

log = get_logger("llm")


class LLMEngine:
    """
    Wrapper around Groq's free LLM API.
    Reads API key from environment at call time (not at import time),
    so it works correctly when the key is set via the Streamlit sidebar.
    """

    def __init__(
        self,
        model: str = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        # Read from env at construction time — but allow override per-call
        self.model = model or os.getenv("LLM_MODEL", "llama3-8b-8192")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        log.info(f"LLM engine initialised: model={self.model}")

    def _get_client(self):
        """Build (or rebuild) a Groq client using the current env key."""
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set.\n"
                "1. Get a FREE key at https://console.groq.com\n"
                "2. Enter it in the sidebar API Key field, OR\n"
                "3. Add it to your .env file as GROQ_API_KEY=gsk_..."
            )
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Run: pip install groq")

        return Groq(api_key=api_key)

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a response. Raises clearly on auth/type errors."""
        client = self._get_client()

        # Refresh model from env in case sidebar changed it
        self.model = os.getenv("LLM_MODEL", self.model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        log.debug(f"Calling Groq ({self.model}), prompt={len(prompt)} chars")

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            answer = response.choices[0].message.content or ""
            log.debug(f"Response: {len(answer)} chars")
            return answer
        except Exception as e:
            log.error(f"Groq API error: {e}")
            raise

    def stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        """Stream response tokens."""
        client = self._get_client()
        self.model = os.getenv("LLM_MODEL", self.model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

"""ChatGPT interface that uses the OpenAI REST API instead of browser automation."""
from typing import Optional, Sequence, Dict, Any
import os, openai

class ChatGPTInterface:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",   # ≈ “o3” on the website
        **completion_opts: Any        # temperature, seed, etc.
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set.")
        openai.api_key = self.api_key
        self.model = model
        self.completion_opts = {"temperature": 0.2, **completion_opts}

    # context-manager stubs so existing code (`with ChatGPTInterface() as chat:`) keeps working
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass
    def close(self): pass

    # --- public --- #
    def send_prompt(self, prompt: str, system_prompt: str | None = None) -> str:
        if system_prompt is not None:
            messages: Sequence[Dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        else:
            messages: Sequence[Dict[str, str]] = [{"role": "user", "content": prompt}]
        resp = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            **self.completion_opts
        )
        return resp.choices[0].message.content.strip()

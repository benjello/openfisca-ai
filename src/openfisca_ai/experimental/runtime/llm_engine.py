"""LLM engine abstraction for agent calls."""


class LLMEngine:
    """Abstract interface to an LLM (e.g. OpenAI, local model)."""

    def complete(self, prompt: str, **kwargs) -> str:
        """Send a prompt and return the model's text completion."""
        raise NotImplementedError

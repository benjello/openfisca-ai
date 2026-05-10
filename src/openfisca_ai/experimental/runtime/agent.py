"""Base agent abstraction."""


class Agent:
    """Base class for openfisca_ai agents (extractor, coder, etc.)."""

    def __init__(self, name: str, llm_engine=None):
        self.name = name
        self.llm_engine = llm_engine

    def run(self, **inputs):
        """Execute the agent's task. Override in subclasses."""
        raise NotImplementedError

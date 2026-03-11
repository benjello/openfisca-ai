"""Agent that extracts structured information from law text."""

from openfisca_ai.core.agent import Agent


class ExtractorAgent(Agent):
    """Extracts legal/legislative content into structured form."""

    def __init__(self, llm_engine=None):
        super().__init__(name="extractor", llm_engine=llm_engine)

    def run(self, text: str, **kwargs):
        """Extract structured data from raw law text."""
        # TODO: use skills.extract_law and LLM
        return {"raw": text, "extracted": {}}

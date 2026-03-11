"""Agent that generates OpenFisca code from structured law data."""

from openfisca_ai.core.agent import Agent


class CoderAgent(Agent):
    """Generates OpenFisca (Python) code from extracted law."""

    def __init__(self, llm_engine=None):
        super().__init__(name="coder", llm_engine=llm_engine)

    def run(
        self,
        extracted: dict,
        reference_code_path: str | None = None,
        country_config: dict | None = None,
        **kwargs,
    ):
        """
        Produce code from extracted legislation.

        If reference_code_path is set (e.g. from country config), the agent
        can use that codebase as reference for patterns and naming.
        country_config can provide conventions (entity_levels, parameter_hierarchy).
        """
        # TODO: use skills.generate_code and LLM; optionally read reference_code_path
        return {
            "code": "",
            "extracted": extracted,
            "reference_code_path": reference_code_path,
            "country_config": country_config,
        }

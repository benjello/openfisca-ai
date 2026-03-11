"""Orchestrates agents and pipelines."""


class Orchestrator:
    """Coordinates agents and execution flow."""

    def __init__(self, agents=None):
        self.agents = agents or {}

    def register_agent(self, name: str, agent):
        """Register an agent by name."""
        self.agents[name] = agent

    def run_pipeline(self, pipeline_name: str, **inputs):
        """Run a named pipeline with the given inputs."""
        raise NotImplementedError(f"Pipeline '{pipeline_name}' not implemented")

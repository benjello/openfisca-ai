"""Core components: agent, orchestrator, LLM engine."""

from openfisca_ai.core.agent import Agent
from openfisca_ai.core.artifacts import (
    materialize_artifacts,
    plan_artifact_writes,
    resolve_openfisca_repo_root,
)
from openfisca_ai.core.orchestrator import Orchestrator
from openfisca_ai.core.llm_engine import LLMEngine
from openfisca_ai.core.reference_package import (
    analyze_reference_package,
    build_implementation_brief,
)
from openfisca_ai.core.scaffold_report import (
    render_scaffold_report_markdown,
    render_scaffold_report_text,
)

__all__ = [
    "Agent",
    "Orchestrator",
    "LLMEngine",
    "materialize_artifacts",
    "plan_artifact_writes",
    "resolve_openfisca_repo_root",
    "analyze_reference_package",
    "build_implementation_brief",
    "render_scaffold_report_markdown",
    "render_scaffold_report_text",
]

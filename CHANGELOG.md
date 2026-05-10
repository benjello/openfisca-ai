# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Clarified stable, beta, and experimental layers in the package architecture.
- Moved alpha agent runtime, skills, and pipelines under `openfisca_ai.experimental` while keeping compatibility wrappers.
- Centralized OpenFisca package layout and parameter/unit helpers under `openfisca_ai.domain`.
- Added target diagnostics and target-aware MCP setup commands.

## [0.1.1] - 2026-04-17

### Changed

- Simplified docstrings across codebase to use standard single-line format
- Removed verbose multi-line docstrings from validation tools
- Lightened docstrings in MCP client initialization

## [0.1.0] - 2025-02-26

### Added

- Initial project structure: `openfisca_ai` package with `core`, `agents`, `skills`, `pipelines`
- Core components: `Agent`, `Orchestrator`, `LLMEngine` (stub implementations)
- Agents: `ExtractorAgent`, `CoderAgent`
- Skills: `extract_law`, `generate_code` (placeholders)
- Pipeline: `run_law_to_code` (law text → extracted structure → code)
- CLI: `openfisca-ai run <task.json>` for running pipeline tasks
- Example task: `tasks/example_task.json`
- Tests for the law_to_code pipeline
- Documentation: README, CONTRIBUTING, LICENSE

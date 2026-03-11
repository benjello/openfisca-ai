# Workflows and Pipelines

End-to-end workflows to transform legislation into tested OpenFisca code.

## Main Pipeline: `law_to_code`

Transformation: **legal text → tested OpenFisca code**.

### Architecture

```
[Legal text]
    ↓
[document-collector] → Structured sources
    ↓
[Extractor] → Extracted data (rules, parameters, variables)
    ↓
[parameter-architect] → YAML parameter structure
    ↓
[rules-engineer] → Python code (variables, formulas)
    ↓
[test-creator] → Unit tests + integration tests
    ↓
[implementation-validator] → Validation report
    ↓
[ci-fixer] → Fixes applied, tests pass
    ↓
[Code ready for PR]
```

### Current Implementation

See `src/openfisca_ai/pipelines/law_to_code.py`:

```python
def run_law_to_code(
    law_text: str,
    country_id: str | None = None,
    use_existing_code_as_reference: bool = False,
) -> dict:
    """
    Complete pipeline: legal text → OpenFisca code.

    If country_id is provided, automatically loads:
    - Country config (conventions)
    - Existing code (as reference)
    """
    # Load country config
    if country_id and use_existing_code_as_reference:
        country_config = load_country_config(country_id)
        reference_code_path = get_reference_code_path(country_id)

    # Agents
    extractor = ExtractorAgent()
    coder = CoderAgent()

    # Execution
    extracted = extractor.run(text=law_text)
    code = coder.run(
        extracted=extracted,
        reference_code_path=reference_code_path,
        country_config=country_config
    )

    return {"extracted": extracted, "code": code}
```

### Usage via CLI

```bash
# With task file
openfisca-ai run tasks/countries/countria/encode_ceiling.json

# The task.json contains:
{
  "id": "encode_ceiling",
  "country": "countria",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Section 1 – The ceiling..."
  },
  "options": {
    "use_existing_code_as_reference": true
  }
}
```

## Command-Based Workflows (inspired by PolicyEngine)

### `/encode-policy <program>`

Complete implementation of a program (end-to-end).

**Steps**:
1. `document-collector`: Search for official sources
2. `parameter-architect`: Design parameter hierarchy
3. `rules-engineer`: Implement rules + variables
4. `test-creator`: Generate tests
5. `implementation-validator`: Validate quality
6. `ci-fixer`: Fix until tests pass

**Example**:
```bash
/encode-policy "Housing allowance Countria"
```

### `/review-pr <number>`

Complete PR review.

**Steps**:
1. `program-reviewer`: Check regulatory compliance
2. `reference-validator`: Verify references (URLs, pages)
3. `implementation-validator`: Check patterns and quality
4. `cross-program-validator`: Check consistency with other programs
5. Post report on GitHub

**Example**:
```bash
/review-pr 42
```

### `/fix-pr <number>`

Apply automatic fixes.

**Steps**:
1. Load report from `/review-pr`
2. `ci-fixer`: Apply fixes
3. Run tests locally
4. Iterate until tests pass
5. Push changes

**Example**:
```bash
/fix-pr 42
```

## Agents by Phase

### Phase 1: Collection and Extraction

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **document-collector** | Gather official sources | Program/benefit to implement | Structured documents (markdown, PDF→text) |
| **Extractor** | Extract structured rules | Legal text | Dict `{rules, parameters, variables}` |

### Phase 2: Architecture

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **parameter-architect** | Design parameter structure | Extracted rules + country conventions | YAML files (hierarchy, metadata) |

### Phase 3: Implementation

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **rules-engineer** | Implement variables/formulas | Rules + parameters + reference code | Python code (variables.py) |
| **test-creator** | Generate tests | Rules + implemented code | Test files (test_*.py) |

### Phase 4: Validation

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **implementation-validator** | Validate overall quality | Code + parameters + tests | Report with fixes |
| **program-reviewer** | Regulatory review | Code + legal sources | Compliance report |
| **reference-validator** | Validate references | Parameters + variables | List of broken/incorrect links |
| **cross-program-validator** | Cross-program consistency | All country programs | Inconsistency report |

### Phase 5: Correction

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **ci-fixer** | Apply fixes | Validation report | Fixed code + passing tests |

## Minimal Workflow (one country, one program)

For a **first country** and **first implementation**:

### 1. Prepare country config
```yaml
# config/countries/countria.yaml
id: countria
legislative_sources:
  root: /data/countria-laws
existing_code:
  path: /repos/openfisca-countria
```

### 2. Create task
```json
{
  "id": "child_allowance",
  "country": "countria",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Section 53 – Child allowances..."
  }
}
```

### 3. Execute pipeline
```bash
openfisca-ai run tasks/countries/countria/child_allowance.json
```

### 4. (Optional) Manual validation
- Review generated code
- Check tests
- Run `pytest`

### 5. (Optional) Correction
If issues detected:
```bash
# Run implementation-validator
# Apply fixes with ci-fixer
# Re-test
```

## Extension: Adding a New Workflow

### Example: Migration workflow (old code → new format)

```python
# pipelines/migrate_legacy.py
def run_migration(
    old_code_path: str,
    country_id: str,
    target_format: str = "openfisca-core-latest"
) -> dict:
    """Migrate old code to new format."""

    config = load_country_config(country_id)

    # Agents
    analyzer = LegacyCodeAnalyzer()
    migrator = CodeMigrator()
    validator = ImplementationValidator()

    # Execution
    analysis = analyzer.run(old_code_path=old_code_path)
    migrated = migrator.run(
        analysis=analysis,
        target_format=target_format,
        conventions=config.get('conventions')
    )
    validated = validator.run(code=migrated)

    return {"migrated": migrated, "validation": validated}
```

### Register in CLI

```python
# cli.py
elif pipeline_name == "migrate_legacy":
    from openfisca_ai.pipelines.migrate_legacy import run_migration
    result = run_migration(
        old_code_path=inputs['old_code_path'],
        country_id=country_id
    )
```

## Parallelization (future)

To process **multiple programs in parallel**:

```python
# Isolate each program in a Git worktree
from openfisca_ai.agents.isolation import create_worktree

worktree_housing = create_worktree('housing-allowance')
worktree_child = create_worktree('child-allowance')

# Execute pipelines in parallel (threads/processes)
results = await asyncio.gather(
    run_law_to_code(..., worktree=worktree_housing),
    run_law_to_code(..., worktree=worktree_child)
)

# Merge results
merge_worktrees([worktree_housing, worktree_child])
```

See PolicyEngine's `isolation-setup` and `integration-agent` agents.

## Summary

| Workflow | Command | Agents Used |
|----------|---------|-------------|
| Complete implementation | `/encode-policy` | document-collector → extractor → parameter-architect → rules-engineer → test-creator → validators → ci-fixer |
| PR review | `/review-pr` | program-reviewer, reference-validator, implementation-validator, cross-program-validator |
| PR fix | `/fix-pr` | ci-fixer (+ re-test) |
| Basic pipeline | `openfisca-ai run` | extractor → coder |

---

**Next steps**:
- See [roles/](roles/) for details on each agent
- See [country-config.md](country-config.md) for country configuration

"""Pipeline: from law text to OpenFisca code."""

from openfisca_ai.agents.extractor import ExtractorAgent
from openfisca_ai.agents.coder import CoderAgent
from openfisca_ai.core.artifacts import (
    materialize_artifacts,
    plan_artifact_writes,
    resolve_openfisca_repo_root,
)
from openfisca_ai.core.reference_package import (
    analyze_reference_package,
    build_implementation_brief,
)


def run_law_to_code(
    law_text: str,
    llm_engine=None,
    country_id: str | None = None,
    use_existing_code_as_reference: bool = False,
    include_reference_audit_summary: bool = False,
    extracted_data: dict | None = None,
    artifacts_output_dir: str | None = None,
    apply_artifacts_to_reference_package: bool = False,
    existing_artifact_strategy: str = "create",
    overwrite_artifacts: bool = False,
    plan_only: bool = False,
) -> dict:
    """
    Run the full pipeline: raw law text -> extracted structure -> code.

    If country_id is set and use_existing_code_as_reference is True, the coder
    receives the path to existing OpenFisca code for that country (from config)
    so it can use it as reference. Same pipeline for any country.

    Returns dict with keys: extracted, code, and optional reference package metadata.
    """
    if artifacts_output_dir and apply_artifacts_to_reference_package:
        raise ValueError(
            "Use either artifacts_output_dir or apply_artifacts_to_reference_package, not both."
        )

    reference_code_path = None
    country_config = None
    reference_package_analysis = None
    reference_package_analysis_error = None

    if country_id and use_existing_code_as_reference:
        try:
            from openfisca_ai.config_loader import load_country_config, get_reference_code_path
            country_config = load_country_config(country_id)
            ref_path = get_reference_code_path(country_id)
            reference_code_path = str(ref_path) if ref_path and ref_path.exists() else None
        except Exception:
            pass

    if reference_code_path:
        try:
            reference_package_analysis = analyze_reference_package(
                reference_code_path,
                include_audit_summary=include_reference_audit_summary,
            )
        except Exception as exc:
            reference_package_analysis_error = str(exc)

    extractor = ExtractorAgent(llm_engine=llm_engine)
    coder = CoderAgent(llm_engine=llm_engine)

    if extracted_data is None:
        extracted = extractor.run(text=law_text)
    else:
        extracted = {
            "raw": law_text,
            "extracted": extracted_data,
        }
    implementation_brief = build_implementation_brief(
        extracted=extracted.get("extracted", extracted),
        country_config=country_config,
        reference_package_analysis=reference_package_analysis,
        country_id=country_id,
    )
    result = coder.run(
        extracted=extracted.get("extracted", extracted),
        reference_code_path=reference_code_path,
        country_config=country_config,
        reference_package_analysis=reference_package_analysis,
        implementation_brief=implementation_brief,
    )

    out = {
        "extracted": extracted,
        "code": result.get("code", ""),
        "implementation_brief": implementation_brief,
        "artifacts": result.get("artifacts", []),
    }
    if country_id:
        out["country_id"] = country_id
    if reference_code_path:
        out["reference_code_path"] = reference_code_path
    if reference_package_analysis:
        out["reference_package_analysis"] = reference_package_analysis
    if reference_package_analysis_error:
        out["reference_package_analysis_error"] = reference_package_analysis_error
    if result.get("notes"):
        out["notes"] = result["notes"]
    if artifacts_output_dir:
        out["artifacts_output_dir"] = artifacts_output_dir
        out["artifact_write_plan"] = plan_artifact_writes(
            out["artifacts"],
            artifacts_output_dir,
            strategy="update" if overwrite_artifacts else existing_artifact_strategy,
        )
        if not plan_only:
            out["written_artifacts"] = materialize_artifacts(
                out["artifacts"],
                artifacts_output_dir,
                strategy=existing_artifact_strategy,
                overwrite=overwrite_artifacts,
            )
    elif apply_artifacts_to_reference_package:
        if not reference_code_path:
            raise ValueError(
                "apply_artifacts_to_reference_package requires a configured existing_code.path."
            )
        reference_package_write_root = resolve_openfisca_repo_root(reference_code_path)
        out["reference_package_write_root"] = str(reference_package_write_root)
        out["artifact_write_plan"] = plan_artifact_writes(
            out["artifacts"],
            reference_package_write_root,
            strategy="update" if overwrite_artifacts else existing_artifact_strategy,
        )
        if not plan_only:
            out["written_artifacts"] = materialize_artifacts(
                out["artifacts"],
                reference_package_write_root,
                strategy=existing_artifact_strategy,
                overwrite=overwrite_artifacts,
            )
    return out

"""Pipeline: from law text to OpenFisca code."""

from openfisca_ai.agents.extractor import ExtractorAgent
from openfisca_ai.agents.coder import CoderAgent


def run_law_to_code(
    law_text: str,
    llm_engine=None,
    country_id: str | None = None,
    use_existing_code_as_reference: bool = False,
) -> dict:
    """
    Run the full pipeline: raw law text -> extracted structure -> code.

    If country_id is set and use_existing_code_as_reference is True, the coder
    receives the path to existing OpenFisca code for that country (from config)
    so it can use it as reference. Same pipeline for any country.

    Returns dict with keys: extracted, code, and optionally country_config, reference_code_path.
    """
    reference_code_path = None
    country_config = None

    if country_id and use_existing_code_as_reference:
        try:
            from openfisca_ai.config_loader import load_country_config, get_reference_code_path
            country_config = load_country_config(country_id)
            ref_path = get_reference_code_path(country_id)
            reference_code_path = str(ref_path) if ref_path and ref_path.exists() else None
        except Exception:
            pass

    extractor = ExtractorAgent(llm_engine=llm_engine)
    coder = CoderAgent(llm_engine=llm_engine)

    extracted = extractor.run(text=law_text)
    result = coder.run(
        extracted=extracted.get("extracted", extracted),
        reference_code_path=reference_code_path,
        country_config=country_config,
    )

    out = {
        "extracted": extracted,
        "code": result.get("code", ""),
    }
    if country_id:
        out["country_id"] = country_id
    if reference_code_path:
        out["reference_code_path"] = reference_code_path
    return out

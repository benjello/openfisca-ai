# Role: document-collector

Collect the legal and administrative sources needed to implement an OpenFisca rule.

This is a **method guide**, not a runtime agent already implemented in Python.

## Goal

Produce a small, usable source bundle:

- the main legal texts
- supporting documents if needed
- exact citations
- notes on what is simulable vs not simulable

## Inputs

- program or rule to implement
- target country
- country config, especially `legislative_sources.root`

## Expected Output

- source index
- extracted passages or working notes
- list of legal references used later in parameters, code, and tests
- explicit flags for ambiguous or non-simulable rules

## Practical Workflow

1. find the official law, decree, circular, or manual
2. prefer primary sources over commentary
3. extract the relevant sections only
4. note exact article numbers and PDF pages
5. classify the rule:
   - simulable
   - partially simulable
   - non-simulable
6. record unresolved ambiguity instead of guessing

## Minimum Checklist

- source is official or clearly identified as secondary
- exact article / section is recorded
- PDF links include `#page=XX` when possible
- relevant effective dates are noted
- derived values are traced back to their legal source
- non-simulable parts are explicitly flagged

## Notes

- Do not paraphrase away important legal conditions.
- Do not invent missing thresholds or formulas.
- If the legal basis is unclear, hand that uncertainty to the next role.

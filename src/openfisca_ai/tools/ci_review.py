#!/usr/bin/env python3
"""AI-powered PR review for CI pipelines.

Reads a pre-digested review (from review-diff) and optionally enriches it
with an LLM review. Falls back gracefully if no API key is available.

Usage:
  python -m openfisca_ai.tools.ci_review --digest review-digest.json --diff pr.diff --output review.md
"""

import json
import os
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]
    digest_path = "review-digest.json"
    digest_md_path = "review-digest.md"
    diff_path = "pr.diff"
    output_path = "review.md"

    i = 0
    while i < len(args):
        if args[i] == "--digest" and i + 1 < len(args):
            digest_path = args[i + 1]
            i += 2
        elif args[i] == "--diff" and i + 1 < len(args):
            diff_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--digest-md" and i + 1 < len(args):
            digest_md_path = args[i + 1]
            i += 2
        else:
            i += 1

    digest_data = json.loads(Path(digest_path).read_text(encoding="utf-8"))
    digest_md = Path(digest_md_path).read_text(encoding="utf-8")
    diff_excerpt = Path(diff_path).read_text(encoding="utf-8")[:5000]

    if digest_data.get("summary", {}).get("is_trivial"):
        Path(output_path).write_text(
            "Changement trivial (documentation/CI) — pas de review approfondie nécessaire.\n",
            encoding="utf-8",
        )
        return

    prompt = (
        "Tu es un relecteur expert OpenFisca. Voici le rapport pré-digéré d'une PR :\n\n"
        f"{digest_md}\n\n"
        f"Extrait du diff :\n```diff\n{diff_excerpt}\n```\n\n"
        "Produis une review concise en français :\n"
        "1. Résumé des changements (2-3 lignes)\n"
        "2. Problèmes détectés\n"
        "3. Suggestions d'amélioration\n"
        "4. Verdict : Approuvé / Changements demandés"
    )

    review_text = None

    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            review_text = response.content[0].text
        except Exception:
            pass

    if not review_text and os.environ.get("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            review_text = response.choices[0].message.content
        except Exception:
            pass

    if not review_text and os.environ.get("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            review_text = response.text
        except Exception:
            pass

    if not review_text:
        review_text = digest_md

    Path(output_path).write_text(review_text, encoding="utf-8")
    print(f"Review written to {output_path}")


if __name__ == "__main__":
    main()

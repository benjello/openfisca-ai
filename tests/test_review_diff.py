"""Tests for review_diff.py."""

from tests.tool_test_helpers import create_modern_country_repo, load_tool_module


review_diff = load_tool_module("review_diff.py", "review_diff_tool")


def test_review_diff_uses_package_layout_for_package_directory(tmp_path):
    repo_path = create_modern_country_repo(tmp_path)
    package_path = repo_path / "openfisca_demo"
    diff = """diff --git a/openfisca_demo/variables/income_tax.py b/openfisca_demo/variables/income_tax.py
--- a/openfisca_demo/variables/income_tax.py
+++ b/openfisca_demo/variables/income_tax.py
@@ -1,1 +1,2 @@
+# changed
"""

    report = review_diff.build_report(diff, package_path)

    assert report["summary"]["change_type"] == "modification formules"
    assert report["validation"]["code"]["valid"] is True

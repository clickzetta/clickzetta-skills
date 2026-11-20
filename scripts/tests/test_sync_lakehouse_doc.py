"""Regression coverage for upstream llms index formats and failed syncs."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
REWRITER = REPO / "scripts/rewrite-llms-urls.sh"


class RewriteLlmsUrlsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.references = Path(temporary.name) / "references"
        self.references.mkdir()

    def rewrite(self, content):
        return subprocess.run(
            [str(REWRITER), str(self.references)],
            input=content, text=True, capture_output=True,
        )

    def test_root_and_legacy_index_urls(self):
        (self.references / "llms-guide.txt").touch()
        for prefix in (
            "https://singdata.com/",
            "https://www.singdata.com/",
            "https://singdata.com/documents/",
            "https://www.singdata.com/documents/",
        ):
            with self.subTest(prefix=prefix):
                content = f"- [User Guide]({prefix}llms-guide.txt)\n  <!-- keywords: SQL, tables -->"
                result = self.rewrite(content)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    result.stdout,
                    "- [User Guide](references/llms-guide.txt)\n  <!-- keywords: SQL, tables -->",
                )

    def test_document_urls_and_sdk_overrides(self):
        (self.references / "Notebook.md").touch()
        (self.references / "python_reference").mkdir()
        (self.references / "python_reference/python-sdk-summary.md").touch()
        result = self.rewrite(
            "[Notebook](https://singdata.com/documents/Notebook)\n"
            "[SDK](https://www.singdata.com/documents/python-sdk-refer)"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "[Notebook](references/Notebook.md)\n"
            "[SDK](references/python_reference/python-sdk-summary.md)",
        )

    def test_content_without_document_urls_succeeds(self):
        for content in ("", "Plain index text.", "[Pricing](https://singdata.com/pricing)"):
            with self.subTest(content=content):
                result = self.rewrite(content)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, content)

    def test_missing_references_directory_reports_error(self):
        self.references.rmdir()
        result = self.rewrite("Plain index text.")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("references dir not found:", result.stderr)


class SyncLakehouseDocTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name)
        shutil.copyfile(REPO / "Makefile", self.project / "Makefile")
        self.source = self.project / "upstream docs"
        self.source.mkdir()
        (self.source / "topic.md").write_text("# Updated topic\n")
        self.skill_dir = self.project / "lakehouse-doc-en"
        self.references = self.skill_dir / "references"
        self.references.mkdir(parents=True)
        (self.references / "existing.md").write_text("Existing reference\n")
        (self.skill_dir / "SKILL.md.template").write_text("# Skill template\n")
        self.skill = self.skill_dir / "SKILL.md"
        self.skill.write_text("Existing complete skill\n")

    def sync(self):
        return subprocess.run(
            ["make", "sync-lakehouse-doc", f"LAKEHOUSE_DOC_SRC={self.source}"],
            cwd=self.project, text=True, capture_output=True,
        )

    def test_missing_index_preserves_existing_output(self):
        result = self.sync()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing llms.txt:", result.stdout)
        self.assertEqual(self.skill.read_text(), "Existing complete skill\n")
        self.assertEqual(
            (self.references / "existing.md").read_text(), "Existing reference\n",
        )

    def test_failed_generation_preserves_skill_and_removes_temporary_file(self):
        (self.source / "llms.txt").write_text("# New index\n")
        scripts = self.project / "scripts"
        scripts.mkdir()
        rewriter = scripts / "rewrite-llms-urls.sh"
        rewriter.write_text("#!/bin/sh\nprintf 'Partial index\\n'\nexit 7\n")
        rewriter.chmod(0o755)
        result = self.sync()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Generating", result.stdout)
        self.assertEqual(self.skill.read_text(), "Existing complete skill\n")
        self.assertEqual(list(self.skill_dir.glob("SKILL.md.tmp.*")), [])


if __name__ == "__main__":
    unittest.main()

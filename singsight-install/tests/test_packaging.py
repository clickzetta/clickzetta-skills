import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SkillPackagingTest(unittest.TestCase):
    def test_pages_index_can_recreate_the_standalone_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts/update-index.py", root / "scripts")
            shutil.copytree(ROOT / "singsight-install", root / "singsight-install")
            subprocess.run(
                [sys.executable, str(root / "scripts/update-index.py")],
                check=True,
                capture_output=True,
            )

            def entry(base):
                index = json.loads((base / ".well-known/skills/index.json").read_text())
                return next(
                    s for s in index["skills"] if s["name"] == "singsight-install"
                )

            local = entry(root)
            subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts/update-index.py"),
                    "--include-docs",
                ],
                check=True,
                capture_output=True,
            )
            self.assertEqual(local, entry(root))
            files = entry(root)["files"]
            self.assertEqual(entry(root), entry(ROOT))
            self.assertTrue(
                {
                    "SKILL.md",
                    "references/codex.md",
                    "scripts/codex/configure.py",
                    "scripts/codex/relay.py",
                    "scripts/codex/requirements.txt",
                }
                <= set(files)
            )
            workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text()
            self.assertIn(
                "run: python3 scripts/update-index.py --include-docs", workflow
            )
            for f in files:
                if f.endswith(".md"):
                    md = (root / "singsight-install" / f).read_text()
                    for link in re.findall(r"\]\(([^)]+)\)", md):
                        if ":" not in link and not link.startswith("#"):
                            target = Path(f).parent / link.split("#")[0]
                            self.assertIn(
                                str(
                                    (root / target)
                                    .resolve()
                                    .relative_to(root.resolve())
                                ),
                                files,
                            )

    def test_lakehouse_reference_routes_to_standalone_entry_point(self):
        guide = (
            ROOT / "lakehouse-doc-en/references/singsight/singsight_install_skill.md"
        ).read_text()
        link = re.search(r"\[canonical install skill\]\(([^)]+)\)", guide)
        self.assertIsNotNone(link)
        self.assertEqual(
            link[1],
            "https://raw.githubusercontent.com/clickzetta/clickzetta-skills/refs/heads/main/singsight-install/SKILL.md",
        )

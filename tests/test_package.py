from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]


class PackageReferences(unittest.TestCase):
    def test_skill_reference_files_ship_with_both_installable_and_frozen_packages(self):
        for package in (ROOT/'skills/xhs-favorites-distiller', ROOT/'evals/frozen-skill'):
            for document in package.rglob('*.md'):
                for link in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                    if '://' in link or link.startswith('#'):
                        continue
                    with self.subTest(document=str(document.relative_to(ROOT)),link=link):
                        self.assertTrue((document.parent/link.split('#')[0]).is_file())


if __name__=='__main__': unittest.main()

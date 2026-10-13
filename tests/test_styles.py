"""The pages' styles come from the tokens in web/styles/tokens.css."""

import glob
import os
import re
import unittest

from calculator.report import SUMMARY_STYLE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLES = os.path.join(ROOT, "web", "styles")
RAW = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b\d*\.?\d+(px|rem)\b")


def light_tokens(css):
    """Custom properties set in the first :root block (the light scheme)."""
    block = re.search(r":root\s*{(.*?)}", css, re.S).group(1)
    return dict(re.findall(r"(--[\w-]+):\s*([^;]+);", block))


class Tokens(unittest.TestCase):
    def test_stylesheets_use_tokens(self):
        for path in glob.glob(os.path.join(STYLES, "*.css")):
            if path.endswith("tokens.css"):
                continue
            with open(path) as f:
                for n, line in enumerate(f, 1):
                    if line.lstrip().startswith("@media") or "top: -10rem" in line:
                        continue  # breakpoints can't be tokens; the skip link hides off-screen
                    self.assertIsNone(RAW.search(line), f"{os.path.basename(path)}:{n}: {line.strip()}")

    def test_pages_carry_no_styles_of_their_own(self):
        with open(os.path.join(ROOT, "web", "template.html")) as f:
            template = f.read()
        self.assertNotIn("<style", template)
        self.assertNotIn("style=", template)
        for path in glob.glob(os.path.join(ROOT, "web", "docs", "**", "*.html"), recursive=True):
            with open(path) as f:
                self.assertNotIn("<style", f.read(), path)

    def test_summary_copy_matches_tokens(self):
        with open(os.path.join(STYLES, "tokens.css")) as f:
            tokens = light_tokens(f.read())
        copy = light_tokens(SUMMARY_STYLE)
        for name, value in copy.items():
            if name == "--font-body":
                continue  # the summary uses the system font on purpose
            self.assertEqual(tokens.get(name), value.strip(), name)


if __name__ == "__main__":
    unittest.main()

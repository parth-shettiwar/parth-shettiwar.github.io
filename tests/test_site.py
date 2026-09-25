"""Dependency-free checks for the static portfolio. Run: python3 -m unittest discover -s tests."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest


ROOT = Path(__file__).resolve().parents[1]
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag: {tag}")
        else:
            self.stack.pop()


class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.page = Page()
        cls.page.feed(cls.source)
        cls.ids = [attrs["id"] for _, attrs in cls.page.elements if "id" in attrs]

    def test_markup_is_balanced(self):
        self.assertEqual(self.page.errors, [])
        self.assertEqual(self.page.stack, [])

    def test_unique_ids_and_navigation_targets(self):
        self.assertEqual([key for key, count in Counter(self.ids).items() if count > 1], [])
        for tag, attrs in self.page.elements:
            if tag == "a" and attrs.get("href", "").startswith("#"):
                self.assertIn(unquote(attrs["href"][1:]), self.ids)
            for label in attrs.get("aria-labelledby", "").split():
                self.assertIn(label, self.ids)

    def test_local_assets_exist(self):
        for tag, attrs in self.page.elements:
            key = "src" if tag == "img" else "href"
            url = urlsplit(attrs.get(key, ""))
            if url.path and not url.scheme and not url.netloc:
                with self.subTest(path=url.path):
                    self.assertTrue((ROOT / unquote(url.path)).is_file())

    def test_images_have_accessible_descriptions(self):
        images = [attrs for tag, attrs in self.page.elements if tag == "img"]
        self.assertEqual(len(images), 25)
        for attrs in images:
            self.assertTrue(attrs.get("alt", "").strip())

    def test_project_collection_preserved(self):
        projects = [attrs for tag, attrs in self.page.elements
                    if tag == "article" and attrs.get("class") == "project"]
        self.assertEqual(len(projects), 24)
        self.assertEqual(sum(tag == "h1" for tag, _ in self.page.elements), 1)
        roles = [attrs for tag, attrs in self.page.elements
                 if tag == "article" and attrs.get("class") == "experience"]
        self.assertEqual(len(roles), 5)

    def test_resume_updates(self):
        for phrase in ["Notifications-AI", "Project Apollo", "Contracts AI", "ICPR 2022",
                       "AAMAS 2024", "SW-NPUCB", "0.7% AUC", "0.5% DAU",
                       "2.5% AUC", "268.9 KB", "4.0/4.0", "9.49/10"]:
            self.assertIn(phrase, self.source)
        for stale in ["second year Masters student", "Under Progress",
                      "1400 Midvale", "parthisultimate@gmail.com"]:
            self.assertNotIn(stale, self.source)

    def test_no_broken_hover_handlers_or_trackers(self):
        for _, attrs in self.page.elements:
            self.assertFalse(any(key.startswith("on") for key in attrs))
        self.assertNotIn("revolvermaps", self.source)
        self.assertNotIn("<iframe", self.source)

    def test_scholar_link_and_decorative_social_icons(self):
        scholar = "https://scholar.google.com/citations?user=Ne4T5JYAAAAJ&hl=en"
        links = [attrs.get("href") for tag, attrs in self.page.elements if tag == "a"]
        self.assertIn(scholar, links)
        self.assertIn("Google Scholar", self.source.split('<section id="contact"', 1)[1])
        icons = [attrs for tag, attrs in self.page.elements
                 if tag == "svg" and attrs.get("class") == "social-icon"]
        self.assertEqual(len(icons), 8)
        for attrs in icons:
            self.assertEqual(attrs.get("aria-hidden"), "true")
            self.assertEqual(attrs.get("focusable"), "false")
        for tag, attrs in self.page.elements:
            if tag == "use":
                self.assertIn(attrs["href"][1:], self.ids)

    def test_dark_mode_support(self):
        css = (ROOT / "stylesheet.css").read_text(encoding="utf-8")
        self.assertIn("prefers-color-scheme: dark", css)
        self.assertIn('html[data-theme="dark"]', css)
        self.assertIn("--bg:", css)
        self.assertIn('class="theme-toggle"', self.source)
        self.assertIn('aria-label="Toggle dark mode"', self.source)
        self.assertIn("localStorage", self.source)
        for symbol in ["icon-sun", "icon-moon"]:
            self.assertIn(f'id="{symbol}"', self.source)
        for tag, attrs in self.page.elements:
            if tag == "use" and attrs.get("href") in ("#icon-sun", "#icon-moon"):
                self.assertIn(attrs["href"][1:], self.ids)
        # The early theme script must run before the stylesheet to avoid a flash.
        self.assertLess(self.source.index("dataset.theme"),
                        self.source.index('<link rel="stylesheet"'))

    def test_hobbies_intro(self):
        for phrase in ["pickleball", "badminton", "rated table tennis player",
                       "30+ US national parks", "15+ countries"]:
            self.assertIn(phrase, self.source)

    def test_legacy_bookmarks_and_reduced_motion(self):
        for old in ["Research Experience", "Projects", "Coding Skills", "Contact"]:
            self.assertIn(f'"{old}":', self.source)
        self.assertIn("Teaching", self.ids)
        self.assertIn("Awards", self.ids)
        css = (ROOT / "stylesheet.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(":focus-visible", css)


if __name__ == "__main__":
    unittest.main()

"""Faktaboksen 'Det ved vi' grupperes uden at ændre fakta eller links."""
import re
import unittest
from html import unescape
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "content" / "artikler"
FAKTA_RE = build.FAKTA_RE
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)")


def visible(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(text)).strip()


class FactboxTests(unittest.TestCase):
    def test_viden_groups_and_keeps_link(self):
        html = build.markdown(
            ":::fakta Det ved vi – og det ved vi ikke\n"
            "- **Vi ved:** Første faktum med [Rådet](https://www.consilium.europa.eu/da/).\n"
            "- **Vi ved ikke:** Andet faktum, stadig åbent.\n"
            ":::\n"
        )
        self.assertIn('class="factbox factbox-viden"', html)
        self.assertIn('class="viden-grid viden-pair"', html)
        self.assertIn('class="viden-group viden-ved"', html)
        self.assertIn('class="viden-group viden-ikke"', html)
        self.assertIn(">Vi ved</h3>", html)
        self.assertIn(">Vi ved ikke</h3>", html)
        self.assertNotIn("<strong>Vi ved:</strong>", html)
        self.assertIn("Første faktum med", html)
        self.assertIn('href="https://www.consilium.europa.eu/da/"', html)
        self.assertIn('rel="noopener" target="_blank"', html)
        self.assertIn('aria-labelledby="fakta-0"', html)

    def test_paragraph_variant_and_slash_title(self):
        html = build.markdown(
            ":::fakta Det ved vi / Det ved vi ikke\n"
            "**Det ved vi:** EU forhandler med Storbritannien.\n"
            "\n"
            "**Det ved vi ikke:** Om regeringen vil forsøge en særaftale.\n"
            ":::\n"
        )
        self.assertIn('class="viden-group viden-ved"', html)
        self.assertIn('class="viden-group viden-ikke"', html)
        self.assertIn("<p>EU forhandler med Storbritannien.</p>", html)
        self.assertNotIn("<ul>", html)

    def test_other_factbox_stays_generic(self):
        html = build.markdown(
            ":::fakta Sådan stemte de danske MEP'er 18. juni\n"
            "- **For:** Majbritt Birkholm (DF).\n"
            "- **Imod:** Stine Bosse (M).\n"
            ":::\n"
        )
        self.assertIn('<aside class="factbox">', html)
        self.assertNotIn("factbox-viden", html)
        self.assertIn("<strong>For:</strong>", html)
        self.assertIn("<strong>Imod:</strong>", html)

    def test_update_note_and_internal_link(self):
        html = build.markdown(
            ":::fakta Det ved vi – og det ved vi ikke\n"
            "- **Vi ved:** Se [sagen](/artikler/eu-inc-28-ordning-regeringen/).\n"
            "- **Opdatering:** Rådet bekræfter lukningen.\n"
            ":::\n"
        )
        self.assertIn('class="viden-group viden-ved"', html)
        self.assertIn('class="viden-group viden-note"', html)
        self.assertNotIn("viden-pair", html)
        self.assertIn('href="/artikler/eu-inc-28-ordning-regeringen/"', html)
        self.assertNotIn('target="_blank"', html)

    def test_unstructured_viden_box_falls_back(self):
        html = build.markdown(
            ":::fakta Det ved vi – og det ved vi ikke\n"
            "En løs sætning uden mærke.\n"
            ":::\n"
        )
        self.assertIn('<aside class="factbox">', html)
        self.assertNotIn("factbox-viden", html)
        self.assertIn("En løs sætning uden mærke.", html)

    def test_every_published_box_keeps_facts_and_urls(self):
        viden = generic = 0
        for path in sorted(ARTICLES.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for match in FAKTA_RE.finditer(text):
                title = match.group(1).strip() or "Fakta"
                body = match.group(2)
                html = build.markdown(f":::fakta {title}\n{body}\n:::\n")
                aside = html[html.find("<aside"):html.find("</aside>") + len("</aside>")]
                for _, url in LINK_RE.findall(body):
                    self.assertIn(f'href="{url}"', aside, path.name)
                shown = visible(aside)
                self.assertIn(title, shown, path.name)
                is_viden = "factbox-viden" in aside
                if build.VIDEN_TITLE_RE.match(title):
                    self.assertTrue(is_viden, path.name)
                    viden += 1
                    for raw in body.splitlines():
                        line = raw.strip()
                        if not line:
                            continue
                        item = build.VIDEN_ITEM_RE.match(line)
                        self.assertIsNotNone(item, f"{path.name}: {line[:80]}")
                        label = item.group("label").strip()
                        rest = item.group("rest").strip()
                        self.assertIn(label, shown, path.name)
                        rest_visible = visible(f"<p>{build.inline_md(rest)}</p>")
                        self.assertIn(rest_visible, shown, path.name)
                else:
                    self.assertFalse(is_viden, path.name)
                    generic += 1
        self.assertGreater(viden, 100)
        self.assertGreater(generic, 10)


if __name__ == "__main__":
    unittest.main()

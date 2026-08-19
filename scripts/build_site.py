#!/usr/bin/env python3
"""Validate the public module catalog and build a dependency-free site."""

from __future__ import annotations

import argparse
import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "modules.json"
TEMPLATE = ROOT / "site" / "template.html"
OUTPUT = ROOT / "_site"
EXPECTED_MODULES = {"trainings", "kpi", "protocols", "smm"}


def load_catalog() -> dict:
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    modules = payload.get("modules")
    gallery = payload.get("gallery")
    if not isinstance(modules, list) or not isinstance(gallery, list):
        raise ValueError("modules and gallery must be lists")

    module_ids = [item.get("id") for item in modules]
    if len(module_ids) != len(set(module_ids)):
        raise ValueError("module ids must be unique")
    if set(module_ids) != EXPECTED_MODULES:
        raise ValueError(
            f"catalog modules must be {sorted(EXPECTED_MODULES)}, got "
            f"{sorted(module_ids)}"
        )

    required = {
        "id", "number", "icon", "title", "eyebrow", "summary",
        "features", "outcome", "accent",
    }
    for module in modules:
        missing = required - module.keys()
        if missing:
            raise ValueError(f"module {module.get('id')} misses {sorted(missing)}")
        if not module["features"]:
            raise ValueError(f"module {module['id']} has no features")

    for item in gallery:
        image = ROOT / "site" / item["image"]
        if not image.is_file():
            raise ValueError(f"gallery image does not exist: {image}")
    return payload


def icon(name: str) -> str:
    paths = {
        "calendar": '<path d="M7 3v3M17 3v3M4 9h16M6 5h12a2 2 0 0 1 2 2v12H4V7a2 2 0 0 1 2-2Z"/><path d="m8 14 2 2 5-5"/>',
        "chart": '<path d="M4 19V9M10 19V5M16 19v-7M22 19H2"/><path d="m4 7 6-4 6 6 5-5"/>',
        "clipboard": '<path d="M9 5H6a2 2 0 0 0-2 2v13h16V7a2 2 0 0 0-2-2h-3"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="m8 13 2 2 5-5"/>',
        "spark": '<path d="m12 2 1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2Z"/><path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z"/>',
    }
    return (
        '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths[name]}</svg>'
    )


def render_modules(modules: list[dict]) -> tuple[str, str]:
    cards = []
    sections = []
    for module in modules:
        features = "".join(
            f"<li>{escape(feature)}</li>" for feature in module["features"]
        )
        cards.append(
            f'<a class="module-card accent-{module["accent"]}" '
            f'href="#{module["id"]}">'
            f'<span class="module-card__number">{escape(module["number"])}</span>'
            f'<span class="module-card__icon">{icon(module["icon"])}</span>'
            f'<strong>{escape(module["title"])}</strong>'
            f'<span>{escape(module["summary"])}</span>'
            '<span class="module-card__link">Смотреть возможности →</span>'
            '</a>'
        )
        sections.append(
            f'<article class="module-detail accent-{module["accent"]}" '
            f'id="{module["id"]}">'
            '<div class="module-detail__heading">'
            f'<span class="module-detail__icon">{icon(module["icon"])}</span>'
            '<div>'
            f'<span class="eyebrow">Модуль {escape(module["number"])}</span>'
            f'<h2>{escape(module["title"])}</h2>'
            f'<p>{escape(module["eyebrow"])}</p>'
            '</div></div>'
            '<div class="module-detail__body">'
            f'<p class="module-detail__summary">{escape(module["summary"])}</p>'
            f'<ul>{features}</ul>'
            '<div class="outcome"><span>Результат для клуба</span>'
            f'<p>{escape(module["outcome"])}</p></div>'
            '</div></article>'
        )
    return "".join(cards), "".join(sections)


def render_gallery(items: list[dict]) -> str:
    return "".join(
        '<button class="gallery-card" type="button" '
        f'data-image="{escape(item["image"])}" '
        f'data-title="{escape(item["title"])}">'
        f'<img src="{escape(item["image"])}" alt="Визуальный стиль '
        f'{escape(item["title"])}" loading="lazy">'
        '<span class="gallery-card__copy">'
        f'<strong>{escape(item["title"])}</strong>'
        f'<span>{escape(item["caption"])}</span>'
        '</span><span class="gallery-card__zoom">Развернуть ↗</span>'
        '</button>'
        for item in items
    )


def build() -> None:
    payload = load_catalog()
    cards, sections = render_modules(payload["modules"])
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{MODULE_CARDS}}", cards)
    html = html.replace("{{MODULE_SECTIONS}}", sections)
    html = html.replace("{{GALLERY}}", render_gallery(payload["gallery"]))

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    (OUTPUT / "index.html").write_text(html, encoding="utf-8")
    shutil.copytree(ROOT / "site" / "assets", OUTPUT / "assets")
    shutil.copy2(ROOT / "site" / "styles.css", OUTPUT / "styles.css")
    shutil.copy2(ROOT / "site" / "app.js", OUTPUT / "app.js")
    (OUTPUT / ".nojekyll").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="validate and build the site"
    )
    parser.parse_args()
    build()
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    main()

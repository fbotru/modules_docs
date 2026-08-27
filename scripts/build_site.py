#!/usr/bin/env python3
"""Validate and build the dependency-free SportsSmartBot website."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "data" / "site.json"
TEMPLATE = ROOT / "site" / "template.html"
STYLES = ROOT / "site" / "styles.css"
OUTPUT = ROOT / "_site"

TELEGRAM_URL = "https://t.me/ReddysAdmin_bot"
EXPECTED_CAPABILITIES = {
    "matches",
    "team",
    "finance",
    "development",
    "media",
}
EXPECTED_TIERS = ["basic", "standard", "maximum"]
EXPECTED_STYLES = ["modern-heritage", "street-calcio", "tactical-grid"]
FORBIDDEN_KEYS = {
    "price",
    "currency",
    "testimonial",
    "metrics",
    "integrations",
    "legal",
}
FORBIDDEN_COPY = {
    "4 модуля",
    "четыре модуля",
    "начните с одного модуля",
    "digital football operations",
    "оставляем футбол",
    "с помощью ии",
    "генерация текстов",
}

# Widths are encoded in filenames so the static HTML can expose honest srcsets.
MEDIA = {
    "product-platform": (720, 1280, 1280, 853),
    "tier-basic": (640, 1120, 1120, 840),
    "tier-standard": (640, 1120, 1120, 840),
    "tier-maximum": (640, 1120, 1120, 840),
    "capabilities-grid": (960, 1600, 1600, 900),
    "smm-match-announce": (640, 1000, 1000, 1000),
    "smm-match-result-v2": (640, 1000, 1000, 1000),
    "smm-mvp": (560, 900, 900, 1125),
    "smm-standings-v2": (960, 1440, 1440, 810),
    "style-modern-heritage": (720, 1280, 1280, 801),
    "style-street-calcio": (720, 1280, 1280, 819),
    "style-tactical-grid": (720, 1280, 1280, 801),
    "workflow": (960, 1600, 1600, 640),
    "cta-team-v3": (960, 1600, 1600, 686),
}


def escaped(value: object) -> str:
    return escape(str(value), quote=True)


def require_keys(item: dict, required: set[str], label: str) -> None:
    missing = required - item.keys()
    if missing:
        raise ValueError(f"{label} misses {sorted(missing)}")


def unique_ids(items: list[dict], label: str) -> list[str]:
    ids = [item.get("id") for item in items]
    if any(not isinstance(item_id, str) or not item_id for item_id in ids):
        raise ValueError(f"{label} ids must be non-empty strings")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label} ids must be unique")
    return ids


def walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def validate_site_settings(payload: dict) -> None:
    site = payload["site"]
    require_keys(
        site,
        {"name", "short_name", "positioning", "tagline", "telegram_url"},
        "site",
    )
    if site["name"] != "SportsSmartBot":
        raise ValueError("site name must be SportsSmartBot")
    if site["telegram_url"] != TELEGRAM_URL:
        raise ValueError("the existing Telegram URL must be preserved")


def validate_problem_results(payload: dict) -> None:
    problems = payload["problem_results"]
    if not isinstance(problems, list) or len(problems) != 4:
        raise ValueError("problem_results must contain four transformations")
    unique_ids(problems, "problem_results")
    for item in problems:
        require_keys(
            item,
            {"id", "number", "source", "result", "text"},
            f"problem result {item.get('id')}",
        )


def validate_capabilities(payload: dict) -> None:
    capabilities = payload["capability_groups"]
    if not isinstance(capabilities, list):
        raise ValueError("capability_groups must be a list")
    capability_ids = unique_ids(capabilities, "capability groups")
    if set(capability_ids) != EXPECTED_CAPABILITIES:
        raise ValueError("capability groups must match the five product areas")
    for item in capabilities:
        require_keys(
            item,
            {"id", "number", "title", "summary", "features"},
            f"capability {item.get('id')}",
        )
        if not item["features"]:
            raise ValueError(f"capability {item['id']} has no features")


def validate_tiers(payload: dict) -> None:
    tiers = payload["tiers"]
    if not isinstance(tiers, list):
        raise ValueError("tiers must be a list")
    tier_ids = unique_ids(tiers, "tiers")
    if tier_ids != EXPECTED_TIERS:
        raise ValueError(f"tiers must be ordered as {EXPECTED_TIERS}")
    if [tier["inherits"] for tier in tiers] != [None, "basic", "standard"]:
        raise ValueError("tier inheritance must be basic → standard → maximum")
    recommended = [tier["id"] for tier in tiers if tier.get("recommended")]
    if recommended != ["standard"]:
        raise ValueError("Standard must be the only recommended tier")
    for tier in tiers:
        require_keys(
            tier,
            {
                "id",
                "number",
                "name",
                "name_genitive",
                "eyebrow",
                "summary",
                "inherits",
                "recommended",
                "image",
                "image_alt",
                "features",
            },
            f"tier {tier.get('id')}",
        )
        if tier["image"] not in MEDIA:
            raise ValueError(f"unknown tier image: {tier['image']}")
        if not tier["features"]:
            raise ValueError(f"tier {tier['id']} has no features")


def validate_comparison(payload: dict) -> None:
    comparison = payload["comparison"]
    if not isinstance(comparison, list) or not comparison:
        raise ValueError("comparison must be a non-empty list")
    valid_statuses = {"included", "absent", "roadmap"}
    for index, row in enumerate(comparison, start=1):
        require_keys(row, {"label", *EXPECTED_TIERS}, f"comparison row {index}")
        statuses = {row[tier_id] for tier_id in EXPECTED_TIERS}
        if not statuses <= valid_statuses:
            raise ValueError(f"comparison row {index} has an invalid status")


def validate_smm(payload: dict) -> None:
    smm = payload["smm"]
    require_keys(smm, {"styles", "gallery", "levels"}, "smm")
    style_ids = unique_ids(smm["styles"], "smm styles")
    if style_ids != EXPECTED_STYLES:
        raise ValueError(f"SMM styles must be ordered as {EXPECTED_STYLES}")
    for item in smm["styles"]:
        require_keys(
            item,
            {"id", "title", "caption", "image", "image_alt"},
            f"smm style {item.get('id')}",
        )
        if item["image"] not in MEDIA:
            raise ValueError(f"unknown style image: {item['image']}")
    gallery_ids = unique_ids(smm["gallery"], "smm gallery")
    if set(gallery_ids) != {"announce", "result", "mvp", "standings"}:
        raise ValueError("smm gallery must cover the four supplied scenes")
    for item in smm["gallery"]:
        require_keys(
            item,
            {"id", "title", "level", "caption", "image", "image_alt"},
            f"smm gallery {item.get('id')}",
        )
        if item["image"] not in MEDIA:
            raise ValueError(f"unknown SMM image: {item['image']}")
    if [item.get("tier") for item in smm["levels"]] != [
        "Базовая",
        "Стандартная",
        "Максимум",
    ]:
        raise ValueError("SMM growth must follow the three subscription levels")


def validate_workflow_and_automation(payload: dict) -> None:
    workflow = payload["workflow"]
    if not isinstance(workflow, list) or len(workflow) != 4:
        raise ValueError("workflow must contain four steps")
    automation = payload["automation"]
    if not isinstance(automation, list) or len(automation) != 4:
        raise ValueError("automation must contain four club processes")
    for index, item in enumerate(automation, start=1):
        require_keys(item, {"number", "title", "text"}, f"automation {index}")


def validate_content_copy(payload: dict) -> None:
    copy = json.dumps(payload, ensure_ascii=False).casefold()
    found = [phrase for phrase in FORBIDDEN_COPY if phrase in copy]
    if found:
        raise ValueError(f"obsolete copy found: {sorted(found)}")


def load_content() -> dict:
    payload = json.loads(CONTENT.read_text(encoding="utf-8"))
    required_sections = {
        "site",
        "problem_results",
        "capability_groups",
        "tiers",
        "comparison",
        "smm",
        "workflow",
        "automation",
    }
    require_keys(payload, required_sections, "site content")
    if "modules" in payload:
        raise ValueError("the obsolete module catalog is not supported")
    forbidden = FORBIDDEN_KEYS & walk_keys(payload)
    if forbidden:
        raise ValueError(f"unsupported commercial fields: {sorted(forbidden)}")

    validators = (
        validate_site_settings,
        validate_problem_results,
        validate_capabilities,
        validate_tiers,
        validate_comparison,
        validate_smm,
        validate_workflow_and_automation,
        validate_content_copy,
    )
    for validator in validators:
        validator(payload)
    return payload


def picture(
    asset: str,
    alt: str,
    class_name: str,
    sizes: str,
) -> str:
    small, large, width, height = MEDIA[asset]
    return (
        f'<picture class="{escaped(class_name)}">'
        '<source type="image/avif" '
        f'srcset="assets/media/{asset}-{small}.avif {small}w, '
        f'assets/media/{asset}-{large}.avif {large}w" '
        f'sizes="{escaped(sizes)}">'
        '<source type="image/webp" '
        f'srcset="assets/media/{asset}-{small}.webp {small}w, '
        f'assets/media/{asset}-{large}.webp {large}w" '
        f'sizes="{escaped(sizes)}">'
        f'<img src="assets/media/{asset}-{large}.webp" '
        f'width="{width}" height="{height}" alt="{escaped(alt)}" '
        'loading="lazy" decoding="async" data-media-role="content">'
        '</picture>'
    )


def render_problem_results(items: list[dict]) -> str:
    parts = []
    for item in items:
        parts.append(
            f'<li class="transformation" id="shift-{escaped(item["id"])}">'
            '<span class="transformation__number">'
            f'{escaped(item["number"])}</span>'
            '<div class="transformation__pair">'
            f'<span><small>Было</small>{escaped(item["source"])}</span>'
            '<i aria-hidden="true">→</i>'
            f'<span><small>Стало</small>{escaped(item["result"])}</span>'
            '</div>'
            f'<p>{escaped(item["text"])}</p>'
            '</li>'
        )
    return "".join(parts)


def render_capabilities(items: list[dict]) -> str:
    parts = []
    for item in items:
        features = "".join(
            f'<li>{escaped(feature)}</li>' for feature in item["features"]
        )
        parts.append(
            '<article class="capability" '
            f'id="capability-{escaped(item["id"])}">'
            f'<span class="capability__number">{escaped(item["number"])}</span>'
            '<div class="capability__title">'
            f'<h3>{escaped(item["title"])}</h3>'
            f'<p>{escaped(item["summary"])}</p>'
            '</div>'
            f'<ul>{features}</ul>'
            '</article>'
        )
    return "".join(parts)


def render_tiers(tiers: list[dict], telegram_url: str) -> str:
    names = {tier["id"]: tier["name_genitive"] for tier in tiers}
    parts = []
    for tier in tiers:
        recommended = (
            '<span class="tier__recommended">Рекомендуем</span>'
            if tier["recommended"]
            else ""
        )
        inherited = ""
        if tier["inherits"]:
            parent_id = tier["inherits"]
            inherited = (
                '<p class="tier__inherit">'
                f'Всё из <a href="#tier-{escaped(parent_id)}">'
                f'{escaped(names[parent_id])}</a>, а также:</p>'
            )
        features = "".join(
            f'<li>{escaped(feature)}</li>' for feature in tier["features"]
        )
        parts.append(
            f'<article class="tier tier--{escaped(tier["id"])}" '
            f'id="tier-{escaped(tier["id"])}">'
            + picture(
                tier["image"],
                tier["image_alt"],
                "tier__picture",
                "(max-width: 760px) 100vw, 34vw",
            )
            + '<div class="tier__body">'
            + '<header class="tier__header">'
            + f'<span class="tier__number">{escaped(tier["number"])}</span>'
            + '<div>'
            + f'<p class="overline">{escaped(tier["eyebrow"])}</p>'
            + f'<h3>{escaped(tier["name"])}</h3>'
            + '</div>'
            + recommended
            + '</header>'
            + f'<p class="tier__summary">{escaped(tier["summary"])}</p>'
            + inherited
            + f'<ul class="feature-list">{features}</ul>'
            + f'<a class="text-link" href="{escaped(telegram_url)}" '
            + 'target="_blank" rel="noopener noreferrer">'
            + 'Обсудить подключение <span aria-hidden="true">↗</span></a>'
            + '</div></article>'
        )
    return "".join(parts)


def status_cell(status: str) -> str:
    if status == "included":
        return (
            '<span class="status status--yes">'
            '<b aria-hidden="true">✓</b> Есть</span>'
        )
    if status == "roadmap":
        return '<span class="status status--roadmap">Новые возможности</span>'
    return (
        '<span class="status status--no"><b aria-hidden="true">—</b>'
        '<span class="visually-hidden">Нет</span></span>'
    )


def render_comparison(rows: list[dict], tiers: list[dict]) -> tuple[str, str]:
    body = []
    for row in rows:
        body.append(
            '<tr>'
            f'<th scope="row">{escaped(row["label"])}</th>'
            + "".join(
                f'<td>{status_cell(row[tier["id"]])}</td>' for tier in tiers
            )
            + '</tr>'
        )
    table = (
        '<div class="comparison-table" tabindex="0" '
        'aria-label="Таблица сравнения подписок">'
        '<table><caption>Что входит в каждый уровень</caption><thead><tr>'
        '<th scope="col">Возможность</th>'
        + "".join(
            '<th scope="col"'
            + (' class="is-recommended"' if tier["recommended"] else "")
            + f'>{escaped(tier["name"])}'
            + ('<span>Рекомендуем</span>' if tier["recommended"] else "")
            + '</th>'
            for tier in tiers
        )
        + '</tr></thead><tbody>'
        + "".join(body)
        + '</tbody></table></div>'
    )

    mobile = []
    names = {tier["id"]: tier["name_genitive"] for tier in tiers}
    for tier in tiers:
        inherited = ""
        if tier["inherits"]:
            inherited = (
                f'<p>Всё из {escaped(names[tier["inherits"]])}, '
                'а также:</p>'
            )
        features = "".join(
            f'<li>{escaped(feature)}</li>' for feature in tier["features"]
        )
        badge = '<span>Рекомендуем</span>' if tier["recommended"] else ""
        open_attr = " open" if tier["recommended"] else ""
        mobile.append(
            f'<details class="mobile-tier mobile-tier--{escaped(tier["id"])}"'
            f'{open_attr}><summary><b>{escaped(tier["name"])}</b>{badge}</summary>'
            f'<div>{inherited}<ul>{features}</ul></div></details>'
        )
    return table, "".join(mobile)


def render_smm_gallery(items: list[dict]) -> str:
    parts = []
    for item in items:
        _, large, width, height = MEDIA[item["image"]]
        label = f'{item["title"]}. {item["caption"]}'
        parts.append(
            f'<button class="smm-card smm-card--{escaped(item["id"])}" '
            'type="button" aria-haspopup="dialog" '
            f'aria-label="Открыть: {escaped(label)}" '
            f'data-image="assets/media/{escaped(item["image"])}-{large}.webp" '
            f'data-title="{escaped(item["title"])}" '
            f'data-width="{width}" data-height="{height}">'
            + picture(
                item["image"],
                item["image_alt"],
                "smm-card__picture",
                "(max-width: 760px) 92vw, 48vw",
            )
            + '<span class="smm-card__copy">'
            + f'<small>{escaped(item["level"])}</small>'
            + f'<strong>{escaped(item["title"])}</strong>'
            + f'<span>{escaped(item["caption"])}</span>'
            + '</span><span class="smm-card__open" aria-hidden="true">↗</span>'
            + '</button>'
        )
    return "".join(parts)


def render_style_gallery(items: list[dict]) -> str:
    parts = []
    for item in items:
        _, large, width, height = MEDIA[item["image"]]
        label = f'{item["title"]}. {item["caption"]}'
        parts.append(
            f'<button class="style-card style-card--{escaped(item["id"])}" '
            'type="button" aria-haspopup="dialog" '
            f'aria-label="Открыть стиль: {escaped(label)}" '
            f'data-image="assets/media/{escaped(item["image"])}-{large}.webp" '
            f'data-title="{escaped(item["title"])}" '
            f'data-width="{width}" data-height="{height}">'
            + picture(
                item["image"],
                item["image_alt"],
                "style-card__picture",
                "(max-width: 760px) 92vw, 31vw",
            )
            + '<span class="style-card__copy">'
            + '<small>Визуальная система</small>'
            + f'<strong>{escaped(item["title"])}</strong>'
            + f'<span>{escaped(item["caption"])}</span>'
            + '</span><span class="style-card__open" aria-hidden="true">↗</span>'
            + '</button>'
        )
    return "".join(parts)


def render_smm_levels(items: list[dict]) -> str:
    return "".join(
        '<li>'
        f'<span>{escaped(item["number"])}</span>'
        '<div>'
        f'<p>{escaped(item["tier"])}</p>'
        f'<h3>{escaped(item["title"])}</h3>'
        f'<p>{escaped(item["text"])}</p>'
        '</div></li>'
        for item in items
    )


def render_workflow(items: list[dict]) -> str:
    return "".join(
        '<li>'
        f'<span>{escaped(item["number"])}</span>'
        '<div>'
        f'<h3>{escaped(item["title"])}</h3>'
        f'<p>{escaped(item["text"])}</p>'
        '</div></li>'
        for item in items
    )


def render_automation(items: list[dict]) -> str:
    return "".join(
        '<li>'
        f'<span>{escaped(item["number"])}</span>'
        f'<h3>{escaped(item["title"])}</h3>'
        f'<p>{escaped(item["text"])}</p>'
        '</li>'
        for item in items
    )


class SiteHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.anchors: list[tuple[str, dict[str, str]]] = []
        self.references: list[str] = []
        self.images: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a":
            self.anchors.append((values.get("href", ""), values))
        if tag == "img":
            self.images.append(values)
        if tag == "button":
            self.buttons.append(values)
        for attribute in ("src", "href", "data-image"):
            if values.get(attribute):
                self.references.append(values[attribute])
        if values.get("srcset"):
            for candidate in values["srcset"].split(","):
                self.references.append(candidate.strip().split()[0])

    handle_startendtag = handle_starttag


def is_local_reference(reference: str) -> bool:
    return not reference.startswith(("#", "http://", "https://", "data:"))


def validate_html_copy(html: str) -> None:
    if re.search(r"{{[A-Z_]+}}", html):
        raise ValueError("unresolved template placeholder")
    lowered = html.casefold()
    found = [phrase for phrase in FORBIDDEN_COPY if phrase in lowered]
    if found:
        raise ValueError(f"obsolete copy found in HTML: {sorted(found)}")
    if "assets/generated/" in html or ".png" in html:
        raise ValueError(
            "source PNGs must not be served by the production HTML"
        )


def validate_links(parser: SiteHTMLParser, telegram_url: str) -> None:
    if len(parser.ids) != len(set(parser.ids)):
        raise ValueError("HTML ids must be unique")
    ids = set(parser.ids)
    telegram_ctas = 0
    for href, attrs in parser.anchors:
        if not href or href == "#":
            raise ValueError("links must have a real destination")
        if href.startswith("#") and href[1:] not in ids:
            raise ValueError(f"missing anchor target: {href}")
        if href.startswith("http"):
            if href != telegram_url:
                raise ValueError(f"unexpected external CTA: {href}")
            telegram_ctas += 1
        if attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").split())
            if not {"noopener", "noreferrer"} <= rel:
                raise ValueError(f"unsafe target=_blank link: {href}")
    if telegram_ctas < 4:
        raise ValueError(
            "the page must expose Telegram CTAs across the journey"
        )


def validate_image_markup(parser: SiteHTMLParser) -> None:
    for image in parser.images:
        if "alt" not in image:
            raise ValueError(f"image misses alt: {image.get('src')}")
        if not image.get("width", "").isdigit() or not image.get(
            "height", ""
        ).isdigit():
            raise ValueError(
                f"image misses numeric dimensions: {image.get('src')}"
            )
        role = image.get("data-media-role")
        if role == "content" and image.get("loading") != "lazy":
            raise ValueError(
                f"below-fold image must be lazy: {image.get('src')}"
            )
        if role == "hero" and image.get("loading") == "lazy":
            raise ValueError("hero image must not be lazy-loaded")

    for button in parser.buttons:
        if button.get("type") != "button":
            raise ValueError("all buttons must declare type=button")


def validate_local_references(parser: SiteHTMLParser) -> None:
    for reference in parser.references:
        if reference.startswith("/"):
            raise ValueError(
                f"root-relative URL breaks GitHub Pages: {reference}"
            )
        if not is_local_reference(reference):
            continue
        local = reference.split("?", 1)[0].split("#", 1)[0]
        if not (ROOT / "site" / local).is_file():
            raise ValueError(f"missing local reference: {reference}")


def validate_html(html: str, telegram_url: str) -> None:
    validate_html_copy(html)
    parser = SiteHTMLParser()
    parser.feed(html)
    validate_links(parser, telegram_url)
    validate_image_markup(parser)
    validate_local_references(parser)


def validate_responsive_assets(media_dir: Path) -> None:
    for asset, (small, large, _, _) in MEDIA.items():
        for width in (small, large):
            for extension in ("avif", "webp"):
                path = media_dir / f"{asset}-{width}.{extension}"
                if not path.is_file():
                    raise ValueError(f"missing responsive image: {path}")


def validate_required_assets(media_dir: Path) -> None:
    required = [
        ROOT / "site" / "assets" / "brand-crest.svg",
        media_dir / "hero-desktop-960.avif",
        media_dir / "hero-desktop-1600.avif",
        media_dir / "hero-desktop-960.webp",
        media_dir / "hero-desktop-1600.webp",
        media_dir / "hero-mobile-720.avif",
        media_dir / "hero-mobile-1120.avif",
        media_dir / "hero-mobile-720.webp",
        media_dir / "hero-mobile-1120.webp",
        media_dir / "texture-640.webp",
        media_dir / "og-cover-1200.jpg",
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"missing production assets: {missing}")


def validate_css_assets() -> None:
    css = STYLES.read_text(encoding="utf-8")
    if "assets/generated/" in css or ".png" in css:
        raise ValueError("source PNGs must not be served by CSS")
    for reference in re.findall(r"url\(['\"]?([^)'\"]+)", css):
        if reference.startswith(("data:", "http://", "https://")):
            continue
        if reference.startswith("/"):
            raise ValueError(f"root-relative CSS asset: {reference}")
        if not (ROOT / "site" / reference).is_file():
            raise ValueError(f"missing CSS asset: {reference}")


def validate_assets() -> None:
    media_dir = ROOT / "site" / "assets" / "media"
    validate_responsive_assets(media_dir)
    validate_required_assets(media_dir)
    validate_css_assets()


def render(payload: dict) -> str:
    tiers = payload["tiers"]
    comparison, mobile_comparison = render_comparison(
        payload["comparison"], tiers
    )
    replacements = {
        "{{PROBLEM_RESULTS}}": render_problem_results(
            payload["problem_results"]
        ),
        "{{CAPABILITIES}}": render_capabilities(
            payload["capability_groups"]
        ),
        "{{PLATFORM_PICTURE}}": picture(
            "product-platform",
            "Три экрана SportsSmartBot: опрос, состав, статистика и медиа.",
            "platform__picture",
            "(max-width: 760px) 94vw, 52vw",
        ),
        "{{CAPABILITIES_PICTURE}}": picture(
            "capabilities-grid",
            "Единая схема опросов, составов, тренировок, чеков и статистики.",
            "capability-visual__picture",
            "(max-width: 760px) 94vw, 82vw",
        ),
        "{{TIERS}}": render_tiers(tiers, payload["site"]["telegram_url"]),
        "{{COMPARISON}}": comparison,
        "{{MOBILE_COMPARISON}}": mobile_comparison,
        "{{STYLE_GALLERY}}": render_style_gallery(payload["smm"]["styles"]),
        "{{SMM_GALLERY}}": render_smm_gallery(payload["smm"]["gallery"]),
        "{{SMM_LEVELS}}": render_smm_levels(payload["smm"]["levels"]),
        "{{WORKFLOW_PICTURE}}": picture(
            "workflow",
            "Клубный процесс от календаря и опроса до аналитики и публикации.",
            "workflow__picture",
            "(max-width: 760px) 94vw, 82vw",
        ),
        "{{WORKFLOW_STEPS}}": render_workflow(payload["workflow"]),
        "{{AUTOMATION}}": render_automation(payload["automation"]),
        "{{CTA_PICTURE}}": picture(
            "cta-team-v3",
            "Спортсмены из разных командных видов спорта "
            "собрались перед игрой.",
            "closing__picture",
            "100vw",
        ),
        "{{TELEGRAM_URL}}": payload["site"]["telegram_url"],
    }
    html = TEMPLATE.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html


def build() -> None:
    payload = load_content()
    validate_assets()
    html = render(payload)
    validate_html(html, payload["site"]["telegram_url"])

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "assets").mkdir(parents=True)
    (OUTPUT / "index.html").write_text(html, encoding="utf-8")
    shutil.copy2(STYLES, OUTPUT / "styles.css")
    shutil.copy2(ROOT / "site" / "app.js", OUTPUT / "app.js")
    shutil.copy2(
        ROOT / "site" / "assets" / "brand-crest.svg",
        OUTPUT / "assets" / "brand-crest.svg",
    )
    shutil.copytree(
        ROOT / "site" / "assets" / "media",
        OUTPUT / "assets" / "media",
    )
    (OUTPUT / ".nojekyll").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the content, HTML and assets while building",
    )
    parser.parse_args()
    build()
    print(f"Built and validated {OUTPUT}")


if __name__ == "__main__":
    main()

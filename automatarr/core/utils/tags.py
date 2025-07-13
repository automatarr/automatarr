from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import tempfile
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional, Tuple

import requests

from automatarr.core.config import config
from automatarr.core.titles.episode import Episode
from automatarr.core.titles.movie import Movie
from automatarr.core.titles.title import Title

STRIP_RE = re.compile(r"[^a-z0-9]+", re.I)
YEAR_RE = re.compile(r"\s*\(?[12][0-9]{3}\)?$")
HEADERS = {"User-Agent": "automatarr-tags/1.0"}


log = logging.getLogger("TAGS")


def _api_key() -> Optional[str]:
    return config.tmdb_api_key or os.getenv("TMDB_API_KEY")


def _clean(s: str) -> str:
    return STRIP_RE.sub("", s).lower()


def _strip_year(s: str) -> str:
    return YEAR_RE.sub("", s).strip()


def fuzzy_match(a: str, b: str, threshold: float = 0.8) -> bool:
    """Return True if ``a`` and ``b`` are a close match."""

    ratio = SequenceMatcher(None, _clean(a), _clean(b)).ratio()
    return ratio >= threshold


def search_tmdb(title: str, year: Optional[int], kind: str) -> Tuple[Optional[int], Optional[str]]:
    api_key = _api_key()
    if not api_key:
        return None, None

    search_title = _strip_year(title)
    log.debug("Searching TMDB for %r (%s, %s)", search_title, kind, year)

    params = {"api_key": api_key, "query": search_title}
    if year is not None:
        params["year" if kind == "movie" else "first_air_date_year"] = year

    r = requests.get(
        f"https://api.themoviedb.org/3/search/{kind}",
        params=params,
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    js = r.json()
    results = js.get("results") or []
    log.debug("TMDB returned %d results", len(results))
    if not results:
        return None, None

    best_ratio = 0.0
    best_id: Optional[int] = None
    best_title: Optional[str] = None
    for result in results:
        candidates = [
            result.get("title"),
            result.get("name"),
            result.get("original_title"),
            result.get("original_name"),
        ]
        candidates = [c for c in candidates if c]  # Filter out None/empty values

        if not candidates:
            continue

        # Find the best matching candidate from all available titles
        for candidate in candidates:
            ratio = SequenceMatcher(None, _clean(search_title), _clean(candidate)).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_id = result.get("id")
                best_title = candidate
    log.debug(
        "Best candidate ratio %.2f for %r (ID %s)",
        best_ratio,
        best_title,
        best_id,
    )

    if best_id is not None:
        return best_id, best_title

    first = results[0]
    return first.get("id"), first.get("title") or first.get("name")


def get_title(tmdb_id: int, kind: str) -> Optional[str]:
    """Fetch the name/title of a TMDB entry by ID."""

    api_key = _api_key()
    if not api_key:
        return None

    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/{kind}/{tmdb_id}",
            params={"api_key": api_key},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Failed to fetch TMDB title: %s", exc)
        return None

    js = r.json()
    return js.get("title") or js.get("name")


def get_year(tmdb_id: int, kind: str) -> Optional[int]:
    """Fetch the release year of a TMDB entry by ID."""

    api_key = _api_key()
    if not api_key:
        return None

    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/{kind}/{tmdb_id}",
            params={"api_key": api_key},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        log.debug("Failed to fetch TMDB year: %s", exc)
        return None

    js = r.json()
    date = js.get("release_date") or js.get("first_air_date")
    if date and len(date) >= 4 and date[:4].isdigit():
        return int(date[:4])
    return None


def external_ids(tmdb_id: int, kind: str) -> dict:
    api_key = _api_key()
    if not api_key:
        return {}
    url = f"https://api.themoviedb.org/3/{kind}/{tmdb_id}/external_ids"
    log.debug("Fetching external IDs for %s %s", kind, tmdb_id)
    r = requests.get(
        url,
        params={"api_key": api_key},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    js = r.json()
    log.debug("External IDs response: %s", js)
    return js


def _apply_tags(path: Path, tags: dict[str, str]) -> None:
    if not tags:
        return
    mkvpropedit = shutil.which("mkvpropedit")
    if not mkvpropedit:
        log.debug("mkvpropedit not found on PATH; skipping tags")
        return
    log.debug("Applying tags to %s: %s", path, tags)
    xml_lines = ["<?xml version='1.0' encoding='UTF-8'?>", "<Tags>", "  <Tag>", "    <Targets/>"]
    for name, value in tags.items():
        xml_lines.append(f"    <Simple><Name>{name}</Name><String>{value}</String></Simple>")
    xml_lines.extend(["  </Tag>", "</Tags>"])
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write("\n".join(xml_lines))
        tmp_path = Path(f.name)
    try:
        subprocess.run(
            [mkvpropedit, str(path), "--tags", f"global:{tmp_path}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log.debug("Tags applied via mkvpropedit")
    finally:
        tmp_path.unlink(missing_ok=True)


def tag_file(path: Path, title: Title, tmdb_id: Optional[int] | None = None) -> None:
    log.debug("Tagging file %s with title %r", path, title)
    standard_tags: dict[str, str] = {}
    custom_tags: dict[str, str] = {}
    # To add custom information to the tags
    # custom_tags["Text to the left side"] = "Text to the right side"

    if config.tag:
        custom_tags["Group"] = config.tag
    description = getattr(title, "description", None)
    if description:
        if len(description) > 255:
            truncated = description[:255]
            if " " in truncated:
                truncated = truncated.rsplit(" ", 1)[0]
            description = truncated + "..."
        custom_tags["Description"] = description

    api_key = _api_key()
    if not api_key:
        log.debug("No TMDB API key set; applying basic tags only")
        _apply_tags(path, custom_tags)
        return

    if isinstance(title, Movie):
        kind = "movie"
        name = title.name
        year = title.year
    elif isinstance(title, Episode):
        kind = "tv"
        name = title.title
        year = title.year
    else:
        _apply_tags(path, custom_tags)
        return

    tmdb_title: Optional[str] = None
    if tmdb_id is None:
        tmdb_id, tmdb_title = search_tmdb(name, year, kind)
        log.debug("Search result: %r (ID %s)", tmdb_title, tmdb_id)
        if not tmdb_id or not tmdb_title or not fuzzy_match(tmdb_title, name):
            log.debug("TMDB search did not match; skipping external ID lookup")
            _apply_tags(path, custom_tags)
            return

    tmdb_url = f"https://www.themoviedb.org/{'movie' if kind == 'movie' else 'tv'}/{tmdb_id}"
    standard_tags["TMDB"] = tmdb_url
    try:
        ids = external_ids(tmdb_id, kind)
    except requests.RequestException as exc:
        log.debug("Failed to fetch external IDs: %s", exc)
        ids = {}
    else:
        log.debug("External IDs found: %s", ids)

    imdb_id = ids.get("imdb_id")
    if imdb_id:
        standard_tags["IMDB"] = f"https://www.imdb.com/title/{imdb_id}"
    tvdb_id = ids.get("tvdb_id")
    if tvdb_id:
        tvdb_prefix = "movies" if kind == "movie" else "series"
        standard_tags["TVDB"] = f"https://thetvdb.com/{tvdb_prefix}/{tvdb_id}"

    merged_tags = {
        **custom_tags,
        **standard_tags,
    }
    _apply_tags(path, merged_tags)


__all__ = [
    "search_tmdb",
    "get_title",
    "get_year",
    "external_ids",
    "tag_file",
    "fuzzy_match",
]

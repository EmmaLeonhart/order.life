#!/usr/bin/env python
"""
Compute localized realm names from raw Wikidata labels.

For each realm in realms.json, strips administrative qualifiers from each
language label and applies the language-appropriate "Realm of X" pattern,
storing the result as realm_names[lang].

English uses the existing realm_name (already hand-normalized with
MANUAL_OVERRIDES) rather than the raw Wikidata label.

Usage:
    python realms/normalize_realm_names.py
"""

import json
import re
from pathlib import Path

REALMS_JSON = Path(__file__).parent / "realms.json"

# ── Localized "Realm of X" patterns ──────────────────────────────────────
# {name} is replaced with the stripped label.
REALM_PATTERNS = {
    "en": "Realm of {name}",
    "ja": "{name}の国",          # X no Kuni
    "zh": "{name}之境",          # X zhī jìng
    "es": "Reino de {name}",
    "hi": "{name} की भूमि",      # X kī bhūmi
    "ar": "أرض {name}",          # Ard X
    "fr": "Royaume de {name}",
    "ru": "Земля {name}",        # Zemlya X
    "uk": "Земля {name}",
    "de": "Land {name}",
    "he": "ארץ {name}",          # Eretz X
    "pt": "Reino de {name}",
}

# ── Prefixes to strip (longest-match-first; case-insensitive) ────────────
STRIP_PREFIXES = {
    "es": [
        "óblast de ", "óblast del ", "óblast de la ",
        "prefectura de ", "prefectura del ", "prefectura de la ",
        "provincia de ", "provincia del ", "provincia de la ",
        "estado de ", "estado del ", "estado de la ",
        "departamento de ", "departamento del ",
        "región de ", "región del ", "región de la ",
        "comunidad de ", "comunidad autónoma de ",
        "krai de ", "cantón de ",
    ],
    "fr": [
        "oblast de ", "oblast d\u2019", "oblast d'",
        "préfecture de ", "préfecture d\u2019", "préfecture d'",
        "province de ", "province d\u2019", "province d'",
        "région de ", "région d\u2019", "région d'",
        "kraï de ", "kraï d\u2019",
        "département de ", "département d\u2019", "département d'",
        "communauté de ", "république de ",
    ],
    "ar": [
        "ولاية ", "أوبلاست ", "محافظة ", "مقاطعة ",
        "إقليم ", "جمهورية ", "منطقة ", "مديرية ",
    ],
    "de": [
        "freistaat ", "kanton ", "landkreis ",
    ],
    "ru": [
        "Республика ",
    ],
    "uk": [
        "Автономна Республіка ",
    ],
    "pt": [
        "estado do ", "estado de ", "estado da ",
        "província de ", "região de ", "prefeitura de ",
    ],
    "he": [
        "מחוז ", "נפת ",
    ],
}

# ── Suffixes to strip (longest-match-first) ───────────────────────────────
STRIP_SUFFIXES = {
    # Japanese: strip all common admin suffixes (single char last; order matters)
    "ja": [
        "自治体", "自治区", "自治州", "特別区",
        "州", "県", "省", "区", "府", "道", "都", "市",
    ],
    # Chinese: same set
    "zh": [
        "自治区", "自治州", "直辖市", "特别行政区",
        "省", "区", "府", "道", "都", "市", "州",
    ],
    # Russian: common admin type words (suffix form, e.g. "Чеченская Республика")
    "ru": [
        " автономный округ", " автономная область", " федеральный округ",
        " Республика", " область", " край", " округ",
    ],
    # Ukrainian
    "uk": [
        " автономна республіка", " область", " округ",
    ],
    # Hindi: transliterated admin words
    "hi": [
        " ओब्लास्ट", " ओब्लास्त",
        " प्रीफेक्चर", " प्रीफ़ेक्चर",
        " प्रान्त", " प्रांत",
        " प्रदेश", " राज्य", " क्षेत्र",
        " गणराज्य", " क्राय",
    ],
}


def normalize_realm_name(label: str, lang: str) -> str | None:
    """Strip admin qualifiers from a Wikidata label and apply the realm pattern."""
    if not label:
        return None

    name = label.strip()

    # Strip trailing parentheticals: "(Province)", "(2014-)", "(प्रान्त)"
    name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()

    # Strip prefixes (case-insensitive, longest first)
    for prefix in sorted(STRIP_PREFIXES.get(lang, []), key=len, reverse=True):
        if name.lower().startswith(prefix.lower()):
            name = name[len(prefix):].strip()
            break

    # Strip suffixes (exact match for CJK, case-sensitive; longest first)
    for suffix in sorted(STRIP_SUFFIXES.get(lang, []), key=len, reverse=True):
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
            break

    # Russian/Ukrainian: strip trailing em-dash alternate names
    # e.g. "Ханты-Мансийский — Югра" → "Ханты-Мансийский"
    if lang in ("ru", "uk"):
        name = re.sub(r"\s*[—–]\s*\S.*$", "", name).strip()

    if not name:
        return None

    # French: elide "de" → "d'" before vowel-initial names
    if lang == "fr":
        _VOWELS = frozenset("aeiouâàäéèêëîïôùûüœæ")
        if name[0].lower() in _VOWELS:
            return f"Royaume d\u2019{name}"
        return f"Royaume de {name}"

    pattern = REALM_PATTERNS.get(lang, "Realm of {name}")
    return pattern.format(name=name)


def main():
    with open(REALMS_JSON, "r", encoding="utf-8") as f:
        realms = json.load(f)

    print(f"Normalizing realm names for {len(realms)} realms...")

    lang_counts = {lang: 0 for lang in REALM_PATTERNS}

    for realm in realms:
        raw_names = realm.get("names", {})
        realm_names = {}

        # English: use the existing realm_name (hand-normalized, MANUAL_OVERRIDES applied)
        realm_names["en"] = realm.get("realm_name", "")

        for lang in REALM_PATTERNS:
            if lang == "en":
                continue
            label = raw_names.get(lang)
            if label:
                result = normalize_realm_name(label, lang)
                if result:
                    realm_names[lang] = result
                    lang_counts[lang] += 1

        realm["realm_names"] = realm_names

    with open(REALMS_JSON, "w", encoding="utf-8") as f:
        json.dump(realms, f, indent=2, ensure_ascii=False)

    print("Done.")
    for lang, count in sorted(lang_counts.items()):
        print(f"  {lang}: {count}/{len(realms)} realm names computed")

    # Show a few examples
    print("\nSample outputs:")
    samples = [r for r in realms if len(r.get("realm_names", {})) >= 8][:4]
    for r in samples:
        print(f"\n  {r['realm_name']} ({r['qid']})")
        for lang, name in sorted(r.get("realm_names", {}).items()):
            print(f"    {lang}: {name}")


if __name__ == "__main__":
    main()

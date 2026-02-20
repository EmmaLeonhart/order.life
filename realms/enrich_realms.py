#!/usr/bin/env python
"""
Enrich realms.json with Wikidata properties.

Queries Wikidata SPARQL for country, population, area, flag, locator map,
and geoshape for each realm QID. Standardizes names to "Realm of X" and
rewrites realms.json sorted by country then realm name.

Usage:
    python realms/enrich_realms.py
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REALMS_JSON = SCRIPT_DIR / "realms.json"

# QIDs to remove from the dataset
REMOVE_QIDS = {"Q67906082"}  # Andhra Pradesh (1956-2014), defunct

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "OrderOfLifeBot/1.0 (https://order.life; contact@order.life)"
BATCH_SIZE = 80
BATCH_DELAY = 2  # seconds between batches

# Languages to fetch labels for (all active site languages)
SITE_LANGS = ["en", "ja", "zh", "es", "hi", "ar", "fr", "ru", "uk", "de", "he", "pt"]

# Suffixes to strip (longest-match-first order matters)
SUFFIXES_TO_STRIP = [
    "Autonomous Okrug",
    "People's Republic",
    "Prefecture",
    "Province",
    "Republic",
    "Oblast",
    "State",
    "Krai",
    "Pradesh",
    "District",
    "Region",
    "Department",
    "Governorate",
    "Canton",
    "County",
    "Voivodeship",
    "Okrug",
]

# Manual overrides for realm_name (QID -> full realm_name)
MANUAL_OVERRIDES = {
    "Q119158": "Realm of Mexico City",       # Federal District (Mexico)
    "Q649": "Realm of Moscow",               # Moscow (city, federal subject)
    "Q656": "Realm of Saint Petersburg",      # Saint Petersburg (city, federal subject)
    "Q1490": "Realm of Tokyo",               # Tokyo (metropolis)
    "Q223": "Realm of Greenland",            # Greenland (autonomous territory)
    "Q7525": "Realm of Sevastopol",          # Sevastopol (city, federal subject)
    "Q57251": "Realm of Taiwan",             # Taiwan Province
}


def standardize_name(qid, wikidata_name):
    """Convert a Wikidata name to 'Realm of X' format."""
    if qid in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[qid]

    name = wikidata_name.strip()

    # Strip suffixes (longest match first, already sorted by length above)
    sorted_suffixes = sorted(SUFFIXES_TO_STRIP, key=len, reverse=True)
    for suffix in sorted_suffixes:
        # Check for " Suffix" at end
        if name.endswith(" " + suffix):
            name = name[: -(len(suffix) + 1)].strip()
            break
        # Check for " Suffix" with parenthetical like "Bhopal State (1949-1956)"
        # Already handled: suffix appears before parenthetical

    # Strip trailing parentheticals like "(1956-2014)"
    import re
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()

    return f"Realm of {name}"


def extract_filename(uri):
    """Extract filename from Wikidata file URI.

    e.g. "http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20Alabama.svg"
    -> "Flag of Alabama.svg"
    """
    if not uri:
        return None
    # Handle Special:FilePath URIs
    if "Special:FilePath/" in uri:
        filename = uri.split("Special:FilePath/")[-1]
        return urllib.parse.unquote(filename)
    # Handle direct commons URIs
    if "/File:" in uri:
        filename = uri.split("/File:")[-1]
        return urllib.parse.unquote(filename)
    return None


def extract_geoshape(uri):
    """Extract geoshape title from Wikidata URI.

    e.g. "http://commons.wikimedia.org/data/main/Data:Alabama.map"
    -> "Data:Alabama.map"
    """
    if not uri:
        return None
    # Various formats seen in Wikidata
    for prefix in ["/data/main/", "commons.wikimedia.org/wiki/"]:
        if prefix in uri:
            return uri.split(prefix)[-1]
    # Fallback: if it starts with Data:
    if "Data:" in uri:
        idx = uri.index("Data:")
        return urllib.parse.unquote(uri[idx:])
    return None


def query_labels(qids):
    """Fetch Wikidata labels in all site languages for a batch of QIDs.

    Returns a dict mapping QID -> {lang: label}.
    """
    values = " ".join(f"wd:{qid}" for qid in qids)
    lang_filter = ", ".join(f'"{l}"' for l in SITE_LANGS)
    sparql = f"""
SELECT ?item (LANG(?label) AS ?lang) ?label WHERE {{
  VALUES ?item {{ {values} }}
  ?item rdfs:label ?label
  FILTER(LANG(?label) IN ({lang_filter}))
}}
"""
    url = SPARQL_ENDPOINT + "?" + urllib.parse.urlencode({
        "query": sparql,
        "format": "json",
    })
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                result = {}
                for row in data["results"]["bindings"]:
                    qid = row["item"]["value"].split("/")[-1]
                    lang = row["lang"]["value"]
                    label = row["label"]["value"]
                    result.setdefault(qid, {})[lang] = label
                return result
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                raise


def query_sparql(qids):
    """Query Wikidata SPARQL for a batch of QIDs."""
    values = " ".join(f"wd:{qid}" for qid in qids)
    sparql = f"""
SELECT ?item ?itemLabel ?countryLabel ?geoshape ?locator_map ?flag ?population ?area
WHERE {{
  VALUES ?item {{ {values} }}
  OPTIONAL {{ ?item wdt:P17 ?country . }}
  OPTIONAL {{ ?item wdt:P3896 ?geoshape . }}
  OPTIONAL {{ ?item wdt:P242 ?locator_map . }}
  OPTIONAL {{ ?item wdt:P41 ?flag . }}
  OPTIONAL {{ ?item wdt:P1082 ?population . }}
  OPTIONAL {{ ?item wdt:P2046 ?area . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""
    url = SPARQL_ENDPOINT + "?" + urllib.parse.urlencode({
        "query": sparql,
        "format": "json",
    })
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["results"]["bindings"]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                raise


def process_results(bindings, qid_to_name):
    """Process SPARQL results into realm dicts, deduplicating by QID."""
    realms = {}

    for row in bindings:
        qid = row["item"]["value"].split("/")[-1]
        if qid in REMOVE_QIDS:
            continue

        wikidata_name = row.get("itemLabel", {}).get("value", qid_to_name.get(qid, qid))

        # Parse numeric values
        pop_val = row.get("population", {}).get("value")
        area_val = row.get("area", {}).get("value")
        population = None
        area_km2 = None
        try:
            if pop_val:
                population = int(float(pop_val))
        except (ValueError, TypeError):
            pass
        try:
            if area_val:
                area_km2 = float(area_val)
        except (ValueError, TypeError):
            pass

        # Extract file names
        flag_uri = row.get("flag", {}).get("value")
        locator_uri = row.get("locator_map", {}).get("value")
        geoshape_uri = row.get("geoshape", {}).get("value")

        flag_image = extract_filename(flag_uri)
        locator_map = extract_filename(locator_uri)
        geoshape = extract_geoshape(geoshape_uri)

        country = row.get("countryLabel", {}).get("value")

        if qid in realms:
            # Deduplicate: take max population/area, prefer non-None values
            existing = realms[qid]
            if population is not None:
                if existing["population"] is None or population > existing["population"]:
                    existing["population"] = population
            if area_km2 is not None:
                if existing["area_km2"] is None or area_km2 > existing["area_km2"]:
                    existing["area_km2"] = area_km2
            if flag_image and not existing["flag_image"]:
                existing["flag_image"] = flag_image
            if locator_map and not existing["locator_map"]:
                existing["locator_map"] = locator_map
            if geoshape and not existing["geoshape"]:
                existing["geoshape"] = geoshape
            if country and not existing["country"]:
                existing["country"] = country
        else:
            realms[qid] = {
                "qid": qid,
                "wikidata_name": wikidata_name,
                "realm_name": standardize_name(qid, wikidata_name),
                "country": country,
                "population": population,
                "area_km2": area_km2,
                "flag_image": flag_image,
                "locator_map": locator_map,
                "geoshape": geoshape,
            }

    return realms


def main():
    # Load current realms
    with open(REALMS_JSON, "r", encoding="utf-8") as f:
        current_realms = json.load(f)

    print(f"Loaded {len(current_realms)} realms from realms.json")

    # Build QID -> name map and filter out removed QIDs
    qid_to_name = {}
    qids = []
    for r in current_realms:
        qid = r["qid"]
        if qid in REMOVE_QIDS:
            print(f"  Removing {qid} ({r['name']})")
            continue
        qid_to_name[qid] = r["name"]
        qids.append(qid)

    print(f"Querying Wikidata for {len(qids)} realms in batches of {BATCH_SIZE}...")

    all_realms = {}
    for i in range(0, len(qids), BATCH_SIZE):
        batch = qids[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(qids) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} QIDs)...")

        bindings = query_sparql(batch)
        batch_realms = process_results(bindings, qid_to_name)
        all_realms.update(batch_realms)

        if i + BATCH_SIZE < len(qids):
            time.sleep(BATCH_DELAY)

    # Add any QIDs that didn't return results (minimal entry)
    for qid in qids:
        if qid not in all_realms:
            name = qid_to_name[qid]
            print(f"  Warning: No SPARQL results for {qid} ({name}), keeping minimal entry")
            all_realms[qid] = {
                "qid": qid,
                "wikidata_name": name,
                "realm_name": standardize_name(qid, name),
                "country": None,
                "population": None,
                "area_km2": None,
                "flag_image": None,
                "locator_map": None,
                "geoshape": None,
            }

    # ── Fetch multilingual labels ────────────────────────────────────────
    print(f"\nFetching multilingual labels for {len(qids)} realms...")
    all_labels = {}
    for i in range(0, len(qids), BATCH_SIZE):
        batch = qids[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(qids) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Labels batch {batch_num}/{total_batches} ({len(batch)} QIDs)...")
        try:
            batch_labels = query_labels(batch)
            all_labels.update(batch_labels)
        except Exception as e:
            print(f"  Warning: label batch failed: {e}")
        if i + BATCH_SIZE < len(qids):
            time.sleep(BATCH_DELAY)

    # Attach names to each realm
    for realm in all_realms.values():
        realm["names"] = all_labels.get(realm["qid"], {})

    # Sort by country (None last) then realm_name
    sorted_realms = sorted(
        all_realms.values(),
        key=lambda r: (r["country"] or "\uffff", r["realm_name"])
    )

    # Write enriched JSON
    with open(REALMS_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted_realms, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(sorted_realms)} enriched realms to {REALMS_JSON}")

    # Stats
    has_country = sum(1 for r in sorted_realms if r["country"])
    has_flag = sum(1 for r in sorted_realms if r["flag_image"])
    has_pop = sum(1 for r in sorted_realms if r["population"])
    has_area = sum(1 for r in sorted_realms if r["area_km2"])
    has_geo = sum(1 for r in sorted_realms if r["geoshape"])
    has_map = sum(1 for r in sorted_realms if r["locator_map"])
    print(f"  Country: {has_country}/{len(sorted_realms)}")
    print(f"  Flag:    {has_flag}/{len(sorted_realms)}")
    print(f"  Pop:     {has_pop}/{len(sorted_realms)}")
    print(f"  Area:    {has_area}/{len(sorted_realms)}")
    print(f"  Geoshape:{has_geo}/{len(sorted_realms)}")
    print(f"  Locator: {has_map}/{len(sorted_realms)}")


if __name__ == "__main__":
    main()

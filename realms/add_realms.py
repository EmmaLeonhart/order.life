#!/usr/bin/env python
"""
Add realms to realms.json by Wikidata class.

Finds all items that are P31 (instance of) a given class, excludes items
that are P31 Q19953632 (former administrative territorial entity), fetches
enrichment data, and merges into realms.json.

Usage:
    python realms/add_realms.py Q6465          # departments of France
    python realms/add_realms.py Q11828004      # provinces of Japan
"""

import io
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="backslashreplace"
        )

SCRIPT_DIR = Path(__file__).parent
REALMS_JSON = SCRIPT_DIR / "realms.json"

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "OrderOfLifeBot/1.0 (https://order.life; contact@order.life)"

# Import shared helpers from enrich_realms
sys.path.insert(0, str(SCRIPT_DIR))
from enrich_realms import (
    standardize_name,
    extract_filename,
    extract_geoshape,
    REMOVE_QIDS,
)


def sparql_query(sparql):
    """Run a SPARQL query and return bindings."""
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
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["results"]["bindings"]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                raise


def find_instances(class_qid):
    """Find all items that are P31 the given class, excluding former entities."""
    sparql = f"""
SELECT ?item ?itemLabel ?countryLabel ?geoshape ?locator_map ?flag ?population ?area
WHERE {{
  ?item wdt:P31 wd:{class_qid} .
  FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q19953632 . }}
  OPTIONAL {{ ?item wdt:P17 ?country . }}
  OPTIONAL {{ ?item wdt:P3896 ?geoshape . }}
  OPTIONAL {{ ?item wdt:P242 ?locator_map . }}
  OPTIONAL {{ ?item wdt:P41 ?flag . }}
  OPTIONAL {{ ?item wdt:P1082 ?population . }}
  OPTIONAL {{ ?item wdt:P2046 ?area . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""
    print(f"Querying Wikidata for instances of {class_qid}...")
    return sparql_query(sparql)


def process_bindings(bindings):
    """Process SPARQL bindings into realm dicts, deduplicating by QID."""
    realms = {}
    for row in bindings:
        qid = row["item"]["value"].split("/")[-1]
        if qid in REMOVE_QIDS:
            continue

        wikidata_name = row.get("itemLabel", {}).get("value", qid)
        # Skip if label is just the QID (unresolved)
        if wikidata_name == qid:
            continue

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

        flag_image = extract_filename(row.get("flag", {}).get("value"))
        locator_map = extract_filename(row.get("locator_map", {}).get("value"))
        geoshape = extract_geoshape(row.get("geoshape", {}).get("value"))
        country = row.get("countryLabel", {}).get("value")

        if qid in realms:
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
    if len(sys.argv) < 2:
        print("Usage: python realms/add_realms.py <CLASS_QID>")
        print("Example: python realms/add_realms.py Q6465  (departments of France)")
        sys.exit(1)

    class_qid = sys.argv[1]

    # Load existing realms
    with open(REALMS_JSON, "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing_qids = {r["qid"] for r in existing}
    print(f"Existing realms: {len(existing)}")

    # Query Wikidata
    bindings = find_instances(class_qid)
    print(f"Got {len(bindings)} SPARQL rows")

    new_realms = process_bindings(bindings)
    print(f"Resolved to {len(new_realms)} unique items")

    # Merge: add new, skip existing
    added = 0
    for qid, realm in new_realms.items():
        if qid not in existing_qids:
            existing.append(realm)
            existing_qids.add(qid)
            added += 1
            print(f"  + {realm['realm_name']} ({qid})")
        else:
            pass  # already present

    print(f"\nAdded {added} new realms, {len(new_realms) - added} already existed")

    # Re-sort by country then realm_name
    existing.sort(key=lambda r: (r.get("country") or "\uffff", r.get("realm_name", "")))

    with open(REALMS_JSON, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"Total realms now: {len(existing)}")


if __name__ == "__main__":
    main()

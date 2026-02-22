#!/usr/bin/env python
"""
Find all Russian Krais (Q831740) on Wikidata and add any missing to realms.json.
Fetches the same fields as enrich_realms.py (country, pop, area, flag, locator, geoshape)
plus multilingual labels.
"""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent
REALMS_JSON = SCRIPT_DIR / "realms.json"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "OrderOfLifeBot/1.0 (https://order.life; contact@order.life)"
SITE_LANGS = ["en", "ja", "zh", "es", "hi", "ar", "fr", "ru", "uk", "de", "he", "pt"]

SUFFIXES_TO_STRIP = [
    "Autonomous Okrug", "People's Republic", "Prefecture", "Province",
    "Republic", "Oblast", "State", "Krai", "Pradesh", "District",
    "Region", "Department", "Governorate", "Canton", "County",
    "Voivodeship", "Okrug",
]
MANUAL_OVERRIDES = {
    "Q119158": "Realm of Mexico City",
    "Q649":    "Realm of Moscow",
    "Q656":    "Realm of Saint Petersburg",
    "Q1490":   "Realm of Tokyo",
    "Q223":    "Realm of Greenland",
    "Q7525":   "Realm of Sevastopol",
    "Q57251":  "Realm of Taiwan",
}


def standardize_name(qid, wikidata_name):
    if qid in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[qid]
    import re
    name = wikidata_name.strip()
    sorted_suffixes = sorted(SUFFIXES_TO_STRIP, key=len, reverse=True)
    for suffix in sorted_suffixes:
        if name.endswith(" " + suffix):
            name = name[:-(len(suffix) + 1)].strip()
            break
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()
    return f"Realm of {name}"


def extract_filename(uri):
    if not uri:
        return None
    if "Special:FilePath/" in uri:
        return urllib.parse.unquote(uri.split("Special:FilePath/")[-1])
    if "/File:" in uri:
        return urllib.parse.unquote(uri.split("/File:")[-1])
    return None


def extract_geoshape(uri):
    if not uri:
        return None
    for prefix in ["/data/main/", "commons.wikimedia.org/wiki/"]:
        if prefix in uri:
            return uri.split(prefix)[-1]
    if "Data:" in uri:
        return urllib.parse.unquote(uri[uri.index("Data:"):])
    return None


def sparql_query(query):
    url = SPARQL_ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))["results"]["bindings"]
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                raise


def main():
    with open(REALMS_JSON, encoding="utf-8") as f:
        realms = json.load(f)
    existing_qids = {r["qid"] for r in realms}
    print(f"Loaded {len(realms)} existing realms.")

    # Query all Russian Krais (P31 = Q831740)
    print("Querying Wikidata for all Russian Krais (Q831740)...")
    krai_query = """
SELECT ?item ?itemLabel ?geoshape ?locator_map ?flag ?population ?area ?countryLabel WHERE {
  ?item wdt:P31 wd:Q831740 .
  OPTIONAL { ?item wdt:P3896 ?geoshape . }
  OPTIONAL { ?item wdt:P242 ?locator_map . }
  OPTIONAL { ?item wdt:P41 ?flag . }
  OPTIONAL { ?item wdt:P1082 ?population . }
  OPTIONAL { ?item wdt:P2046 ?area . }
  OPTIONAL { ?item wdt:P17 ?country . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
"""
    bindings = sparql_query(krai_query)

    # Deduplicate by QID, taking best values
    found = {}
    for row in bindings:
        qid = row["item"]["value"].split("/")[-1]
        name = row.get("itemLabel", {}).get("value", qid)
        country = row.get("countryLabel", {}).get("value")

        def num(key):
            v = row.get(key, {}).get("value")
            try: return float(v) if v else None
            except: return None

        flag = extract_filename(row.get("flag", {}).get("value"))
        locator = extract_filename(row.get("locator_map", {}).get("value"))
        geoshape = extract_geoshape(row.get("geoshape", {}).get("value"))
        pop = num("population")
        area = num("area")

        if qid in found:
            e = found[qid]
            if pop and (not e["population"] or pop > e["population"]): e["population"] = int(pop)
            if area and (not e["area_km2"] or area > e["area_km2"]): e["area_km2"] = area
            if flag and not e["flag_image"]: e["flag_image"] = flag
            if locator and not e["locator_map"]: e["locator_map"] = locator
            if geoshape and not e["geoshape"]: e["geoshape"] = geoshape
        else:
            found[qid] = {
                "qid": qid,
                "wikidata_name": name,
                "realm_name": standardize_name(qid, name),
                "country": country,
                "population": int(pop) if pop else None,
                "area_km2": area,
                "flag_image": flag,
                "locator_map": locator,
                "geoshape": geoshape,
            }

    print(f"Found {len(found)} Krais on Wikidata.")

    missing = {qid: r for qid, r in found.items() if qid not in existing_qids}
    print(f"Already in realms.json: {len(found) - len(missing)}")
    print(f"Missing: {len(missing)}")
    for qid, r in missing.items():
        print(f"  + {qid}: {r['wikidata_name']} -> {r['realm_name']}")

    if not missing:
        print("Nothing to add.")
        return

    # Fetch multilingual labels for missing QIDs
    print(f"\nFetching multilingual labels for {len(missing)} new realms...")
    qids = list(missing.keys())
    values = " ".join(f"wd:{q}" for q in qids)
    lang_filter = ", ".join(f'"{l}"' for l in SITE_LANGS)
    label_query = f"""
SELECT ?item (LANG(?label) AS ?lang) ?label WHERE {{
  VALUES ?item {{ {values} }}
  ?item rdfs:label ?label
  FILTER(LANG(?label) IN ({lang_filter}))
}}
"""
    label_bindings = sparql_query(label_query)
    labels = {}
    for row in label_bindings:
        qid = row["item"]["value"].split("/")[-1]
        lang = row["lang"]["value"]
        label = row["label"]["value"]
        labels.setdefault(qid, {})[lang] = label

    for qid, r in missing.items():
        r["names"] = labels.get(qid, {})
        r["realm_names"] = {}
        r["good_fudoki"] = False
        r["slug"] = r["wikidata_name"].lower().replace(" ", "-").replace("'", "")
        realms.append(r)

    # Also attach names/realm_names/slug/good_fudoki to new entries only — existing ones are unchanged
    # Re-sort
    realms.sort(key=lambda r: (r.get("country") or "\uffff", r.get("realm_name", "")))

    with open(REALMS_JSON, "w", encoding="utf-8") as f:
        json.dump(realms, f, indent=2, ensure_ascii=False)

    print(f"\nAdded {len(missing)} new realms. realms.json now has {len(realms)} entries.")


if __name__ == "__main__":
    main()

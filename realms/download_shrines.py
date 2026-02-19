"""Download all Shinto shrines with English labels from Wikidata via SPARQL."""
import csv
import requests
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

QUERY = """
SELECT ?shrine ?shrineLabel ?coord ?article WHERE {
  ?shrine wdt:P31/wdt:P279* wd:Q845945 .
  ?shrine rdfs:label ?shrineLabel .
  FILTER(LANG(?shrineLabel) = "en")
  OPTIONAL { ?shrine wdt:P625 ?coord . }
  OPTIONAL {
    ?article schema:about ?shrine ;
             schema:isPartOf <https://en.wikipedia.org/> .
  }
}
ORDER BY ?shrineLabel
"""

def main():
    print("Querying Wikidata for Shinto shrines with English labels...")
    r = requests.get(
        SPARQL_ENDPOINT,
        params={"query": QUERY, "format": "json"},
        headers={"User-Agent": "ShintoShrineDownloader/1.0 (Python requests)"},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()

    results = data["results"]["bindings"]
    print(f"Found {len(results)} shrines.")

    # Deduplicate by QID, keeping first coord and enwiki found
    seen = {}
    for item in results:
        qid = item["shrine"]["value"].rsplit("/", 1)[-1]
        if qid in seen:
            # Fill in missing fields from later rows
            if not seen[qid]["enwiki"]:
                seen[qid]["enwiki"] = item.get("article", {}).get("value", "")
            continue
        label = item["shrineLabel"]["value"]
        coord = item.get("coord", {}).get("value", "")
        lat, lon = "", ""
        if coord.startswith("Point("):
            parts = coord.replace("Point(", "").replace(")", "").split()
            if len(parts) == 2:
                lon, lat = parts[0], parts[1]
        enwiki = item.get("article", {}).get("value", "")
        seen[qid] = {"qid": qid, "label": label, "lat": lat, "lon": lon, "enwiki": enwiki}

    rows = sorted(seen.values(), key=lambda x: x["label"])

    outfile = "shinto_shrines_wikidata.csv"
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "label", "lat", "lon", "enwiki"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {outfile}")

if __name__ == "__main__":
    main()

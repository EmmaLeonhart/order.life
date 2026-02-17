"""
Analyze all instance_of_qid values from the first-level divisions CSV.

Gets labels and common properties for each type.
"""

import csv
import sys
import io
import time
import requests
from collections import Counter

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

HEADERS = {
    "User-Agent": "HallowingsOfTheRealms/1.0 (research project) Python/3.x",
    "Accept": "application/sparql-results+json"
}


def run_sparql_query(query):
    """Execute a SPARQL query against Wikidata."""
    params = {"query": query, "format": "json"}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(
                WIKIDATA_SPARQL_ENDPOINT,
                params=params,
                headers=HEADERS,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise
    return None


def get_type_labels(qids):
    """Get English labels for a list of QIDs."""
    # Batch into groups of 50 to avoid query limits
    labels = {}
    qid_list = list(qids)

    for i in range(0, len(qid_list), 50):
        batch = qid_list[i:i+50]
        values = " ".join(f"wd:{qid}" for qid in batch)

        query = f"""
        SELECT ?item ?itemLabel WHERE {{
          VALUES ?item {{ {values} }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """

        print(f"  Fetching labels for batch {i//50 + 1}...")
        results = run_sparql_query(query)

        if results and "results" in results and "bindings" in results["results"]:
            for binding in results["results"]["bindings"]:
                qid = binding["item"]["value"].split("/")[-1]
                label = binding.get("itemLabel", {}).get("value", qid)
                labels[qid] = label

        time.sleep(1)

    return labels


def get_type_properties(qid):
    """Get common properties used on instances of this type."""
    query = f"""
    SELECT ?prop ?propLabel (COUNT(?item) AS ?count) WHERE {{
      ?item wdt:P31 wd:{qid} .
      ?item ?p ?value .
      ?prop wikibase:directClaim ?p .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    GROUP BY ?prop ?propLabel
    ORDER BY DESC(?count)
    LIMIT 20
    """

    results = run_sparql_query(query)

    properties = []
    if results and "results" in results and "bindings" in results["results"]:
        for binding in results["results"]["bindings"]:
            prop_id = binding["prop"]["value"].split("/")[-1]
            prop_label = binding.get("propLabel", {}).get("value", prop_id)
            count = int(binding["count"]["value"])
            properties.append({
                "property": prop_id,
                "label": prop_label,
                "count": count
            })

    return properties


def main():
    print("=" * 60)
    print("Analyzing Instance Types from First-Level Divisions")
    print("=" * 60)
    print()

    # Read the CSV and count instance types
    print("Reading CSV...")
    instance_counts = Counter()

    with open("first_level_divisions.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            instance_counts[row["instance_of_qid"]] += 1

    print(f"Found {len(instance_counts)} unique instance types")
    print()

    # Get labels for all types
    print("Fetching labels for all instance types...")
    type_labels = get_type_labels(instance_counts.keys())
    print()

    # Sort by count descending
    sorted_types = sorted(instance_counts.items(), key=lambda x: -x[1])

    # Output summary CSV
    print("Writing instance_types_summary.csv...")
    with open("instance_types_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["qid", "label", "instance_count"])
        for qid, count in sorted_types:
            label = type_labels.get(qid, qid)
            writer.writerow([qid, label, count])

    print()
    print("All instance types (sorted by count):")
    print("-" * 60)

    for qid, count in sorted_types:
        label = type_labels.get(qid, qid)
        print(f"{qid:15} {count:5} instances  {label}")

    print()
    print("-" * 60)
    print(f"Total: {len(sorted_types)} unique types, {sum(instance_counts.values())} total instances")
    print()

    # Optionally analyze properties for top types
    print("=" * 60)
    print("Analyzing common properties for top 5 instance types...")
    print("=" * 60)

    for qid, count in sorted_types[:5]:
        label = type_labels.get(qid, qid)
        print()
        print(f"{label} ({qid}) - {count} instances")
        print("-" * 40)

        time.sleep(1.5)
        properties = get_type_properties(qid)

        for prop in properties[:10]:
            print(f"  {prop['property']:10} {prop['label']:30} ({prop['count']} uses)")


if __name__ == "__main__":
    main()

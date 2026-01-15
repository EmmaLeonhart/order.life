"""
Filter out historical/former administrative divisions from the CSV.

Removes entities that are instances of:
- Q19953632 (former administrative territorial entity) or its subclasses
- Q19832712 (historical administrative division) or its subclasses
"""

import csv
import sys
import io
import time
import requests

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

HEADERS = {
    "User-Agent": "HallowingsOfTheRealms/1.0 (research project) Python/3.x",
    "Accept": "application/sparql-results+json"
}

# Classes to exclude (and all their subclasses)
EXCLUDE_CLASSES = [
    "Q19953632",  # former administrative territorial entity
    "Q19832712",  # historical administrative division
]


def run_sparql_query(query, timeout=180):
    """Execute a SPARQL query against Wikidata."""
    params = {"query": query, "format": "json"}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(
                WIKIDATA_SPARQL_ENDPOINT,
                params=params,
                headers=HEADERS,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(10 * (attempt + 1))
            else:
                raise
    return None


def get_all_exclude_classes():
    """Get all classes to exclude (the base classes + all subclasses)."""
    all_classes = set()

    for base_class in EXCLUDE_CLASSES:
        print(f"Fetching subclasses of {base_class}...")

        query = f"""
        SELECT DISTINCT ?class ?classLabel WHERE {{
          ?class wdt:P279* wd:{base_class} .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """

        results = run_sparql_query(query)

        if results and "results" in results and "bindings" in results["results"]:
            for binding in results["results"]["bindings"]:
                qid = binding["class"]["value"].split("/")[-1]
                label = binding.get("classLabel", {}).get("value", qid)
                all_classes.add(qid)
                print(f"  {qid}: {label}")

        time.sleep(1)

    return all_classes


def get_entities_to_remove_direct():
    """Find all entities that are instances of excluded classes or their subclasses."""
    print("\nFinding entities to remove using direct SPARQL subclass query...")

    entities_to_remove = set()

    for base_class in EXCLUDE_CLASSES:
        print(f"  Querying instances of {base_class} and subclasses...")

        # Use P279* to traverse subclass hierarchy directly in SPARQL
        query = f"""
        SELECT DISTINCT ?item WHERE {{
          ?type wdt:P279* wd:{base_class} .
          ?item wdt:P31 ?type .
        }}
        """

        results = run_sparql_query(query, timeout=600)

        if results and "results" in results and "bindings" in results["results"]:
            count = 0
            for binding in results["results"]["bindings"]:
                qid = binding["item"]["value"].split("/")[-1]
                entities_to_remove.add(qid)
                count += 1
            print(f"    Found {count} entities")

        time.sleep(2)

    return entities_to_remove


def main():
    print("=" * 70)
    print("Filtering Historical/Former Administrative Divisions")
    print("=" * 70)
    print()

    # Step 1: Find entities to remove directly via SPARQL
    print("Step 1: Finding entities to remove...")
    entities_to_remove = get_entities_to_remove_direct()
    print(f"\nTotal entities to remove: {len(entities_to_remove)}")

    # Step 3: Read the current CSVs and filter
    print("\nStep 3: Filtering CSVs...")

    # Filter basic CSV
    print("\nFiltering first_level_divisions.csv...")
    basic_rows = []
    removed_basic = 0
    with open("first_level_divisions.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["qid"] not in entities_to_remove:
                basic_rows.append(row)
            else:
                removed_basic += 1

    print(f"  Removed {removed_basic} rows, keeping {len(basic_rows)}")

    # Write filtered basic CSV
    with open("first_level_divisions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(basic_rows)

    # Filter enriched CSV
    print("\nFiltering first_level_divisions_enriched.csv...")
    enriched_rows = []
    removed_enriched = 0
    with open("first_level_divisions_enriched.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames_enriched = reader.fieldnames
        for row in reader:
            if row["qid"] not in entities_to_remove:
                enriched_rows.append(row)
            else:
                removed_enriched += 1

    print(f"  Removed {removed_enriched} rows, keeping {len(enriched_rows)}")

    # Write filtered enriched CSV
    with open("first_level_divisions_enriched.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_enriched)
        writer.writeheader()
        writer.writerows(enriched_rows)

    # Save list of removed entities for reference
    print("\nSaving removed entities list...")
    with open("removed_historical_entities.txt", "w", encoding="utf-8") as f:
        f.write(f"# Entities removed as historical/former administrative divisions\n")
        f.write(f"# Based on P31 being subclass of Q19953632 or Q19832712\n")
        f.write(f"# Total removed: {len(entities_to_remove)}\n\n")
        for qid in sorted(entities_to_remove):
            f.write(f"{qid}\n")

    print()
    print("=" * 70)
    print("Done!")
    print(f"  Entities removed: {removed_basic}")
    print(f"  Entities remaining: {len(basic_rows)}")
    print("=" * 70)


if __name__ == "__main__":
    main()

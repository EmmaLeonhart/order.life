"""
Fetch all first-level administrative divisions from Wikidata.

This script queries Wikidata for:
1. All subclasses of Q10864048 (first-level administrative division)
2. All instances of Q10864048 and each subclass
3. Excludes entities that are P31 Q19953632 (former administrative territorial entity)

Output: CSV with columns [label, qid, instance_of_qid]
"""

import csv
import time
import requests
from urllib.parse import quote

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
FIRST_LEVEL_ADMIN_DIV = "Q10864048"
FORMER_ADMIN_ENTITY = "Q19953632"

# User agent as required by Wikidata
HEADERS = {
    "User-Agent": "HallowingsOfTheRealms/1.0 (https://github.com/; contact@example.com) Python/3.x",
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


def get_all_subclasses():
    """Get Q10864048 and all its subclasses."""
    print("Fetching all subclasses of first-level administrative division (Q10864048)...")

    query = f"""
    SELECT DISTINCT ?class ?classLabel WHERE {{
      ?class wdt:P279* wd:{FIRST_LEVEL_ADMIN_DIV} .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    results = run_sparql_query(query)

    subclasses = []
    if results and "results" in results and "bindings" in results["results"]:
        for binding in results["results"]["bindings"]:
            qid = binding["class"]["value"].split("/")[-1]
            label = binding.get("classLabel", {}).get("value", qid)
            subclasses.append({"qid": qid, "label": label})

    print(f"  Found {len(subclasses)} classes (including Q10864048 and all subclasses)")
    return subclasses


def get_instances_of_class(class_qid, class_label):
    """Get all instances of a specific class, excluding former administrative entities."""
    print(f"  Fetching instances of {class_label} ({class_qid})...")

    # Query for instances of this class that are NOT former administrative territorial entities
    query = f"""
    SELECT DISTINCT ?item ?itemLabel WHERE {{
      ?item wdt:P31 wd:{class_qid} .
      FILTER NOT EXISTS {{ ?item wdt:P31 wd:{FORMER_ADMIN_ENTITY} }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    results = run_sparql_query(query)

    instances = []
    if results and "results" in results and "bindings" in results["results"]:
        for binding in results["results"]["bindings"]:
            item_qid = binding["item"]["value"].split("/")[-1]
            item_label = binding.get("itemLabel", {}).get("value", item_qid)
            instances.append({
                "label": item_label,
                "qid": item_qid,
                "instance_of_qid": class_qid
            })

    print(f"    Found {len(instances)} instances")
    return instances


def get_all_instances_single_query():
    """
    Alternative: Get all instances in a single SPARQL query.
    This is more efficient but may timeout for large result sets.
    """
    print("Fetching all instances in a single query...")

    query = f"""
    SELECT DISTINCT ?item ?itemLabel ?class WHERE {{
      ?class wdt:P279* wd:{FIRST_LEVEL_ADMIN_DIV} .
      ?item wdt:P31 ?class .
      FILTER NOT EXISTS {{ ?item wdt:P31 wd:{FORMER_ADMIN_ENTITY} }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    results = run_sparql_query(query)

    instances = []
    if results and "results" in results and "bindings" in results["results"]:
        for binding in results["results"]["bindings"]:
            item_qid = binding["item"]["value"].split("/")[-1]
            item_label = binding.get("itemLabel", {}).get("value", item_qid)
            class_qid = binding["class"]["value"].split("/")[-1]
            instances.append({
                "label": item_label,
                "qid": item_qid,
                "instance_of_qid": class_qid
            })

    return instances


def main():
    print("=" * 60)
    print("Hallowings of the Realms - First-Level Administrative Divisions")
    print("=" * 60)
    print()

    # Try single query first (more efficient)
    print("Attempting single query approach...")
    try:
        all_instances = get_all_instances_single_query()
        print(f"Single query returned {len(all_instances)} instances")
    except Exception as e:
        print(f"Single query failed: {e}")
        print("Falling back to per-class queries...")

        # Fallback: query each class separately
        subclasses = get_all_subclasses()

        all_instances = []
        seen_qids = set()

        print()
        print("Fetching instances for each class...")
        for i, cls in enumerate(subclasses):
            # Rate limiting
            if i > 0:
                time.sleep(1)

            instances = get_instances_of_class(cls["qid"], cls["label"])

            for inst in instances:
                # Avoid duplicates (an entity might be instance of multiple subclasses)
                if inst["qid"] not in seen_qids:
                    seen_qids.add(inst["qid"])
                    all_instances.append(inst)

    # Remove duplicates while keeping track of one instance_of
    seen = {}
    for inst in all_instances:
        if inst["qid"] not in seen:
            seen[inst["qid"]] = inst

    unique_instances = list(seen.values())

    # Sort by label for readability
    unique_instances.sort(key=lambda x: x["label"].lower())

    # Write to CSV
    output_file = "first_level_divisions.csv"
    print()
    print(f"Writing {len(unique_instances)} entries to {output_file}...")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "qid", "instance_of_qid"])
        writer.writeheader()
        writer.writerows(unique_instances)

    print(f"Done! Output saved to {output_file}")
    print()

    # Print some stats
    instance_of_counts = {}
    for inst in unique_instances:
        iof = inst["instance_of_qid"]
        instance_of_counts[iof] = instance_of_counts.get(iof, 0) + 1

    print("Top 10 most common instance types:")
    sorted_counts = sorted(instance_of_counts.items(), key=lambda x: -x[1])[:10]
    for qid, count in sorted_counts:
        print(f"  {qid}: {count} instances")


if __name__ == "__main__":
    main()

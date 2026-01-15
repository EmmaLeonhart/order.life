"""
Analyze property coverage across all first-level administrative divisions.

Queries Wikidata to find which properties are most common across the ~6000 entities.
Outputs statistics showing how many entities have each property.
"""

import sys
import io
import time
import requests

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
FIRST_LEVEL_ADMIN_DIV = "Q10864048"
FORMER_ADMIN_ENTITY = "Q19953632"

HEADERS = {
    "User-Agent": "HallowingsOfTheRealms/1.0 (research project) Python/3.x",
    "Accept": "application/sparql-results+json"
}


def run_sparql_query(query, timeout=300):
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


def get_total_count():
    """Get total count of first-level administrative divisions."""
    print("Getting total count of entities...")

    query = f"""
    SELECT (COUNT(DISTINCT ?item) AS ?count) WHERE {{
      ?class wdt:P279* wd:{FIRST_LEVEL_ADMIN_DIV} .
      ?item wdt:P31 ?class .
      FILTER NOT EXISTS {{ ?item wdt:P31 wd:{FORMER_ADMIN_ENTITY} }}
    }}
    """

    results = run_sparql_query(query)
    if results and "results" in results and "bindings" in results["results"]:
        return int(results["results"]["bindings"][0]["count"]["value"])
    return 0


def get_property_counts():
    """Get count of entities having each property."""
    print("Querying property coverage (this may take a few minutes)...")

    query = f"""
    SELECT ?prop ?propLabel (COUNT(DISTINCT ?item) AS ?count) WHERE {{
      ?class wdt:P279* wd:{FIRST_LEVEL_ADMIN_DIV} .
      ?item wdt:P31 ?class .
      FILTER NOT EXISTS {{ ?item wdt:P31 wd:{FORMER_ADMIN_ENTITY} }}
      ?item ?p ?value .
      ?prop wikibase:directClaim ?p .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    GROUP BY ?prop ?propLabel
    ORDER BY DESC(?count)
    """

    results = run_sparql_query(query, timeout=600)

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
    print("=" * 70)
    print("Property Coverage Analysis - First-Level Administrative Divisions")
    print("=" * 70)
    print()

    # Get total count
    total = get_total_count()
    print(f"Total entities: {total}")
    print()

    # Get property counts
    properties = get_property_counts()
    print(f"Found {len(properties)} distinct properties used")
    print()

    # Display results
    print("=" * 70)
    print(f"{'Property':<12} {'Label':<45} {'Count':>7} {'%':>7}")
    print("=" * 70)

    for prop in properties:
        pct = (prop["count"] / total * 100) if total > 0 else 0
        label = prop["label"][:44] if len(prop["label"]) > 44 else prop["label"]
        print(f"{prop['property']:<12} {label:<45} {prop['count']:>7} {pct:>6.1f}%")

    print()
    print("=" * 70)

    # Highlight nearly universal properties (>90%)
    print()
    print("NEARLY UNIVERSAL PROPERTIES (>90% coverage):")
    print("-" * 70)
    for prop in properties:
        pct = (prop["count"] / total * 100) if total > 0 else 0
        if pct >= 90:
            print(f"  {prop['property']:<10} {prop['label']:<50} {pct:.1f}%")

    # Highlight common properties (50-90%)
    print()
    print("COMMON PROPERTIES (50-90% coverage):")
    print("-" * 70)
    for prop in properties:
        pct = (prop["count"] / total * 100) if total > 0 else 0
        if 50 <= pct < 90:
            print(f"  {prop['property']:<10} {prop['label']:<50} {pct:.1f}%")

    # Highlight moderately common (25-50%)
    print()
    print("MODERATELY COMMON PROPERTIES (25-50% coverage):")
    print("-" * 70)
    for prop in properties:
        pct = (prop["count"] / total * 100) if total > 0 else 0
        if 25 <= pct < 50:
            print(f"  {prop['property']:<10} {prop['label']:<50} {pct:.1f}%")


if __name__ == "__main__":
    main()

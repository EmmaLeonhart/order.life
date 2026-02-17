"""
Investigate P131 on first-level administrative divisions.
P131 shouldn't really be on true first-level divisions since they're directly under the country.
"""

import sys
import io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

HEADERS = {
    "User-Agent": "HallowingsOfTheRealms/1.0 (research project) Python/3.x",
    "Accept": "application/sparql-results+json"
}


def run_query(query):
    response = requests.get(
        WIKIDATA_SPARQL_ENDPOINT,
        params={"query": query, "format": "json"},
        headers=HEADERS,
        timeout=120
    )
    return response.json()


# Check what P131 values look like for first-level divisions
print("Checking P131 values on first-level administrative divisions...")
print()

# Get some examples of P131 values
query = """
SELECT ?item ?itemLabel ?p131 ?p131Label ?p131Type ?p131TypeLabel WHERE {
  ?class wdt:P279* wd:Q10864048 .
  ?item wdt:P31 ?class .
  FILTER NOT EXISTS { ?item wdt:P31 wd:Q19953632 }
  ?item wdt:P131 ?p131 .
  OPTIONAL { ?p131 wdt:P31 ?p131Type . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 50
"""

results = run_query(query)

print("Sample of P131 values found:")
print("-" * 100)
print(f"{'Item':<30} {'P131 Value':<30} {'P131 Type':<30}")
print("-" * 100)

for binding in results["results"]["bindings"]:
    item = binding.get("itemLabel", {}).get("value", "?")[:29]
    p131 = binding.get("p131Label", {}).get("value", "?")[:29]
    p131_type = binding.get("p131TypeLabel", {}).get("value", "?")[:29]
    print(f"{item:<30} {p131:<30} {p131_type:<30}")

print()
print("=" * 100)
print()

# Count P131 values by type
print("Counting P131 target types...")
query2 = """
SELECT ?p131Type ?p131TypeLabel (COUNT(DISTINCT ?item) AS ?count) WHERE {
  ?class wdt:P279* wd:Q10864048 .
  ?item wdt:P31 ?class .
  FILTER NOT EXISTS { ?item wdt:P31 wd:Q19953632 }
  ?item wdt:P131 ?p131 .
  ?p131 wdt:P31 ?p131Type .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?p131Type ?p131TypeLabel
ORDER BY DESC(?count)
LIMIT 30
"""

results2 = run_query(query2)

print()
print("What types of entities are P131 pointing to?")
print("-" * 70)

for binding in results2["results"]["bindings"]:
    p131_type = binding.get("p131TypeLabel", {}).get("value", "?")
    count = binding.get("count", {}).get("value", "?")
    qid = binding.get("p131Type", {}).get("value", "").split("/")[-1]
    print(f"{qid:<15} {count:>6}  {p131_type}")

print()
print("=" * 100)

# Check how many P131 values point to countries (which would be expected)
print()
print("How many P131 values point to countries (Q6256)?")
query3 = """
SELECT (COUNT(DISTINCT ?item) AS ?count) WHERE {
  ?class wdt:P279* wd:Q10864048 .
  ?item wdt:P31 ?class .
  FILTER NOT EXISTS { ?item wdt:P31 wd:Q19953632 }
  ?item wdt:P131 ?p131 .
  ?p131 wdt:P31 wd:Q6256 .  # country
}
"""

results3 = run_query(query3)
country_count = results3["results"]["bindings"][0]["count"]["value"]
print(f"  P131 pointing to a country: {country_count}")

# Total with P131
query4 = """
SELECT (COUNT(DISTINCT ?item) AS ?count) WHERE {
  ?class wdt:P279* wd:Q10864048 .
  ?item wdt:P31 ?class .
  FILTER NOT EXISTS { ?item wdt:P31 wd:Q19953632 }
  ?item wdt:P131 ?p131 .
}
"""
results4 = run_query(query4)
total_p131 = results4["results"]["bindings"][0]["count"]["value"]
print(f"  Total with P131: {total_p131}")

print()
print("If most P131 values point to countries, that's expected/redundant.")
print("If they point to other admin entities, these might not be true first-level divisions.")

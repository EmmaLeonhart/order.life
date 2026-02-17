"""
Enrich the first-level divisions CSV with property values.

For each of the 49 properties with 20%+ coverage, adds a column with:
- {QID, label} for entity references
- Raw value for literals (strings, numbers, coordinates, etc.)

Multiple values are separated by " | "
"""

import csv
import sys
import io
import time
import requests
import json

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
FIRST_LEVEL_ADMIN_DIV = "Q10864048"
FORMER_ADMIN_ENTITY = "Q19953632"

HEADERS = {
    "User-Agent": "HallowingsOfTheRealms/1.0 (research project) Python/3.x",
    "Accept": "application/sparql-results+json"
}

# Properties with 20%+ coverage (excluding P31 which we handle specially)
PROPERTIES = [
    ("P31", "instance of"),
    ("P17", "country"),
    ("P131", "located in admin territorial entity"),
    ("P625", "coordinate location"),
    ("P646", "Freebase ID"),
    ("P242", "locator map image"),
    ("P36", "capital"),
    ("P910", "topic's main category"),
    ("P373", "Commons category"),
    ("P2046", "area"),
    ("P1566", "GeoNames ID"),
    ("P300", "ISO 3166-2 code"),
    ("P1082", "population"),
    ("P402", "OpenStreetMap relation ID"),
    ("P7471", "iNaturalist place ID"),
    ("P3896", "geoshape"),
    ("P6766", "Who's on First ID"),
    ("P18", "image"),
    ("P571", "inception"),
    ("P47", "shares border with"),
    ("P901", "FIPS 10-4"),
    ("P2326", "GNS Unique Feature ID"),
    ("P856", "official website"),
    ("P982", "MusicBrainz area ID"),
    ("P13591", "Yale LUX ID"),
    ("P421", "located in time zone"),
    ("P1667", "Getty TGN ID"),
    ("P1464", "category for people born here"),
    ("P150", "contains admin territorial entity"),
    ("P1792", "category of associated people"),
    ("P214", "VIAF cluster ID"),
    ("P94", "coat of arms image"),
    ("P41", "flag image"),
    ("P1705", "native label"),
    ("P8189", "NLI J9U ID"),
    ("P244", "Library of Congress ID"),
    ("P2936", "language used"),
    ("P2044", "elevation above sea level"),
    ("P227", "GND ID"),
    ("P7867", "category for maps"),
    ("P8119", "HASC"),
    ("P1465", "category for people who died here"),
    ("P948", "page banner"),
    ("P9957", "museum-digital place ID"),
    ("P1296", "Gran Enciclopedia Catalana ID (old)"),
    ("P12385", "Gran Enciclopedia Catalana ID"),
    ("P576", "dissolved/abolished date"),
    ("P1313", "office held by head of government"),
    ("P1448", "official name"),
]


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
            print(f"    Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(10 * (attempt + 1))
            else:
                return None
    return None


def format_value(value_obj):
    """Format a SPARQL value object appropriately."""
    if not value_obj:
        return ""

    val_type = value_obj.get("type", "")
    value = value_obj.get("value", "")

    if val_type == "uri":
        # Check if it's a Wikidata entity
        if "wikidata.org/entity/Q" in value:
            qid = value.split("/")[-1]
            return qid  # Just return QID, we'll add label separately
        elif "commons.wikimedia.org" in value:
            # Commons file - extract filename
            return value.split("/")[-1].replace("_", " ")
        else:
            return value
    elif val_type == "literal":
        datatype = value_obj.get("datatype", "")
        if "decimal" in datatype or "integer" in datatype or "double" in datatype:
            return value
        elif "dateTime" in datatype:
            # Extract just the date part
            return value.split("T")[0] if "T" in value else value
        else:
            return value
    else:
        return value


def fetch_property_batch(qids, prop_id):
    """Fetch a single property for a batch of QIDs."""
    values_str = " ".join(f"wd:{qid}" for qid in qids)

    query = f"""
    SELECT ?item ?value ?valueLabel WHERE {{
      VALUES ?item {{ {values_str} }}
      OPTIONAL {{
        ?item wdt:{prop_id} ?value .
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    return run_sparql_query(query, timeout=120)


def fetch_all_properties_for_batch(qids):
    """Fetch all properties for a batch of QIDs in a single query."""
    values_str = " ".join(f"wd:{qid}" for qid in qids)

    # Build OPTIONAL clauses for each property
    optional_clauses = []
    select_vars = ["?item"]

    for prop_id, _ in PROPERTIES:
        var_name = prop_id.lower()
        select_vars.append(f"?{var_name}")
        select_vars.append(f"?{var_name}Label")
        optional_clauses.append(f"OPTIONAL {{ ?item wdt:{prop_id} ?{var_name} . }}")

    query = f"""
    SELECT {" ".join(select_vars)} WHERE {{
      VALUES ?item {{ {values_str} }}
      {chr(10).join(optional_clauses)}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    return run_sparql_query(query, timeout=180)


def process_batch_results(results, prop_id):
    """Process results from a property batch query."""
    data = {}  # qid -> list of values

    if not results or "results" not in results:
        return data

    for binding in results["results"]["bindings"]:
        item_uri = binding.get("item", {}).get("value", "")
        if not item_uri:
            continue
        qid = item_uri.split("/")[-1]

        if qid not in data:
            data[qid] = []

        if "value" in binding and binding["value"].get("value"):
            value_obj = binding["value"]
            val_type = value_obj.get("type", "")
            raw_value = value_obj.get("value", "")

            if val_type == "uri" and "wikidata.org/entity/Q" in raw_value:
                # It's a QID - get label too
                linked_qid = raw_value.split("/")[-1]
                label = binding.get("valueLabel", {}).get("value", linked_qid)
                formatted = f"{{{linked_qid}, {label}}}"
            elif val_type == "uri" and "commons.wikimedia.org" in raw_value:
                # Commons file
                formatted = raw_value.split("/")[-1].replace("_", " ")
            elif val_type == "literal":
                datatype = value_obj.get("datatype", "")
                if "dateTime" in datatype:
                    formatted = raw_value.split("T")[0] if "T" in raw_value else raw_value
                else:
                    formatted = raw_value
            else:
                formatted = raw_value

            if formatted and formatted not in data[qid]:
                data[qid].append(formatted)

    return data


def main():
    print("=" * 70)
    print("Enriching First-Level Divisions CSV with Property Values")
    print("=" * 70)
    print()

    # Read existing CSV
    print("Reading existing CSV...")
    rows = []
    with open("first_level_divisions.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"Loaded {len(rows)} divisions")

    # Get all QIDs
    all_qids = [row["qid"] for row in rows]

    # Initialize property data storage
    # prop_id -> {qid -> [values]}
    all_prop_data = {prop_id: {} for prop_id, _ in PROPERTIES}

    # Process in batches - fetch one property at a time for all entities
    # This is more reliable than fetching all properties at once
    batch_size = 200

    for prop_idx, (prop_id, prop_label) in enumerate(PROPERTIES):
        print(f"\nFetching {prop_id} ({prop_label}) [{prop_idx + 1}/{len(PROPERTIES)}]...")

        prop_data = {}

        for i in range(0, len(all_qids), batch_size):
            batch_qids = all_qids[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(all_qids) + batch_size - 1) // batch_size

            print(f"  Batch {batch_num}/{total_batches}...", end=" ", flush=True)

            results = fetch_property_batch(batch_qids, prop_id)

            if results:
                batch_data = process_batch_results(results, prop_id)
                prop_data.update(batch_data)
                print(f"got {len(batch_data)} entities with values")
            else:
                print("failed")

            time.sleep(0.5)  # Rate limiting

        all_prop_data[prop_id] = prop_data

        # Save progress periodically
        if (prop_idx + 1) % 10 == 0:
            print(f"\n  Progress checkpoint: {prop_idx + 1}/{len(PROPERTIES)} properties fetched")

    # Build enriched rows
    print("\n" + "=" * 70)
    print("Building enriched CSV...")

    # Create new column names
    new_fieldnames = ["label", "qid", "instance_of_qid"]  # Original columns
    for prop_id, prop_label in PROPERTIES:
        new_fieldnames.append(prop_id)

    enriched_rows = []
    for row in rows:
        qid = row["qid"]
        new_row = {
            "label": row["label"],
            "qid": row["qid"],
            "instance_of_qid": row["instance_of_qid"]
        }

        for prop_id, _ in PROPERTIES:
            values = all_prop_data[prop_id].get(qid, [])
            new_row[prop_id] = " | ".join(values) if values else ""

        enriched_rows.append(new_row)

    # Write enriched CSV
    output_file = "first_level_divisions_enriched.csv"
    print(f"Writing to {output_file}...")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"\nDone! Enriched CSV saved to {output_file}")
    print(f"Columns: {len(new_fieldnames)} (3 original + {len(PROPERTIES)} properties)")

    # Print some stats
    print("\nProperty fill rates in enriched data:")
    for prop_id, prop_label in PROPERTIES[:10]:
        filled = sum(1 for row in enriched_rows if row[prop_id])
        pct = filled / len(enriched_rows) * 100
        print(f"  {prop_id:<8} {prop_label:<40} {filled:>5} ({pct:.1f}%)")
    print("  ...")


if __name__ == "__main__":
    main()

"""
Analyze property coverage in the filtered (current) divisions dataset.
Reads from the enriched CSV to calculate fill rates.
"""

import csv
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Property labels for display
PROPERTY_LABELS = {
    "P31": "instance of",
    "P17": "country",
    "P131": "located in admin territorial entity",
    "P625": "coordinate location",
    "P646": "Freebase ID",
    "P242": "locator map image",
    "P36": "capital",
    "P910": "topic's main category",
    "P373": "Commons category",
    "P2046": "area",
    "P1566": "GeoNames ID",
    "P300": "ISO 3166-2 code",
    "P1082": "population",
    "P402": "OpenStreetMap relation ID",
    "P7471": "iNaturalist place ID",
    "P3896": "geoshape",
    "P6766": "Who's on First ID",
    "P18": "image",
    "P571": "inception",
    "P47": "shares border with",
    "P901": "FIPS 10-4",
    "P2326": "GNS Unique Feature ID",
    "P856": "official website",
    "P982": "MusicBrainz area ID",
    "P13591": "Yale LUX ID",
    "P421": "located in time zone",
    "P1667": "Getty TGN ID",
    "P1464": "category for people born here",
    "P150": "contains admin territorial entity",
    "P1792": "category of associated people",
    "P214": "VIAF cluster ID",
    "P94": "coat of arms image",
    "P41": "flag image",
    "P1705": "native label",
    "P8189": "NLI J9U ID",
    "P244": "Library of Congress ID",
    "P2936": "language used",
    "P2044": "elevation above sea level",
    "P227": "GND ID",
    "P7867": "category for maps",
    "P8119": "HASC",
    "P1465": "category for people who died here",
    "P948": "page banner",
    "P9957": "museum-digital place ID",
    "P1296": "Gran Enciclopedia Catalana ID (old)",
    "P12385": "Gran Enciclopedia Catalana ID",
    "P576": "dissolved/abolished date",
    "P1313": "office held by head of government",
    "P1448": "official name",
}


def main():
    print("=" * 70)
    print("Property Coverage Analysis - Current Administrative Divisions")
    print("=" * 70)
    print()

    # Read the enriched CSV
    print("Reading first_level_divisions_enriched.csv...")
    rows = []
    with open("first_level_divisions_enriched.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    total = len(rows)
    print(f"Total entities: {total}")
    print()

    # Get property columns (excluding label, qid, instance_of_qid)
    property_cols = [col for col in fieldnames if col.startswith("P")]

    # Calculate coverage for each property
    coverage = []
    for prop in property_cols:
        filled = sum(1 for row in rows if row.get(prop, "").strip())
        pct = (filled / total * 100) if total > 0 else 0
        label = PROPERTY_LABELS.get(prop, prop)
        coverage.append({
            "property": prop,
            "label": label,
            "count": filled,
            "pct": pct
        })

    # Sort by percentage descending
    coverage.sort(key=lambda x: -x["pct"])

    # Display results
    print("=" * 70)
    print(f"{'Property':<10} {'Label':<45} {'Count':>6} {'%':>7}")
    print("=" * 70)

    for item in coverage:
        print(f"{item['property']:<10} {item['label']:<45} {item['count']:>6} {item['pct']:>6.1f}%")

    print()
    print("=" * 70)

    # Highlight tiers
    print()
    print("NEARLY UNIVERSAL (>90% coverage):")
    print("-" * 70)
    for item in coverage:
        if item["pct"] >= 90:
            print(f"  {item['property']:<10} {item['label']:<45} {item['pct']:.1f}%")

    print()
    print("COMMON (50-90% coverage):")
    print("-" * 70)
    for item in coverage:
        if 50 <= item["pct"] < 90:
            print(f"  {item['property']:<10} {item['label']:<45} {item['pct']:.1f}%")

    print()
    print("MODERATELY COMMON (25-50% coverage):")
    print("-" * 70)
    for item in coverage:
        if 25 <= item["pct"] < 50:
            print(f"  {item['property']:<10} {item['label']:<45} {item['pct']:.1f}%")


if __name__ == "__main__":
    main()

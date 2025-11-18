#!/usr/bin/env python3
"""
Add character ID tags to all epic chapters (001-062).
"""

import re
from pathlib import Path

# Comprehensive list of actual character names (not common words)
# Assigning IDs based on importance/frequency
CHARACTER_IDS = {
    # Primary cosmic entities
    "Aster": 1,
    "Andromeda": 2,

    # Major deities and cosmic beings
    "Mithra": 3,
    "Luna": 4,
    "Gaia": 5,

    # Stellar goddess sisters
    "Juno": 6,
    "Brunhilda": 7,
    "Ruby": 8,
    "Chrystella": 9,
    "Celestella": 10,
    "Gigastella": 11,

    # Early cosmic/stellar
    "Rhodes": 12,
    "Marigold": 13,

    # Planetary/lunar beings
    "Terra": 14,
    "Venus": 15,
    "Io": 16,
    "Titan": 17,
    "Serenitide": 18,
    "Hesper": 19,
    "Phaestia": 20,
    "Kolob": 21,

    # Primordial life
    "Bios": 22,
    "Luca": 23,
    "Euka": 24,
    "Eve": 25,

    # Early cellular
    "Seth": 26,
    "Azura": 27,
    "Resan": 28,
    "Theron": 29,
    "Protea": 30,
    "Chronos": 31,
    "Cylla": 32,
    "Myxon": 33,
    "Euglena": 34,
    "Nectarius": 35,
    "Chlora": 36,
    "Planta": 37,
    "Mycon": 38,
    "Protist": 39,
    "Metazoa": 40,

    # Organelles personified
    "Reticulus": 41,
    "Flagella": 42,
    "Golgi": 43,
    "Peroxis": 44,
    "Vaultess": 45,
    "Centrioles": 46,
    "Nucleus": 47,

    # Bacterial/viral
    "Bacta": 48,
    "Saya": 49,
    "Viros": 50,
    "Pelagia": 51,
    "Roseobella": 52,
    "Dinoflagellus": 53,
    "Xanthus": 54,

    # Animal kingdom founders
    "Anima": 55,
    "Metazo": 56,
    "Carcinoma": 57,

    # Early animals
    "Demos": 58,
    "Cnider": 59,
    "Nettle": 60,
    "Anthus": 61,
    "Anaxydros": 62,
    "Pompom": 63,
    "Meduson": 64,
    "Conos": 65,
    "Stauros": 66,
    "Diplos": 67,
    "Jelly": 68,
    "Cubos": 69,
    "Scyphos": 70,

    # Worms and early bilaterians
    "Dutrus": 71,
    "Ambulus": 72,
    "Stomatos": 73,
    "Tracheus": 74,
    "Chordatus": 75,
    "Olfacter": 76,
    "Vertebratus": 77,
    "Tunicatus": 78,
    "Larvaceus": 79,
    "Ascidaceus": 80,
    "Proteus": 81,
    "Thallasus": 82,
    "Dolios": 83,
    "Pyros": 84,
    "Salpus": 85,

    # Cambrian explosion
    "Cambrius": 86,
    "Lobopus": 87,
    "Onychodictyon": 88,
    "Tactopus": 89,
    "Xenu": 90,
    "Gracilis": 91,
    "Ferreus": 92,
    "Ferox": 93,
    "Ursus": 94,
    "Gille": 95,
    "Kerygmachelon": 96,
    "Pambdelurion": 97,
    "Arthur": 98,
    "Anomalos": 99,
    "Opabinia": 100,

    # Arthropods
    "Chelicer": 101,
    "Arachnus": 102,
    "Myriapus": 103,
    "Millipa": 104,
    "Centipus": 105,

    # Trilobites and relatives
    "Trilobites": 106,
    "Ordovices": 107,
    "Hirnan": 108,

    # Molluscs
    "Molluscus": 109,
    "Gastropus": 110,
    "Bivalvus": 111,
    "Cephalus": 112,
    "Spiralius": 113,
    "Bactridius": 114,
    "Neo": 115,
    "Ammon": 116,
    "Coleos": 117,

    # Echinoderms
    "Echidna": 118,
    "Esther": 119,
    "Lily": 120,
    "Crinosa": 121,
    "Blastosa": 122,
    "Luther": 123,
    "Asteros": 124,
    "Echinos": 125,
    "Starfy": 126,
    "Ophis": 127,
    "Britta": 128,
    "Serpentus": 129,
    "Baskette": 130,
    "Aristotle": 131,
    "Cucus": 132,

    # Crustaceans
    "Crustaceus": 133,
    "Ectus": 134,
    "Malacus": 135,
    "Caridus": 136,
    "Phyllos": 137,
    "Hoplos": 138,
    "Peras": 139,
    "Possa": 140,
    "Amphipus": 141,
    "Isopus": 142,
    "Yuval": 143,
    "Decapus": 144,
    "Krillon": 145,
    "Pleos": 146,
    "Prawnmegas": 147,
    "Repton": 148,
    "Shrimpon": 149,
    "Thalasson": 150,
    "Omar": 151,
    "Meiuron": 152,
    "Anomuron": 153,
    "Saraton": 154,
    "Paguros": 155,
    "Menses": 156,

    # Fish ancestors
    "Ostichthus": 157,
    "Osticthus": 158,  # variant spelling
    "Brachios": 159,
    "Acanthos": 160,
    "Chondros": 161,
    "Actinos": 162,
    "Dipnos": 163,
    "Pulmon": 164,
    "Sarcopteryx": 165,
    "Ichtheus": 166,
    "Coel": 167,
    "Canus": 168,
    "Lazer": 169,
    "Leviathan": 170,

    # Tetrapods
    "Tiktaalik": 171,
    "Acantho": 172,
    "Ichthyos": 173,
    "Stega": 174,
    "Tulerpeton": 175,

    # Amphibians
    "Fros": 176,
    "Caecilia": 177,
    "Urodeles": 178,

    # Reptiles
    "Reptilus": 179,
    "Anapsidus": 180,
    "Syntapsidus": 181,
    "Diapsidus": 182,
    "Pelycus": 183,
    "Therion": 184,
    "Cynognath": 185,

    # Synapsids/Mammals
    "Mammalus": 186,
    "Monotremus": 187,
    "Marsupia": 188,
    "Placentus": 189,

    # Dinosaurs
    "Dinosaurus": 190,
    "Ornithis": 191,
    "Sauris": 192,
    "Theropodus": 193,
    "Tyrannos": 194,

    # Birds
    "Archaeopteryx": 195,
    "Avius": 196,

    # Plants
    "Plantus": 197,
    "Bryophylla": 198,
    "Pteridios": 199,
    "Gymnosper": 200,
    "Angiosper": 201,
    "Lichen": 202,

    # Fungi
    "Mycos": 203,
    "Chytros": 204,

    # Silurian period
    "Silur": 205,
    "Eurypter": 206,
    "Chasmas": 207,
    "Belangkas": 208,
    "Xiphos": 209,
    "Soliber": 210,
    "Opiliona": 211,
    "Pneumaran": 212,
    "Kitzi": 213,
    "Solaran": 214,
    "Acares": 215,
    "Sarco": 216,
    "Trombo": 217,
    "Solifugon": 218,
    "Ricinulon": 219,
    "Byblos": 220,
    "Paras": 221,
    "Mesos": 222,
    "Holoxos": 223,
    "Thyrus": 224,
    "Ricinus": 225,

    # Devonian period
    "Devon": 226,
    "Denton": 227,
    "Dietrich": 228,

    # Carboniferous
    "Carbonifer": 229,
    "Rhea": 230,
    "Romulus": 231,
    "Remus": 232,
    "Hexapus": 233,
    "Vernus": 234,
    "Proturus": 235,
    "Collembo": 236,
    "Tails": 237,
    "Dipluron": 238,
    "Ectognus": 239,
    "Archegnos": 240,
    "Zerygos": 241,
    "Zygentos": 242,
    "Pterygos": 243,
    "Isopter": 244,
    "Dezotopter": 245,
    "Seizapter": 246,
    "Quatorzapter": 247,
    "Duzapter": 248,
    "Decapter": 249,
    "Octapter": 250,
    "Hexapter": 251,
    "Insectus": 252,
    "Ephemeros": 253,
    "Draco": 254,
    "Neopter": 255,
    "Odonatos": 256,

    # Biblical/mythological
    "Lilith": 257,
    "Cain": 258,
    "Abel": 259,
    "Enki": 260,
    "Adapa": 261,

    # Ordovician
    "Ordovician": 262,

    # Other notable
    "Myry": 263,
    "Polycomb": 264,
    "Rhizar": 265,
    "Paraxus": 266,
    "Scorpio": 267,
    "Choanos": 268,
    "Cyath": 269,
    "Chondrocles": 270,
    "Entelodos": 271,
    "Barameda": 272,
    "Quiyah": 273,
    "Pluvia": 274,
    "Amaterasu": 275,
    "Usagi": 276,
    "Vaalbara": 277,
    "Tezca": 278,
    "Silvio": 279,
    "Silurian": 280,
}

def add_character_tags(content):
    """Add {{c|ID|Name}} tags to character mentions."""
    # Split on existing tags to avoid re-tagging
    tag_pattern = r'(\{\{c\|\d+\|[^}]+\}\})'
    parts = re.split(tag_pattern, content)

    # Process only non-tag parts
    for i in range(len(parts)):
        if not parts[i].startswith('{{c|'):
            # Sort by length (longest first) to avoid partial matches
            for name in sorted(CHARACTER_IDS.keys(), key=len, reverse=True):
                char_id = CHARACTER_IDS[name]
                # Match the name as a whole word
                pattern = rf'\b{re.escape(name)}\b'
                parts[i] = re.sub(pattern, rf'{{{{c|{char_id}|{name}}}}}', parts[i])

    return ''.join(parts)

def process_all_chapters():
    """Process all chapters 001-062."""
    epic_dir = Path("/home/user/Gaiad-and-Literature-work/epic")

    # Get chapters 001-062
    chapter_files = (sorted(epic_dir.glob("chapter_0[0-5][0-9].md")) +
                    sorted(epic_dir.glob("chapter_06[0-2].md")))

    print(f"Processing {len(chapter_files)} chapters...")
    print(f"Total characters to tag: {len(CHARACTER_IDS)}\n")

    for i, chapter_file in enumerate(chapter_files, 1):
        # Read original content
        with open(chapter_file, 'r', encoding='utf-8') as f:
            original = f.read()

        # Add tags
        tagged = add_character_tags(original)

        # Write back
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(tagged)

        # Count tags added
        tags_count = len(re.findall(r'\{\{c\|\d+\|', tagged))
        print(f"{i:2d}. {chapter_file.name}: {tags_count} character tags")

    print("\nDone! All chapters have been tagged.")

if __name__ == "__main__":
    process_all_chapters()

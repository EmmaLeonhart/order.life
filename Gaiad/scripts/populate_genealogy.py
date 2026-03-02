#!/usr/bin/env python3
"""
Populate genealogy JSON files with parent-child relationships and Wikidata QIDs.

This script extracts genealogical data from the characters_index.md and
character_ids.csv files, then updates the individual character JSON files
in Gaiad/genealogy/ with:
  - father / mother relationships
  - children lists
  - wiki_qid mappings (for well-known mythological/historical figures)

It is designed to be run multiple times safely (idempotent).
"""

import json
import os
import re
import glob

GENEALOGY_DIR = os.path.join(os.path.dirname(__file__), '..', 'genealogy')
CHARACTERS_INDEX = os.path.join(os.path.dirname(__file__), '..', '..', 'summaries', 'characters_index.md')
CHARACTER_IDS = os.path.join(os.path.dirname(__file__), '..', 'epic', 'character_ids.csv')


def load_genealogy_file(name):
    """Load a character's genealogy JSON file."""
    safe_name = name.lower().replace(' ', '-').replace("'", '').replace('.', '')
    path = os.path.join(GENEALOGY_DIR, f"{safe_name}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f), path
    # Try other variations
    for variant in [
        safe_name.replace('the-', '').replace('-the-', '-'),
        safe_name.replace('é', 'e').replace('à', 'a').replace('ö', 'o'),
        safe_name.split('-')[0],  # first word only
    ]:
        path = os.path.join(GENEALOGY_DIR, f"{variant}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f), path
    return None, None


def save_genealogy_file(data, path):
    """Save a character's genealogy JSON file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def find_file_for_name(name):
    """Find the genealogy JSON file path for a character name."""
    safe_name = name.lower().replace(' ', '-').replace("'", '').replace('.', '')
    path = os.path.join(GENEALOGY_DIR, f"{safe_name}.json")
    if os.path.exists(path):
        return path
    # Try variants
    for variant in [
        safe_name.replace('the-', '').replace('-the-', '-'),
        safe_name.replace('é', 'e').replace('à', 'a').replace('ö', 'o'),
        safe_name.split('-')[0],
    ]:
        path = os.path.join(GENEALOGY_DIR, f"{variant}.json")
        if os.path.exists(path):
            return path
    return None


# ============================================================
# PART 1: Explicit parent-child relationships from the epic
# ============================================================
# These are extracted from characters_index.md descriptions.
# Format: (child_name, father_name, mother_name)
# Use None where relationship is unknown or not stated.

RELATIONSHIPS = [
    # ---- Chapters 1-5: Cosmic/Stellar figures ----
    # Aster and Andromeda are primordial, no parents
    ("Rhodes", "Ruby", None),        # Ch4: Son of Ruby
    ("Marigold", "Chrystella", None), # Ch4: Daughter of Chrystella

    # ---- Chapter 7: Cyborg brothers ----
    # Bios, Viros, Dedos are brothers - children of the cosmic lineage

    # ---- Chapter 12: Nolah's lineage (Bios line) ----
    ("Kenan", "Bios", None),
    ("Aenos", "Kenan", None),
    ("Malathan", "Aenos", None),
    ("Jared", "Malathan", None),     # from Phaestia in Nolah's lineage
    ("Maharoch", "Jared", None),
    ("Enid", "Maharoch", None),
    ("Pahadok", "Enid", None),
    ("Pelod", "Pahadok", None),
    ("Aroch", "Pelod", None),
    ("Nerod", "Aroch", None),
    ("Larthok", "Nerod", None),
    ("Idris", "Larthok", None),
    ("Methuselah", "Idris", None),
    ("Lammes", "Methuselah", None),

    # ---- Chapter 12: Nemla's lineage (Viros line) ----
    ("Caynen", "Viros", None),
    ("Hanos", "Caynen", None),
    ("Mehuthen", "Hanos", None),
    ("Irad", "Mehuthen", None),      # born on Phaestia
    ("Malathok", "Irad", None),
    ("Hanad", "Malathok", None),
    ("Peladok", "Hanad", None),
    ("Sarnod", "Peladok", None),
    ("Alok", "Sarnod", None),
    ("Illod", "Alok", None),
    ("Umroch", "Illod", None),
    ("Oblas", "Umroch", None),
    ("Makusholah", "Oblas", None),
    ("Romas", "Makusholah", None),

    # ---- Chapter 13: Solar system ----
    ("Mercury", "Sol", None),
    ("Venus", "Sol", None),
    ("Gaia", "Sol", None),
    ("Mars", "Sol", None),
    ("Ceres", "Sol", None),
    ("Jupiter", "Sol", None),
    ("Saturn", "Sol", None),
    ("Uranus", "Sol", None),
    ("Neptune", "Sol", None),

    # Moons as children of planets
    ("Io", "Jupiter", None),
    ("Europa", "Jupiter", None),
    ("Ganymede", "Jupiter", None),   # moon of Jupiter in ch13
    ("Enceladus", "Saturn", None),
    ("Titan", "Saturn", None),

    # ---- Chapter 16: Luca's children ----
    ("Arka", "Luca", None),
    ("Bacta", "Luca", None),

    # ---- Chapter 16: Arka's lineage ----
    ("Dipana", "Arka", None),
    ("Proteus", "Arka", None),
    ("Asgarda", "Proteus", None),
    ("Heimdalla", "Asgarda", None),
    ("Odina", "Asgarda", None),
    ("Thora", "Asgarda", None),
    ("Lokia", "Asgarda", None),
    ("Hela", "Asgarda", None),

    # ---- Chapter 17: Bacta's lineage ----
    ("Hydra", "Bacta", None),
    ("Terra", "Bacta", None),
    ("Proteus", "Hydra", None),      # Note: different Proteus from Arka's son
    ("Aqua", "Hydra", None),
    ("Alif", "Proteus", None),
    ("Beth", "Proteus", None),
    ("Camilla", "Proteus", None),
    ("Mixo", "Proteus", None),
    ("Rachel", "Alif", None),
    ("Kalia", "Alif", None),
    ("Splauron", "Aqua", None),
    ("Chloram", "Aqua", None),
    ("Planka", "Splauron", None),
    ("Spira", "Splauron", None),
    ("Chlamydi", "Chloram", None),
    ("Korba", "Chloram", None),
    ("Chlorobia", "Korba", None),
    ("Bactero", "Korba", None),
    ("Actano", "Terra", None),
    ("Fermus", "Terra", None),
    ("Actina", "Actano", None),
    ("Prasea", "Actano", None),
    ("Saya", "Prasea", None),
    ("Chloroflexa", "Prasea", None),
    ("Firmicutie", "Fermus", None),
    ("Conan", "Fermus", None),

    # ---- Chapter 19: Proto-eukaryotic lineage ----
    ("Starvos", "Mehuthen", None),
    ("Navros", "Starvos", None),
    ("Gravros", "Navros", None),
    ("Poxus", "Gravros", "Heimdalla"),
    ("Proto-One", "Gravros", "Mardöll"),
    ("Proto-Two", "Proto-One", "Cellina"),
    ("Euka", "Proto-Two", "Nuclella"),
    ("Rickettsia", "Lilith", None),
    ("Wolbachia", "Lilith", None),

    # ---- Chapter 19-20: Euka's children ----
    ("Reticulus", "Euka", "Eve"),
    ("Flagella", "Euka", "Eve"),
    ("Golgi", "Euka", "Eve"),
    ("Peroxis", "Euka", "Eve"),
    ("Vaultess", "Euka", "Eve"),
    ("Nucleus the Second", "Euka", "Eve"),

    # ---- Chapter 20: Seth's line ----
    ("Seth", "Euka", None),
    ("Resan", "Seth", "Azura"),
    ("Theron", "Resan", None),
    ("Protea", "Theron", None),
    ("Chronos", "Protea", None),
    ("Bios-Neos", "Protea", None),
    ("Myxon", "Chronos", "Cylla"),
    ("Euglena", "Myxon", None),
    ("Nectarius", "Bios-Neos", "Plasma-Belle"),
    ("Planta", "Nectarius", "Chlora"),
    ("Mycon", "Nectarius", "Chlora"),
    ("Protist", "Nectarius", "Chlora"),
    ("Metazoa", "Nectarius", "Chlora"),

    # ---- Chapter 21: Nectarius's kingdom ----
    ("Animus", "Nectarius", "Ambrosia"),
    ("Plantus", "Nectarius", "Ambrosia"),
    ("Opima", "Nectarius", "Ambrosia"),
    ("Cortica", "Nectarius", "Ambrosia"),
    ("Plastidus", "Plantus", "Chlora"),
    ("Glauca", "Plastidus", "Cortica"),
    ("Alges", "Plastidus", "Cortica"),
    ("Alga", "Plastidus", "Cortica"),
    ("Rhodes", "Alga", "Alges"),     # Ch21-22: red algae king
    ("Vert", "Alga", "Alges"),
    ("Ozymandias", "Animus", "Opima"),
    ("Podius", "Ozymandias", None),
    ("Metamon", "Ozymandias", None),

    # ---- Chapter 22: Complex protist genealogy ----
    ("Hacroses", "Plantus", None),
    ("Haroses", "Hacroses", None),
    ("Haptistus", "Hacroses", None),
    ("Heterokon", "Haroses", None),
    ("Alveolus", "Haroses", None),
    ("Rhizar", "Haroses", None),
    ("Ochros", "Heterokon", None),
    ("Oomy", "Heterokon", None),
    ("Bigyres", "Heterokon", None),
    ("Rosa", "Rhodes", None),
    ("Diana", "Ochros", "Rosa"),
    ("Kelpus", "Ochros", "Rosa"),
    ("Synura", "Ochros", "Rosa"),
    ("Chrysanthema", "Ochros", "Rosa"),
    ("Cilliofer", "Alveolus", "Okra"),
    ("Myzo", "Alveolus", "Okra"),
    ("Dinoflagellus", "Myzo", None),
    ("Malarius", "Myzo", None),

    # ---- Chapter 23: Post-extinction recovery ----
    ("Nephillus", "Rhizar", None),
    ("Filoses", "Rhizar", None),
    ("Chlorar", "Filoses", None),
    ("Thaumatus", "Filoses", None),
    ("Paul", "Thaumatus", None),
    ("Vampyrellida", "Nephillus", None),
    ("Testatus", "Nephillus", None),
    ("Radios", "Testatus", None),
    ("Gromius", "Testatus", None),
    ("Zancleus", "Radios", None),
    ("Retar", "Radios", None),
    ("Acanthar", "Radios", None),
    ("Foramer", "Retar", None),
    ("Polycyston", "Retar", None),
    ("Nummulus", "Foramer", None),
    ("Esther", "Foramer", None),
    ("Monoth", "Foramer", None),
    ("Spiculus", "Monoth", None),
    ("Oceana", "Monoth", None),

    # ---- Chapter 24: Choanos line ----
    ("Mebarasi", "Choanos", "Chana"),
    ("Corona", "Choanos", "Chana"),
    ("Diana the Augmented", "Corona", "Silicarius"),

    # ---- Chapter 25: Anima & Metazo ----
    ("Therion", "Metazo", "Anima"),

    # ---- Chapter 26: Therion's children ----
    ("Porifer", "Therion", None),
    ("Thallus", "Therion", None),
    ("Cloudi", "Therion", None),
    ("Cloudina", "Cloudi", None),
    ("Namacalathus", "Cloudi", None),
    ("Wallas", "Porifer", None),
    ("Solenos", "Wallas", None),
    ("Leucon", "Solenos", None),
    ("Sponga", None, "Solenos"),     # Sponga works with Leucon
    ("Vitrius", "Leucon", "Sponga"),
    ("Spongius", "Leucon", "Sponga"),
    ("Aristos", "Spongius", None),
    ("Demos", "Spongius", None),
    ("Anu", "Aristos", None),
    ("Calcidoros", "Aristos", None),

    # ---- Chapter 27: Anu's children ----
    ("Enki", "Anu", None),
    ("Homos", "Anu", None),
    ("Paraxus", "Enki", None),
    ("Xiangus", "Enki", None),
    ("Daihua", "Xiangus", None),
    ("Dinomischus", "Daihua", None),
    ("Siphus", "Dinomischus", None),

    # ---- Chapter 28: Paraxus's children ----
    ("Bilateron", "Paraxus", None),
    ("Cnider", "Paraxus", None),
    ("Placus", "Paraxus", None),
    ("Coelomus", "Bilateron", "Vendia"),
    ("Xenus", "Bilateron", "Vendia"),
    ("Nephrus", "Coelomus", "Kimberella"),
    ("Cambrius", "Nephrus", "Ikaria"),

    # ---- Chapter 29: Lichens ----
    ("Glomer", "Arbusculus", "Amber"),
    ("Ashley", "Arbusculus", "Amber"),

    # ---- Chapter 30: Cnider's children ----
    ("Anthus", "Cnider", None),
    ("Anaxydros", "Cnider", None),
    ("Pompom", "Anaxydros", None),
    ("Meduson", "Anaxydros", None),
    ("Conos", "Pompom", None),
    ("Stauros", "Pompom", None),
    ("Diplos", "Meduson", None),
    ("Jelly", "Meduson", None),
    ("Scyphos", "Jelly", None),
    ("Cubos", "Jelly", None),

    # ---- Chapter 31: Cambrian divergence ----
    ("Protos", "Cambrius", "Spriggina"),
    ("Dutrus", "Cambrius", "Spriggina"),
    ("Saccorhytus", "Dutrus", None),
    ("Dietrich", "Dutrus", None),
    ("Ectus", "Protos", None),
    ("Spiralius", "Protos", None),

    # ---- Chapter 32: Ecdysozoans ----
    ("Ishmael", "Ectus", None),
    ("Isaac", "Ectus", None),
    ("Priapus", "Ishmael", None),
    ("Draco", "Ishmael", None),
    ("Nematus", "Isaac", None),
    ("Gordy", "Isaac", None),
    ("Rhineheart", "Isaac", None),
    ("Lobopus", "Rhineheart", None),
    ("Loricus", "Rhineheart", None),

    # ---- Chapter 33: Spiralians ----
    ("Kimberella", "Spiralius", None),
    ("Gnathifer", "Spiralius", None),
    ("Gnathos", "Gnathifer", None),
    ("Xenognath", "Gnathifer", None),
    ("Marinus", "Xenognath", None),
    ("Limnos", "Xenognath", None),
    ("Rotiferus", "Marinus", None),
    ("Amisquius", "Marinus", None),
    ("Acanthus", "Rotiferus", None),

    # ---- Chapter 34: Deuterostomes ----
    ("Ambulus", "Dietrich", None),
    ("Chordatus", "Dietrich", None),

    # ---- Chapter 35: Arthropod evolution ----
    ("Cyath", "Demos", None),
    ("Chondrocles", "Demos", None),
    ("Onychodictyon", "Lobopus", None),
    ("Tactopus", "Onychodictyon", None),
    ("Xenu", "Onychodictyon", None),
    ("Ferreus", "Tactopus", None),
    ("Ferox", "Tactopus", None),
    ("Gracilis", "Xenu", None),
    ("Paucipodes", "Gracilis", None),
    ("Microdictyon", "Gracilis", None),
    ("Xenianus", "Gracilis", None),
    ("Therion Velvetclaw", "Gracilis", None),
    ("Xenusia", "Xenianus", None),
    ("Diania", "Xenianus", None),
    ("Cardios", "Therion Velvetclaw", None),
    ("Hallucigena", "Therion Velvetclaw", None),
    ("Sparsa", "Hallucigena", None),
    ("Fortis", "Hallucigena", None),
    ("Hongmen", "Hallucigena", None),
    ("Annika", "Hallucigena", None),
    ("Luolishania", "Hongmen", None),
    ("Collins Monster", "Hongmen", None),
    ("Ursus", "Ferox", None),
    ("Gille", "Ferreus", None),
    ("Kerygmachelon", "Gille", None),
    ("Pambdelurion", "Kerygmachelon", None),
    ("Arthur", "Pambdelurion", None),
    ("Anomalos", "Pambdelurion", None),
    ("Opabinia", "Pambdelurion", None),

    # ---- Chapter 36: Arthropods proper ----
    ("Arthropus", "Arthur", None),
    ("Fuxi", "Arthur", None),
    ("Ferron", "Arthropus", None),
    ("Isoxys", "Arthropus", None),
    ("Megacheiron", "Ferron", None),
    ("Euthyphro", "Ferron", None),
    ("Pantopus", "Megacheiron", None),
    ("Insectus", "Euthyphro", None),
    ("Arachnus", "Euthyphro", None),
    ("Mandibulus", "Insectus", None),
    ("Crustaceus", "Mandibulus", None),
    ("Euthy", "Mandibulus", None),
    ("Trilos", "Arachnus", None),
    ("Serk", "Arachnus", None),
    ("Chelicer", "Serk", None),
    ("Trilobon", "Trilos", None),
    ("Marrella", "Trilos", None),
    ("Esmeralda", "Trilos", None),
    ("Retifacia", "Trilos", None),
    ("Trilobeth", "Trilobon", None),
    ("Xander", "Trilobon", None),
    ("Necta", "Trilobon", None),
    ("Helmut", "Trilobon", None),
    ("Redlich", "Trilobeth", None),
    ("Agnos", "Trilobeth", None),
    ("Corynex", "Redlich", None),
    ("Lichida", "Corynex", None),
    ("Odontos", "Lichida", None),
    ("Ptychos", "Redlich", None),
    ("Proetes", "Ptychos", None),
    ("Asaphus", "Ptychos", None),
    ("Harpeth", "Ptychos", None),
    ("Phacos", "Ptychos", None),

    # ---- Chapter 37: Annelids ----
    ("Annelon", "Annelidus", None),
    ("Segmentus", "Annelon", None),
    ("Ribbon", "Annelon", None),
    ("Pleistos", "Segmentus", None),
    ("Amphon", "Segmentus", None),
    ("Amphinos", "Amphon", None),
    ("Sipuncula", "Amphon", None),
    ("Vermo", "Pleistos", None),
    ("Errantius", "Pleistos", None),
    ("Greatswimmer", "Errantius", None),
    ("Phyllos", "Greatswimmer", None),
    ("Eunice", "Greatswimmer", None),
    ("Eartha", "Vermo", None),
    ("Sapion", "Vermo", None),
    ("Hestia", "Vermo", None),
    ("Orbinida", "Vermo", None),
    ("Sabella", "Sapion", None),
    ("Spiona", "Sapion", None),
    ("Riftia", "Hestia", None),
    ("Lamella", "Hestia", None),
    ("Terraclithia", "Eartha", None),
    ("Echiuron", "Eartha", None),
    ("Terebella", "Terraclithia", None),
    ("Clitella", "Terraclithia", None),
    ("Spaghettes", "Terebella", None),
    ("Pompeii", "Terebella", None),
    ("Acros", "Terebella", None),

    # ---- Chapter 38: Echinoderms ----
    ("Hemichus", "Ambulus", None),
    ("Acorn", "Hemichus", None),
    ("Oak", "Hemichus", None),
    ("Biscarpon", "Oak", None),
    ("Pterobronk", "Oak", None),
    ("Ctenocyston", "Biscarpon", None),
    ("Cincton", "Biscarpon", None),
    ("Soluton", "Cincton", None),
    ("Helicoplacus", "Soluton", None),
    ("Pentus", "Helicoplacus", "Adria-Esther"),
    ("Stromatos", "Pentus", None),
    ("Lepidos", "Stromatos", None),
    ("Felbabka", "Lepidos", None),
    ("Echidna", "Felbabka", None),

    # ---- Chapter 39: Land colonization ----
    ("Myry", "Euthy", None),
    ("Cain", "Myry", None),
    ("Abel", "Myry", None),
    ("Centipus", "Cain", None),

    # ---- Chapter 40: Mollusks ----
    ("Molluscus", "Wiwaxius", None),
    ("Kamptos", "Wiwaxius", None),
    ("Testar", "Molluscus", None),
    ("Solenos", "Molluscus", None),
    ("Caudos", "Molluscus", None),
    ("Chiton Horizontus", "Testar", None),
    ("Conchifer Verticus", "Testar", None),
    ("Bivos", "Conchifer Verticus", None),
    ("Monos", "Conchifer Verticus", None),
    ("Carlos", "Monos", None),
    ("Gastropus", "Carlos", None),
    ("Digitos", "Carlos", None),
    ("Cephalopus", "Digitos", None),
    ("Scaphopus", "Digitos", None),

    # ---- Chapter 43: Leviathan ----
    ("Leviathan", "Magog", None),
    ("Ordovices", "Leviathan", None),

    # ---- Chapter 44: Crustaceans ----
    ("Karkon", "Crustaceus", None),
    ("Mushi", "Crustaceus", None),
    ("Copepus", "Mushi", None),

    # ---- Chapter 45: Gastropods ----
    ("Limpus", "Gastropus", None),
    ("Snellon", "Gastropus", None),
    ("Vetigas", "Snellon", None),
    ("Escargon", "Snellon", None),
    ("Conchus", "Snellon", None),
    ("Marius", "Conchus", None),
    ("Heterobran", "Conchus", None),
    ("Nudos", "Heterobran", None),
    ("Aeros", "Heterobran", None),
    ("Pulmon", "Heterobran", None),
    ("Angelica", "Heterobran", None),

    # ---- Chapter 46: Echinoderms II ----
    ("Crinosa", "Esther", None),
    ("Blastosa", "Esther", None),
    ("Luther", "Echidna", None),
    ("Asteros", "Luther", None),
    ("Echinos", "Luther", None),
    ("Starfy", "Asteros", None),
    ("Ophis", "Asteros", None),
    ("Britta", "Echinos", None),
    ("Aristotle", "Echinos", None),
    ("Cucus", "Echinos", None),

    # ---- Chapter 47: Bivalves ----
    ("Peter", "Bivos", None),
    ("Aphrodite", "Bivos", None),

    # ---- Chapter 48: Cephalopods ----
    ("Plectron", "Cephalopus", None),
    ("Ellesmer", "Cephalopus", None),
    ("Endos", "Cephalopus", None),
    ("Actinos", "Cephalopus", None),

    # ---- Chapter 49: Plants on land ----
    ("Moses", "Hirnan", None),
    ("Osiris", "Hirnan", None),
    ("Polysporos", "Osiris", None),
    ("Anthoceros", "Osiris", None),

    # ---- Chapter 50: Arachnids ----
    ("Eurypter", "Silur", None),
    ("Chasmas", "Silur", None),
    ("Belangkas", "Chasmas", None),
    ("Xiphos", "Chasmas", None),
    ("Soliber", "Belangkas", None),
    ("Opiliona", "Belangkas", None),
    ("Pneumaran", "Soliber", None),
    ("Kitzi", "Soliber", None),
    ("Solaran", "Pneumaran", None),
    ("Acares", "Pneumaran", None),
    ("Sarco", "Acares", None),
    ("Trombo", "Acares", None),
    ("Solifugon", "Solaran", None),
    ("Ricinulon", "Solaran", None),
    ("Byblos", "Kitzi", None),
    ("Paras", "Kitzi", None),
    ("Mesos", "Paras", None),
    ("Holoxos", "Paras", None),
    ("Thyrus", "Holoxos", None),
    ("Ricinus", "Holoxos", None),

    # ---- Chapter 51: Eurypterids ----
    ("Eurypteron", "Eurypter", "Pulmona"),
    ("Styloner", "Eurypter", "Pulmona"),
    ("Diploper", "Eurypteron", None),
    ("Eurypterus", "Eurypteron", None),
    ("Waeringos", "Diploper", None),
    ("Carcinos", "Diploper", None),
    ("Humiller", "Waeringos", None),
    ("Adelops", "Waeringos", None),
    ("Slimon", "Humiller", "Pterra"),
    ("Pterygo", "Slimon", None),
    ("Scorpio", "Pterygo", None),
    ("Makoko", "Styloner", "Rhena"),
    ("Stylonurus", "Styloner", "Rhena"),
    ("Mycter", "Makoko", None),
    ("Kokomo", "Makoko", None),
    ("Flumon", "Mycter", None),
    ("Drepan", "Mycter", None),
    ("Hibbert", "Flumon", None),
    ("Mycterops", "Flumon", None),
    ("Megarachne", "Mycterops", None),
    ("Minirachne", "Mycterops", None),

    # ---- Chapter 52: Vertebrate jaws ----
    ("Arandus", "Vater", None),
    ("Hestracon", "Vater", None),
    ("Astrops", "Hestracon", None),
    ("Eteros", "Hestracon", None),
    ("Cyatha", "Eteros", None),
    ("Tsubasa", "Eteros", None),
    ("Thelos", "Tsubasa", None),
    ("Cephalus", "Tsubasa", None),
    ("Galeas", "Cephalus", None),
    ("Osteos", "Cephalus", None),
    ("Pituri", "Osteos", None),
    ("Ostracos", "Osteos", None),
    ("Beakon", "Pituri", None),
    ("Gnathus", "Beakon", None),

    # ---- Chapter 53: Plants ----
    ("Polycomb", "Agamemnon", "Clytemnestra"),
    ("Knoxy", "Polycomb", None),
    ("Pholon", "Knoxy", "Xylon"),
    ("Tracheus", "Pholon", None),

    # ---- Chapter 54: Welsh/Arthurian vertebrates ----
    ("Llŷr", "Devon", None),
    ("Stennisio", "Devon", None),
    ("Bran", "Llŷr", None),
    ("Caradoc", "Bran", None),
    ("Cynan", "Caradoc", None),
    ("Acantho", "Caradoc", None),
    ("Sudopedal", "Caradoc", None),
    ("Cadwr", "Cynan", None),
    ("Eudaf", "Cadwr", None),
    ("Morfawr", "Eudaf", None),
    ("Tudwal", "Morfawr", None),
    ("Rhineheart", "Morfawr", None),
    ("Cynfawr", "Tudwal", None),
    ("Antiarchon", "Tudwal", None),
    ("Custennin", "Cynfawr", None),
    ("Uther", "Custennin", None),
    ("Petallon", "Custennin", None),
    ("Arthur", "Uther", None),
    ("Maxil", "Uther", None),
    ("Arthur the Younger", "Arthur", None),
    ("Ptycho", "Arthur", None),
    ("Mary", "Ptycho", None),
    ("Icthys", "Mary", None),
    ("Mordred", "Arthur the Younger", None),
    ("Wuttago", "Arthur the Younger", None),
    ("Actino", "Arthur the Younger", None),
    ("Philip", "Mordred", None),
    ("Melehan", "Mordred", None),
    ("Brachy", "Melehan", None),
    ("Phlyctae", "Melehan", None),
    ("Eubar", "Brachy", None),
    ("Buchan", "Brachy", None),
    ("Homosteus", "Brachy", None),
    ("Pachos", "Eubar", None),
    ("Coccos", "Eubar", None),
    ("Dunkella", "Pachos", None),
    ("Aspino", "Pachos", None),
    ("Qilinyu", "Maxil", None),
    ("Entelognathus", "Qilinyu", None),
    ("Janusicthus", "Entelognathus", None),

    # ---- Chapter 55: Neo's line (cephalopods) ----
    ("Ammon", "Neo", None),
    ("Coleos", "Neo", None),

    # ---- Chapter 55: Malacus's children ----
    ("Caridus", "Malacus", None),
    ("Phyllos", "Malacus", None),
    ("Hoplos", "Malacus", None),
    ("Amphipus", "Peras", "Possa"),
    ("Isopus", "Peras", "Possa"),
    ("Decapus", "Yuval", None),
    ("Krillon", "Yuval", None),
    ("Pleos", "Decapus", None),
    ("Prawnmegas", "Decapus", None),
    ("Repton", "Pleos", None),
    ("Shrimpon", "Pleos", None),
    ("Thalasson", "Repton", None),
    ("Omar", "Repton", None),
    ("Anomuron", "Meiuron", None),
    ("Saraton", "Meiuron", None),
    ("Paguros", "Anomuron", None),

    # ---- Chapter 56: Plants on land ----
    ("Lycos", "Arboreus", None),
    ("Ginkgon", "Arboreus", None),
    ("Isolagos", "Lycos", None),
    ("Lycopodion", "Lycos", None),
    ("Quill", "Isolagos", None),
    ("Sellagine", "Isolagos", None),
    ("Phyllon", "Ginkgon", None),
    ("Pteridos", "Phyllon", None),
    ("Gymnos", "Phyllon", None),
    ("Horsa", "Pteridos", None),
    ("Euspor", "Pteridos", None),
    ("Equis", "Horsa", None),
    ("Adderos", "Euspor", None),
    ("Fernando", "Euspor", None),
    ("Ophios", "Adderos", None),
    ("Psilos", "Adderos", None),
    ("Maratton", "Fernando", None),
    ("Marattidus", "Maratton", None),
    ("Leptos", "Maratton", None),

    # ---- Chapter 57: Vertebrate fish ----
    ("Janusicthus", "Janus", None),
    ("Kondricthus", "Janusicthus", None),
    ("Osticthus", "Janusicthus", None),
    ("Acanthus", "Kondricthus", None),
    ("Actinus", "Osticthus", None),
    ("Sacropter", "Osticthus", None),

    # ---- Chapter 58: Fungi ----
    ("Ascus", "Dikar", "Ferma"),
    ("Baston", "Dikar", "Ferma"),
    ("Taphrin", "Ascus", None),
    ("Saccharos", "Ascus", None),
    ("Peziz", "Saccharos", None),
    ("Melchizedek", "Saccharos", None),
    ("Lopez", "Peziz", None),
    ("Orbillus", "Peziz", None),
    ("Ganymede", "Lopez", None),
    ("Leotios", "Lopez", None),
    ("Pyrenos", "Leotios", None),
    ("Lecanius", "Leotios", None),
    ("Ortho", "Baston", None),
    ("Puccini", "Baston", None),
    ("Botry", "Puccini", None),
    ("Ustella", "Ortho", None),
    ("Agaricus", "Ortho", None),
    ("Jello", "Agaricus", None),
    ("Bartholomew", "Agaricus", None),
    ("William", "Agaricus", None),
    ("Gemini", "Agaricus", None),
    ("Tremello", "Jello", None),
    ("Dagar", "Jello", None),

    # ---- Chapter 60: Insects ----
    ("Romulus", "Carbonifer", "Rhea"),
    ("Remus", "Carbonifer", "Rhea"),
    ("Hexapus", "Romulus", None),
    ("Vernus", "Hexapus", None),
    ("Proturus", "Hexapus", None),
    ("Collembo", "Vernus", None),
    ("Tails", "Vernus", None),
    ("Dipluron", "Tails", None),
    ("Ectognus", "Tails", None),
    ("Archegnos", "Ectognus", None),
    ("Zerygos", "Ectognus", None),
    ("Zygentos", "Zerygos", None),
    ("Pterygos", "Zerygos", None),
    ("Isopter", "Pterygos", None),
    ("Dezotopter", "Isopter", None),
    ("Seizapter", "Dezotopter", None),
    ("Quatorzapter", "Seizapter", None),
    ("Duzapter", "Quatorzapter", None),
    ("Decapter", "Duzapter", None),
    ("Octapter", "Decapter", None),
    ("Hexapter", "Octapter", None),
    ("Insectus", "Hexapter", None),
    ("Ephemeros", "Insectus", None),
    ("Draco", "Insectus", None),
    ("Neopter", "Draco", None),
    ("Odonatos", "Draco", None),

    # ---- Chapter 61: Tetrapods ----
    ("Dipnos", "Rhipidistius", None),
    ("Tetram", "Rhipidistius", None),
    ("Kenicthus", "Tetram", None),
    ("Tetracan", "Kenicthus", None),
    ("Rhizodon", "Kenicthus", None),
    ("Tetramegas", "Tetracan", None),
    ("Canowin", "Tetracan", None),
    ("Eotetras", "Tetramegas", None),
    ("Megalicthus", "Tetramegas", None),
    ("Tintetra", "Eotetras", None),
    ("Tristichos", "Eotetras", None),
    ("Platelpis", "Tintetra", None),
    ("Tiniraus", "Tintetra", None),
    ("Elpis", "Platelpis", None),
    ("Platycephalus", "Platelpis", None),
    ("Pandericthus", "Elpis", None),
    ("Tictalicus", "Pandericthus", "Stega"),
    ("Elgin", "Tictalicus", None),
    ("Ventas", "Elgin", None),
    ("Acanthos", "Ventas", None),
    ("Icthyos", "Acanthos", None),
    ("Watcher", "Icthyos", None),
    ("Crassigar", "Watcher", None),
    ("Tetrus", "Watcher", None),

    # ---- Chapter 62: Gastropod air-breathers ----
    ("Pulmon", "Gastropus", None),
    ("Siphonogloss", "Pulmon", None),
    ("Oceanus", "Pulmon", None),
    ("Terron", "Pulmon", None),
    ("Siphonar", "Oceanus", None),
    ("Sacos", "Oceanus", None),
    ("Glampyron", "Terron", None),
    ("Aeroger", "Terron", None),
    ("Glacid", "Glampyron", None),
    ("Pyramphon", "Glampyron", None),
    ("Pyramidius", "Pyramphon", None),
    ("Amphibius", "Pyramphon", None),
    ("Euple", "Aeroger", None),
    ("Hygros", "Aeroger", None),
    ("Acox", "Euple", None),
]


# ============================================================
# PART 2: Wikidata QID mappings for well-known figures
# ============================================================
# These are the real-world Wikidata QIDs for figures that correspond
# to actual mythological/historical entities.
# Only assigning QIDs where the mapping is clear and unambiguous.

WIKIDATA_QIDS = {
    # Gaiad-specific cosmic characters (internal QIDs from character_ids.csv)
    # These already have internal IDs - we map Wikidata IDs for real-world figures

    # Greek mythology
    "Agamemnon": "Q131029",       # Greek king
    "Clytemnestra": "Q192665",    # Wife of Agamemnon
    "Aphrodite": "Q35500",        # Goddess of love
    "Chronos": "Q47652",          # Titan of time (Kronos)
    "Proteus": "Q330508",         # Shape-shifting sea god
    "Ganymede": "Q131418",        # Cupbearer of the gods
    "Gaia": "Q93172",             # Earth mother goddess
    "Rhea": "Q128421",            # Titan mother of gods

    # Biblical figures
    "Abraham": "Q9190",           # Patriarch
    "Moses": "Q9077",             # Prophet/lawgiver
    "Abel": "Q333573",            # Son of Adam
    "Cain": "Q128532",            # Son of Adam
    "Seth": "Q386717",            # Third son of Adam
    "Lilith": "Q36040",           # First wife of Adam
    "Melchizedek": "Q314969",     # King of Salem
    "Methuselah": "Q327419",      # Longest-lived biblical figure
    "Ishmael": "Q133833",         # Son of Abraham
    "Isaac": "Q133872",           # Son of Abraham
    "Mary": "Q345",               # Mother of Jesus
    "Eve": "Q830183",             # First woman

    # Roman/Latin figures
    "Romulus": "Q6144",           # Founder of Rome
    "Remus": "Q131760",           # Twin brother of Romulus

    # Norse mythology
    "Heimdalla": "Q184025",       # Heimdall - watchman of the gods
    "Odina": "Q43610",            # Odin
    "Thora": "Q42952",            # Thor
    "Lokia": "Q26822",            # Loki
    "Hela": "Q180600",            # Hel - goddess of death
    "Freyr": "Q179723",           # God of fertility
    "Brunhilda": "Q155099",       # Valkyrie

    # Japanese mythology
    "Amaterasu": "Q172640",       # Sun goddess
    "Usagi": "Q223345",           # Moon rabbit (Tsuki no Usagi)

    # Hindu/Vedic
    "Shiva": "Q11378",            # Destroyer god
    "Matsya": "Q584598",          # Fish avatar of Vishnu
    "Shesha": "Q1756654",         # Serpent deity

    # Sumerian/Mesopotamian
    "Enki": "Q82811",             # God of water and wisdom
    "Anu": "Q134430",             # Sky father god
    "Adapa": "Q382170",           # First man

    # Egyptian mythology
    "Osiris": "Q45889",           # God of the dead

    # Zoroastrian/Indo-Iranian
    "Mithra": "Q171669",          # God of covenant/light

    # Arthurian legend
    "Arthur": "Q45792",           # King Arthur
    "Uther": "Q590486",           # Uther Pendragon
    "Mordred": "Q378510",         # Arthur's betrayer

    # Welsh legendary kings
    "Bran": "Q795834",            # Bran the Blessed
    "Caradoc": "Q1325036",        # Caradoc/Caractacus

    # Celestial bodies (as mythological/personified)
    "Sol": "Q525",                # The Sun
    "Luna": "Q405",               # The Moon
    "Mercury": "Q308",            # Planet Mercury
    "Venus": "Q313",              # Planet Venus
    "Mars": "Q111",               # Planet Mars
    "Jupiter": "Q319",            # Planet Jupiter
    "Saturn": "Q193",             # Planet Saturn
    "Uranus": "Q324",             # Planet Uranus
    "Neptune": "Q332",            # Planet Neptune
    "Ceres": "Q596",              # Dwarf planet
    "Io": "Q3123",                # Moon of Jupiter
    "Europa": "Q3169",            # Moon of Jupiter
    "Titan": "Q2565",             # Moon of Saturn
    "Enceladus": "Q3303",         # Moon of Saturn
    "Triton": "Q3359",            # Moon of Neptune
    "Miranda": "Q3352",           # Moon of Uranus
    "Ariel": "Q3698",             # Moon of Uranus
    "Oberon": "Q3332",            # Moon of Uranus
    "Titania": "Q3322",           # Moon of Uranus
    "Callisto": "Q3134",          # Moon of Jupiter

    # Biological concepts personified (Wikidata for the concept)
    "Luca": "Q213339",            # Last Universal Common Ancestor (LUCA)
    "Nautilus": "Q83405",         # Nautilus (genus)
    "Leviathan": "Q131784",       # Biblical sea monster
    "Aristotle": "Q868",          # The philosopher (for Aristotle's Lantern)

    # Historical
    "Bacchus": "Q44204",          # God of wine (Dionysus/Bacchus)

    # Geological periods personified
    "Cambrius": "Q79064",         # Cambrian period
    "Devon": "Q78786",            # Devonian period
    "Carbonifer": "Q79029",       # Carboniferous period
    "Silur": "Q79065",            # Silurian period

    # Other mythological
    "Janus": "Q47422",            # Two-faced Roman god
    "Hera": "Q38012",             # Greek queen of gods
    "Diana": "Q132543",           # Roman goddess of the hunt
    "Hecate": "Q170382",          # Goddess of magic
    "Kali": "Q182985",            # Hindu goddess
}


def main():
    print("Loading existing genealogy files...")
    # Build index of all existing files
    file_index = {}
    for filepath in glob.glob(os.path.join(GENEALOGY_DIR, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            name = data.get('name', '')
            file_index[name.lower()] = (data, filepath)
        except (json.JSONDecodeError, KeyError):
            continue

    print(f"Loaded {len(file_index)} character files.")

    # Helper to find a character by name
    def find_char(name):
        if not name:
            return None, None
        key = name.lower()
        if key in file_index:
            return file_index[key]
        # Try common variations
        for variant in [
            key.replace(' ', '-'),
            key.replace('-', ' '),
            key.replace('the ', '').replace(' the ', ' '),
            key.split(' ')[0],  # first word
        ]:
            if variant in file_index:
                return file_index[variant]
        return None, None

    # Track all parent->child relationships to build children lists
    children_map = {}  # parent_name -> set of child_names

    # ---- PASS 1: Set parent relationships ----
    print("\nPass 1: Setting parent relationships...")
    updates = 0
    skipped = 0
    not_found = set()

    for child_name, father_name, mother_name in RELATIONSHIPS:
        child_data, child_path = find_char(child_name)
        if not child_data:
            not_found.add(child_name)
            continue

        changed = False

        if father_name:
            father_data, _ = find_char(father_name)
            if father_data:
                if child_data.get('father') != father_name:
                    child_data['father'] = father_name
                    changed = True
                # Track for children list
                if father_name not in children_map:
                    children_map[father_name] = set()
                children_map[father_name].add(child_name)
            else:
                # Father file doesn't exist, still set the name
                if child_data.get('father') != father_name:
                    child_data['father'] = father_name
                    changed = True
                if father_name not in children_map:
                    children_map[father_name] = set()
                children_map[father_name].add(child_name)

        if mother_name:
            mother_data, _ = find_char(mother_name)
            if child_data.get('mother') != mother_name:
                child_data['mother'] = mother_name
                changed = True
            # Track for children list
            if mother_name not in children_map:
                children_map[mother_name] = set()
            children_map[mother_name].add(child_name)

        if changed:
            save_genealogy_file(child_data, child_path)
            updates += 1
        else:
            skipped += 1

    print(f"  Updated {updates} files, skipped {skipped} (already correct)")
    if not_found:
        print(f"  Could not find files for: {sorted(not_found)[:20]}...")

    # ---- PASS 2: Set children lists ----
    print("\nPass 2: Setting children lists...")
    children_updates = 0

    for parent_name, child_names in children_map.items():
        parent_data, parent_path = find_char(parent_name)
        if not parent_data:
            continue

        sorted_children = sorted(child_names)
        existing = parent_data.get('children', [])

        # Merge: add new children without removing existing ones
        merged = list(set(existing) | child_names)
        merged.sort()

        if merged != sorted(existing):
            parent_data['children'] = merged
            save_genealogy_file(parent_data, parent_path)
            children_updates += 1

    print(f"  Updated {children_updates} parent files with children lists")

    # ---- PASS 3: Set Wikidata QIDs ----
    print("\nPass 3: Setting Wikidata QIDs...")
    qid_updates = 0

    for name, qid in WIKIDATA_QIDS.items():
        char_data, char_path = find_char(name)
        if not char_data:
            # Try to find by exact filename
            continue

        # Don't overwrite existing internal QIDs (like Q1 for Aster)
        existing_qid = char_data.get('wiki_qid')
        if existing_qid and existing_qid.startswith('Q') and len(existing_qid) <= 4:
            # This is an internal QID (Q1, Q3, etc.) - skip
            continue

        if char_data.get('wiki_qid') != qid:
            char_data['wiki_qid'] = qid
            save_genealogy_file(char_data, char_path)
            qid_updates += 1

    print(f"  Updated {qid_updates} files with Wikidata QIDs")

    # ---- Summary ----
    print(f"\n=== Summary ===")
    print(f"Total relationship entries: {len(RELATIONSHIPS)}")
    print(f"Parent relationships set: {updates}")
    print(f"Children lists updated: {children_updates}")
    print(f"QIDs mapped: {qid_updates}")

    # Verify a few
    print("\n=== Spot checks ===")
    for name in ["Euka", "Nectarius", "Arthur", "Romulus", "Agamemnon", "Gaia"]:
        data, path = find_char(name)
        if data:
            print(f"  {data['name']}: father={data.get('father')}, mother={data.get('mother')}, "
                  f"children={data.get('children', [])[:5]}, qid={data.get('wiki_qid')}")


if __name__ == '__main__':
    main()

"""
Portraits of the Gaiad's people with a local free model (backlog item "Portraits with a local free model", moved to
the queue by Emma 2026-10-20). Same model and environment as the covers and chapter art
(scripts/make_chapter_art.py: Stable Diffusion XL base 1.0, CreativeML OpenRAIL++-M, whose outputs carry no claim
from the model's licensors); the images are released CC0. Each person's prompt is written by hand below: who they are,
their era and dress, since a name alone gives the model little. A portrait already drawn is skipped, so a stopped run
resumes. Needs torch with CUDA and diffusers (scratch/art-venv in inochi-no-michikyo); the images are committed.

    python scripts/make_portraits.py
"""
import sys
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "portraits"
MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
STYLE = "head and shoulders portrait, sacred illuminated manuscript painting, gold leaf background, detailed face"
NEGATIVE = ("text, letters, words, caption, watermark, signature, blurry, low quality, deformed, extra fingers, "
            "photo, modern clothing, multiple people")

# slug: (name, description). The first test batch: people the Gaiad names most often who have no likeness from life.
PEOPLE = {
    "abraham": ("Abraham", "elderly Semitic patriarch with long white beard, wool robe and head cloth, Bronze Age Canaan"),
    "david": ("David", "young king of Israel with dark curly hair and short beard, gold crown, holding a lyre"),
    "rama": ("Rama", "Hindu prince Rama with blue skin, gold crown and jewels, bow over his shoulder, serene"),
    "hammurabi": ("Hammurabi", "Babylonian king with braided square beard, round royal cap, raised hand, Mesopotamia"),
    "zarathustra": ("Zarathustra", "ancient Iranian prophet with white robe and beard, holding a fire, sacred flame"),
    "huangdi": ("Huangdi", "the Yellow Emperor of ancient China, yellow imperial robe, beaded mian crown, long beard"),
    "ashoka": ("Ashoka", "Mauryan emperor of India, turban and gold jewelry, calm face, lotus and dharma wheel"),
    "confucius": ("Confucius", "Chinese sage, elderly scholar with long grey beard, Zhou dynasty robes, hands clasped"),
    "cain": ("Cain", "first farmer, brooding young man with dark beard, rough hide clothing, wheat sheaves"),
    "abel": ("Abel", "young shepherd with gentle face, simple tunic, holding a lamb, pastoral hills"),
    "seth": ("Seth", "son of Adam, grave bearded man in plain robe, primeval paradise garden behind him"),
    "makeda": ("Makeda", "Queen of Sheba, Ethiopian queen with dark skin, gold crown and jewels, regal robes"),
}

# Other names for a portrait's person: further character-page slugs, and EXIDs in gaiad.ged (FamilySearch, Wikidata).
ALSO = {
    "huangdi": ["yellow_emperor", "Q29201"],
    "zarathustra": ["zoroaster", "Q35811"],
    "seth": ["Q107626"],
    "cain": ["Q205365"],
    "makeda": ["G8P5-MWN"],
}


def write_index():
    """static/portraits/index.tsv: each portrait and every slug or id it belongs to, read by build.py,
    wiki-scripts/entity_index.py and wiki-scripts/gedcom_portraits.py."""
    rows = ["file\tname\tmatch"]
    for slug, (name, _) in PEOPLE.items():
        if (OUT / f"{slug}.jpg").exists():
            rows.append(f"{slug}.jpg\t{name}\t{','.join([slug] + ALSO.get(slug, []))}")
    (OUT / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [s for s in PEOPLE if not (OUT / f"{s}.jpg").exists()]
    if not todo:
        write_index()
        return
    pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16",
                                                     use_safetensors=True)
    pipe.enable_model_cpu_offload()   # fits an 8 GB GPU
    pipe.set_progress_bar_config(disable=True)
    for i, slug in enumerate(PEOPLE):
        if slug not in todo:
            continue
        name, desc = PEOPLE[slug]
        g = torch.Generator("cuda").manual_seed(9000 + i)
        img = pipe(prompt=f"{STYLE}. {name}, {desc}", negative_prompt=NEGATIVE, num_inference_steps=30,
                   guidance_scale=7.0, width=896, height=1152, generator=g).images[0]
        img.resize((448, 576)).save(OUT / f"{slug}.jpg", quality=82)
        print(slug, flush=True)
    write_index()


if __name__ == "__main__":
    sys.exit(main())

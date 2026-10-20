"""
Make the cover art of the Gaiad's 13 books (Emma, 2026-10-20: the covers come from AI art, made "using a local free
model"; what they show is left to this script). One painting per book in one shared style, written to
static/covers/<month>.jpg, which scripts/epub_to_pdf.lua puts on each book's cover page in the PDF.

The model is Stable Diffusion XL base 1.0 (stabilityai/stable-diffusion-xl-base-1.0, CreativeML OpenRAIL++-M), run
locally on the GPU with diffusers. Fixed seeds, so a rerun gives the same covers. Needs torch with CUDA and diffusers,
which the site build does not; the images are committed.

    python scripts/make_cover_art.py [month ...]
"""
import sys
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "covers"
MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
STYLE = ("sacred illuminated manuscript painting, ornate gold leaf border, deep lapis blue and gold, luminous, "
         "symmetrical, mythic, highly detailed, no text")
NEGATIVE = "text, letters, words, watermark, signature, blurry, low quality, deformed, photo"

# What each book holds, from its chapters: the month, its book name, and the scene of its cover.
COVERS = {
    "sagittarius": "two cat goddesses in the cosmos spinning a ball of yarn into galaxies, the Milky Way and Andromeda",
    "capricorn": "the first ice age over a young earth, glaciers and early sea life, cephalopods glowing beneath the ice",
    "aquarius": "the first vertebrates and great insects in a primeval coal forest, houses of life branching like a tree",
    "pisces": "dinosaurs under a red sky as a great asteroid falls, small mammals fleeing to safety, an exodus",
    "aries": "the first humans by a fire after the extinction, early mammals and a family of three brothers",
    "taurus": "ancient kings and empires, ziggurat, Persian palace and the Yellow Emperor, a bull of gold",
    "gemini": "twin sages Confucius and a Roman philosopher, Rome and Chang'an facing each other across the world",
    "cancer": "a golden age of caliphs, a house of wisdom with astrolabes, Granada and the Alhambra by the ocean",
    "leo": "a lion of gold over the Americas, Maya pyramids and mound cities, a sacred book unsealed under the sun",
    "virgo": "a chronicle of popes and cathedrals, a printing press and a great open book of history",
    "libra": "balanced scales over a town hall register, a crown taken, Napoleon and the ghost of a revolution",
    "scorpius": "telegraph wires and machines across the earth, railways, a scorpion of steel and light",
    "ophiuchus": "the serpent bearer among the stars, a woman healer holding a serpent, the Milky Way meeting Andromeda",
}
SEEDS = {m: 1000 + i for i, m in enumerate(COVERS)}


def main():
    months = sys.argv[1:] or list(COVERS)
    OUT.mkdir(parents=True, exist_ok=True)
    pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16",
                                                     use_safetensors=True)
    pipe.enable_model_cpu_offload()   # fits an 8 GB GPU
    for m in months:
        g = torch.Generator("cuda").manual_seed(SEEDS[m])
        img = pipe(prompt=f"{COVERS[m]}, {STYLE}", negative_prompt=NEGATIVE, num_inference_steps=30,
                   guidance_scale=7.0, width=896, height=1152, generator=g).images[0]
        path = OUT / f"{m}.jpg"
        img.save(path, quality=88)
        print(f"{m}: {path}", flush=True)


if __name__ == "__main__":
    main()

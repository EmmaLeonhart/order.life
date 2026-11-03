"""
Make one image for every chapter of the Gaiad (Emma, 2026-10-20: "try making art for every single chapter"), with the
local free model of the book covers (scripts/make_cover_art.py: Stable Diffusion XL base 1.0, CreativeML
OpenRAIL++-M) and in their illuminated style. Each prompt is the chapter's title and its summary
(content/gaian_days.json). Written to static/chapters/NNN.jpg at half size, so 364 of them stay small;
scripts/epub_to_pdf.lua puts each under its chapter's heading in the PDF. A chapter already drawn is skipped, so a
stopped run resumes. Needs torch with CUDA and diffusers (not the site build's); the images are committed.

    python scripts/make_chapter_art.py [first last]
"""
import json
import re
import sys
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "chapters"
MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
STYLE = "sacred illuminated manuscript painting, gold leaf and lapis blue, mythic, detailed, no text"
NEGATIVE = "text, letters, words, caption, watermark, signature, blurry, low quality, deformed, photo"


def title(n):
    f = ROOT / "Gaiad" / "epic" / f"chapter_{n:03d}.md"
    first = f.read_text(encoding="utf-8").split("\n", 1)[0] if f.exists() else ""
    first = re.sub(r"\{\{[cpx]\|(?:[^}|]*\|)?([^}|]+)\}\}", r"\1", first)
    return re.sub(r"^#\s*(Chapter\s+\d+:\s*)?", "", first).strip()


def main():
    first, last = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 364)
    summaries = json.loads((ROOT / "content" / "gaian_days.json").read_text(encoding="utf-8"))["chapter_summaries"]
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [n for n in range(first, last + 1) if not (OUT / f"{n:03d}.jpg").exists()]
    if not todo:
        return
    pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16",
                                                     use_safetensors=True)
    pipe.enable_model_cpu_offload()   # fits an 8 GB GPU
    pipe.set_progress_bar_config(disable=True)
    for n in todo:
        # Style first: the prompt is cut at 77 tokens, and a long summary should lose its tail, not the style.
        prompt = f"{STYLE}. {title(n)}: {summaries.get(str(n), '')}"
        g = torch.Generator("cuda").manual_seed(5000 + n)
        img = pipe(prompt=prompt, negative_prompt=NEGATIVE, num_inference_steps=30, guidance_scale=7.0,
                   width=896, height=1152, generator=g).images[0]
        img.resize((448, 576)).save(OUT / f"{n:03d}.jpg", quality=82)
        print(f"{n:03d} {title(n)}", flush=True)


if __name__ == "__main__":
    main()

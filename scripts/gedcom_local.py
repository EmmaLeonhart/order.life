"""
The GEDCOM protocol: generate gaiad.ged exactly as CI does, into the folder CI writes it to (site/, gitignored), and
open it in the default program. Run it after every change to the GEDCOM pipeline, every time, the same way.

Emma, 2026-10-29: "we should be having a specific protocol that we run all the time for generating the GEDCOM and then
opening it up in the main program. That does not rely at all on your discretion", in "the git ignored folder that's
also the place where the CI/CD GitHub runner generates the GEDCOM file."

Steps, in the order of build.py and .github/workflows/deploy.yml:
  1. wiki-scripts/build_gaiad_ged.py -> site/gaiad<k>.ged (k: the first free number; next_free())
  2. wiki-scripts/language_gedcom.py for ja zh es hi ar fr ru uk -> site/<lang>/gaiad<k>.ged
  3. wiki-scripts/check_gedcom_links.py, the check CI fails the build on
  4. open site/gaiad<k>.ged in the default program
Left out, on her word the same day ("I don't give a fuck about the portraits and coats of arms right now"):
gedcom_portraits.py and gedcom_arms.py.

    python scripts/gedcom_local.py
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "wiki-scripts"))
from build_gaiad_ged import build, next_free   # noqa: E402

LANGS = ["ja", "zh", "es", "hi", "ar", "fr", "ru", "uk"]   # as deploy.yml


def main():
    dest = next_free(ROOT / "site" / "gaiad.ged")
    print(f"1. {dest.relative_to(ROOT)}")
    for k, v in build(dest).items():
        print(f"  {k}: {v:,}")
    for lang in LANGS:
        out = ROOT / "site" / lang / dest.name
        out.parent.mkdir(parents=True, exist_ok=True)
        print(f"2. {out.relative_to(ROOT)}")
        subprocess.run([sys.executable, str(ROOT / "wiki-scripts" / "language_gedcom.py"), str(dest), lang, str(out)],
                       check=True)
    print("3. wiki-scripts/check_gedcom_links.py (the same check CI fails on)")
    ok = subprocess.run([sys.executable, str(ROOT / "wiki-scripts" / "check_gedcom_links.py"), str(dest)]).returncode == 0
    print(f"4. opening {dest}" + ("" if ok else "  (THE LINK CHECK FAILED: MyHeritage will not export this)"))
    os.startfile(dest)


if __name__ == "__main__":
    main()

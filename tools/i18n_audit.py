import json
from pathlib import Path


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, key))
        return out
    out[prefix] = obj
    return out


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    i18n_dir = root / "content" / "i18n"
    en_path = i18n_dir / "en.json"
    en = json.loads(en_path.read_text(encoding="utf-8"))
    enf = flatten(en)

    langs = sorted(p.stem for p in i18n_dir.glob("*.json") if p.name != "en.json")
    print("Keys (flattened):", len(enf))
    print("Langs:", ", ".join(langs))
    print()

    # Print counts only (ASCII) so this works even on cp1252 consoles.
    for lang in langs:
        p = i18n_dir / f"{lang}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        f = flatten(data)

        missing = [k for k in enf.keys() if k not in f]
        same_as_en = [k for k, v in f.items() if k in enf and v == enf[k]]
        # Strings only, to avoid counting arrays/objects.
        same_str = [
            k
            for k in same_as_en
            if isinstance(enf.get(k), str) and isinstance(f.get(k), str)
        ]

        print(
            f"{lang}: missing={len(missing)} same_as_en={len(same_as_en)} same_str={len(same_str)}"
        )

    print()
    # Dump a focused report file for deeper inspection (with full unicode).
    report = {}
    for lang in langs:
        p = i18n_dir / f"{lang}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        f = flatten(data)
        same_str = [
            k for k, v in f.items() if k in enf and v == enf[k] and isinstance(v, str)
        ]
        report[lang] = {"same_str_keys": sorted(same_str)}

    (root / "tools" / "i18n_audit_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Wrote tools/i18n_audit_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


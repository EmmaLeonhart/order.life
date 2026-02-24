import pathlib
import subprocess
import re


def load_names(path: pathlib.Path):
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    names = load_names(pathlib.Path("misgenerated_names.txt"))
    if not names:
        print("no misgenerated names list available")
        return
    result = subprocess.run(["rg", "-l", "-F", "{{c|"], capture_output=True, text=True)
    files = result.stdout.strip().splitlines() if result.stdout.strip() else []
    replacements = {f"{{{{c|{name}}}}}": name for name in names}
    for file in files:
        path = pathlib.Path(file)
        text = path.read_text(encoding="utf-8")
        new = text
        for target, repl in replacements.items():
            new = new.replace(target, repl)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"updated {path}")


if __name__ == "__main__":
    main()

"""Keep wheel starter resources identical to the public checkout templates."""
from pathlib import Path
import argparse
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[1]
TARGET = PROJECT / "src/labton/resources/starter"


def desired():
    output = {}
    for name in ("LICENSE", "LICENSING.md"):
        output["project/" + name] = (PROJECT / name).read_bytes()
    for folder in ("lab_designs", "configs", "prompts", "templates"):
        for source in (PROJECT / folder).rglob("*"):
            if source.is_file() and source.suffix in {".md", ".yaml", ".json"}:
                if folder == "configs" and source.name != "lab.yaml":
                    continue
                output["project/" + source.relative_to(PROJECT).as_posix()] = source.read_bytes()
    for name in ("SINGLE_SCIENTIST.md", "MULTI_LAB.md", "PROVIDERS.md", "DECISION_PROVIDERS.md"):
        guide = PROJECT / "docs" / name
        if guide.is_file():
            output["project/docs/" + name] = guide.read_bytes()
    for name, example in (("text", "text_workflow"), ("memory", "memory_retention"), ("scientist", "single_scientist"), ("multi-lab", "multi_lab")):
        for source in (PROJECT / "examples" / example).rglob("*"):
            if (source.is_file() and source.suffix in {".py", ".yaml", ".md", ".json"}
                    and "__pycache__" not in source.parts
                    and source.name != "private_splits.json"
                    and "tests" not in source.relative_to(PROJECT / "examples" / example).parts):
                output[name + "/" + source.relative_to(PROJECT / "examples" / example).as_posix()] = source.read_bytes()
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = desired()
    actual = {p.relative_to(TARGET).as_posix(): p.read_bytes()
              for p in TARGET.rglob("*") if p.is_file() and "__pycache__" not in p.parts} if TARGET.exists() else {}
    changed = sorted(k for k in expected.keys() | actual.keys() if expected.get(k) != actual.get(k))
    if args.check:
        if changed:
            print("Starter resources need synchronization: " + ", ".join(changed), file=sys.stderr)
            return 1
    else:
        # This directory contains generated resources only.
        if TARGET.exists():
            shutil.rmtree(TARGET)
        for relative, data in expected.items():
            target = TARGET / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    print(f"Starter resources: {len(expected)} files; synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

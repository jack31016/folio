#!/usr/bin/env python3
"""Generate zh-TW Android resources; missing keys fall back to upstream English."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app/src/main/res/values/strings.xml"
DEST = ROOT / "app/src/main/res/values-zh-rTW/strings.xml"
DICTIONARY = ROOT / "translation/zh-TW.json"
PLACEHOLDER = re.compile(r"%(?:\\d+\\$)?[-#+ 0,(]*\\d*(?:\\.\\d+)?[a-zA-Z%]")

def placeholders(text):
    return sorted(p for p in PLACEHOLDER.findall(text) if p != "%%")

def encode_android(text):
    return escape(text).replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")

def main():
    source = ET.parse(SOURCE).getroot()
    keys = {x.attrib["name"]: x for x in source.findall("string") if "name" in x.attrib}
    data = json.loads(DICTIONARY.read_text(encoding="utf-8"))
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
    count = 0
    stale = []
    for key, translated in data.items():
        original = keys.get(key)
        if original is None:
            stale.append(key)
            continue
        if not isinstance(translated, str) or not translated.strip():
            raise ValueError(f"{key}: translation must be nonempty")
        if len(original) or original.text is None:
            raise ValueError(f"{key}: complex upstream XML; review manually")
        if placeholders(original.text) != placeholders(translated):
            raise ValueError(f"{key}: placeholders changed")
        if "\\n" in original.text and "\\n" not in translated:
            raise ValueError(f"{key}: escaped newline missing")
        lines.append(f'    <string name="{key}">{encode_android(translated)}</string>')
        count += 1
    if count == 0:
        raise RuntimeError("None of the translated keys are in upstream strings.xml")
    lines.append("</resources>")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ET.parse(DEST)
    print(f"Generated {count} zh-TW strings; {len(stale)} keys no longer in upstream.")
    if stale:
        print("Unmatched keys: " + ", ".join(stale), file=sys.stderr)

if __name__ == "__main__":
    main()

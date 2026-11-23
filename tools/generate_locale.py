#!/usr/bin/env python3
"""Generate complete Taiwan Traditional Chinese locale from upstream zh-Hans.

The upstream translation is a beta draft, not professionally reviewed zh-TW.
translation/zh-TW.json contains the preferred Taiwan-localized overrides.
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "app/src/main/res/values/strings.xml"
ZH_HANS = ROOT / "app/src/main/res/values-b+zh+Hans/strings.xml"
DEST = ROOT / "app/src/main/res/values-zh-rTW/strings.xml"
OVERRIDES = ROOT / "translation/zh-TW.json"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[-#+ 0,(]*\d*(?:\.\d+)?[a-zA-Z]")
STRING = re.compile(r'(<string\s+name="([^"]+)"[^>]*>)(.*?)(</string>)', re.DOTALL)

TAIWAN_TERMS = (
    ("靈動島", "動態島"),
    ("程序塢", "Dock"),
    ("程式塢", "Dock"),
    ("主屏幕", "主畫面"),
    ("主螢幕", "主畫面"),
    ("小組件", "小工具"),
    ("小元件", "小工具"),
    ("壁紙", "桌布"),
    ("鎖屏", "鎖定畫面"),
    ("應用商店", "App 商店"),
    ("設置", "設定"),
    ("默認", "預設"),
    ("視頻", "影片"),
    ("屏幕", "螢幕"),
    ("文件", "檔案"),
    ("搜索", "搜尋"),
    ("點擊", "點選"),
)

def placeholders(text):
    return sorted(PLACEHOLDER.findall(text))

def android_escape(text):
    return escape(text).replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")

def strings(root):
    return {x.get("name"): x for x in root.findall("string")}

def main():
    base_root = ET.parse(EN).getroot()
    base = strings(base_root)
    content = OpenCC("s2twp").convert(ZH_HANS.read_text(encoding="utf-8"))
    for old, new in TAIWAN_TERMS:
        content = content.replace(old, new)

    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    applied = set()

    def substitute(match):
        prefix, name, old, suffix = match.groups()
        if name not in overrides:
            return match.group(0)
        new = overrides[name]
        if not isinstance(new, str) or not new.strip():
            raise ValueError(f"{name}: translation is empty")
        if name not in base:
            raise ValueError(f"{name}: missing from English resources")
        if placeholders(base[name].text or "") != placeholders(new):
            raise ValueError(f"{name}: Android formatting arguments mismatch")
        applied.add(name)
        return prefix + android_escape(new) + suffix

    content = STRING.sub(substitute, content)
    missing_overrides = set(overrides) - applied
    if missing_overrides:
        raise ValueError("Overrides missing from Simplified Chinese: " + ", ".join(sorted(missing_overrides)))
    content = content.replace("Simplified Chinese (zh-Hans). A beta translation:",
                              "Traditional Chinese (Taiwan, zh-TW). Draft adapted from a beta translation:")
    parsed = ET.fromstring(content)
    generated = strings(parsed)
    expected = {name for name, item in base.items() if item.get("translatable") != "false"}
    if expected - set(generated):
        raise ValueError(f"Locale incomplete: missing={sorted(expected-set(generated))}")
    for name, item in generated.items():
        if placeholders(base[name].text or "") != placeholders(item.text or ""):
            raise ValueError(f"Formatting mismatch: {name}")
    source_plurals = {x.get("name") for x in base_root.findall("plurals")}
    output_plurals = {x.get("name") for x in parsed.findall("plurals")}
    if source_plurals != output_plurals:
        raise ValueError("Plural resources do not match English source")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(content, encoding="utf-8")
    print(f"Generated {len(generated)}/{len(expected)} strings, {len(output_plurals)} plurals, {len(applied)} Taiwan overrides")

if __name__ == "__main__":
    main()

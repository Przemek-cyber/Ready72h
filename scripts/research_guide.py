"""Research agent: takes the next topic from site/queue.txt, researches it with Claude + web search,
fact-checks it, and saves site/guides/<slug>.json (English + Polish). build_site.py renders the pages.

Env: ANTHROPIC_API_KEY (required), CLAUDE_MODEL (optional).
Run: python scripts/research_guide.py [--count N]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "site" / "guides"
QUEUE = ROOT / "site" / "queue.txt"
DONE = ROOT / "site" / "queue_done.txt"
API = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("CLAUDE_MODEL") or "claude-sonnet-5-5"

LANG_BLOCK = {
    "type": "object",
    "properties": {
        "slug": {"type": "string", "description": "lowercase-hyphenated URL slug in this language (Polish without diacritics)"},
        "title": {"type": "string", "description": "Question-style title people search for, max 70 chars"},
        "description": {"type": "string", "description": "Meta description, 140-160 chars"},
        "summary": {"type": "string", "description": "Direct 1-2 sentence answer to the title (shown first on the page)"},
        "sections": {"type": "array", "items": {"type": "object", "properties": {
            "h": {"type": "string"}, "p": {"type": "array", "items": {"type": "string"}}}, "required": ["h", "p"]},
            "description": "2-4 sections, each 1-3 short paragraphs"},
        "faq": {"type": "array", "items": {"type": "object", "properties": {"q": {"type": "string"}, "a": {"type": "string"}},
                                           "required": ["q", "a"]}, "description": "2-3 questions people actually ask"},
    },
    "required": ["slug", "title", "description", "summary", "sections", "faq"],
}
SCHEMA = {
    "type": "object",
    "properties": {
        "slug": {"type": "string", "description": "English slug (file name)"},
        "tool": {"type": ["string", "null"], "description": "'water' or 'cash' if the guide is about that, else null"},
        "sources": {"type": "array", "items": {"type": "object", "properties": {"title": {"type": "string"}, "url": {"type": "string"}},
                                               "required": ["title", "url"]}, "description": "2-4 sources you read; prefer official civil-protection agencies (RCB, BBK, MSB, Ready.gov, Red Cross)"},
        "en": LANG_BLOCK, "pl": LANG_BLOCK,
    },
    "required": ["slug", "tool", "sources", "en", "pl"],
}
SYSTEM = (
    "You write short, practical household-preparedness guides for ready72h.com, in English and natural Polish (same content). "
    "Use web search to read official guidance (Poland's RCB / gov.pl, Germany's BBK, Sweden's MSB, Ready.gov, Red Cross) and cite 2-4 sources. "
    "Every number or specific recommendation must come from a source you read, attributed to it in the text (e.g. 'RCB recommends...'). "
    "Calm, non-alarmist tone; general safety advice only — no medical dosing, no weapons, nothing dangerous; when unsure, say less. "
    "Do not mention any product. When done, call save_guide exactly once."
)


def call(messages: list, tools: list) -> dict:
    body = {"model": MODEL, "max_tokens": 8000, "system": SYSTEM, "messages": messages, "tools": tools}
    for attempt in range(4):
        r = requests.post(API, json=body, timeout=600, headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"})
        if r.status_code in (429, 500, 502, 503, 529):
            time.sleep(20 * (attempt + 1))
            continue
        if r.status_code >= 400:
            raise RuntimeError(f"Claude API {r.status_code}: {r.text[:500]}")
        return r.json()
    raise RuntimeError("Claude API: too many retries")


def research(topic: str, feedback: str = "", draft: dict | None = None) -> dict:
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8},
             {"name": "save_guide", "description": "Save the guide.", "input_schema": SCHEMA}]
    ask = f"Write and save a guide on: {topic}"
    if feedback:
        ask += ("\n\nA fact-checker rejected your previous draft. Fix EVERY problem below: remove or re-attribute any claim "
                "that is not supported by a source in the sources list (add the source you actually read if needed). "
                f"Problems:\n{feedback}\n\nPrevious draft:\n{json.dumps(draft, ensure_ascii=False)}")
    messages = [{"role": "user", "content": ask}]
    for _ in range(6):
        resp = call(messages, tools)
        for b in resp.get("content", []):
            if b.get("type") == "tool_use" and b.get("name") == "save_guide":
                return b["input"]
        messages.append({"role": "assistant", "content": resp["content"]})
        if resp.get("stop_reason") == "pause_turn":
            continue
        messages.append({"role": "user", "content": "Please call save_guide now."})
    raise RuntimeError("The agent did not save the guide")


def verify(g: dict) -> None:
    tools = [{"name": "verdict", "description": "Fact-check verdict.", "input_schema": {
        "type": "object", "properties": {"ok": {"type": "boolean"}, "problems": {"type": "array", "items": {"type": "string"}}},
        "required": ["ok", "problems"]}}]
    prompt = ("You are a strict fact-checker for household emergency-preparedness content. Reject (ok=false) if ANY claim is likely wrong, "
              "unattributed specific numbers appear, advice could be unsafe, the Polish text says something different from the English, "
              f"or it is alarmist. Otherwise ok=true. Answer by calling the verdict tool.\n\n{json.dumps(g, ensure_ascii=False, indent=1)}")
    messages = [{"role": "user", "content": prompt}]
    for _ in range(3):
        resp = call(messages, tools)
        v = next((b["input"] for b in resp["content"] if b.get("type") == "tool_use"), None)
        if v:
            if not v["ok"]:
                raise RuntimeError("fact-check rejected: " + "; ".join(v["problems"])[:500])
            return
        messages += [{"role": "assistant", "content": resp["content"]}, {"role": "user", "content": "Call the verdict tool now."}]
    raise RuntimeError("fact-check returned no verdict")


def validate(g: dict) -> None:
    slug_re = r"[a-z0-9]+(-[a-z0-9]+)*"
    for s in (g["slug"], g["en"]["slug"], g["pl"]["slug"]):
        if not re.fullmatch(slug_re, s) or len(s) > 70:
            raise ValueError(f"bad slug {s}")
    if (GUIDES / f"{g['slug']}.json").exists():
        raise ValueError("guide already exists")
    taken = {json.loads(f.read_text())[l]["slug"] for f in GUIDES.glob("*.json") for l in ("en", "pl")}
    if g["en"]["slug"] in taken or g["pl"]["slug"] in taken:
        raise ValueError("slug already used")
    if len([s for s in g["sources"] if str(s.get("url", "")).startswith("http")]) < 2:
        raise ValueError("need at least 2 sources")
    for l in ("en", "pl"):
        if len(g[l]["sections"]) < 2 or len(g[l]["faq"]) < 1:
            raise ValueError(f"{l}: too short")
    if g.get("tool") not in (None, "water", "cash"):
        g["tool"] = None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1)
    args = ap.parse_args()
    done = set(DONE.read_text().splitlines()) if DONE.exists() else set()
    todo = [l.strip() for l in QUEUE.read_text().splitlines() if l.strip() and not l.startswith("#") and l.strip() not in done][:args.count]
    made = []
    for topic in todo:
        try:
            g = research(topic)
            validate(g)
            try:
                verify(g)
            except RuntimeError as e:  # jedna poprawka z uwagami fact-checkera
                print(f"::notice title=Poprawka po fact-checku::{str(e)[:300]}")
                g = research(topic, str(e), g)
                validate(g)
                verify(g)
            (GUIDES / f"{g['slug']}.json").write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
            made.append(g["slug"])
            print(f"::notice title=Nowy poradnik::{g['en']['title']} / {g['pl']['title']}")
        except Exception as e:
            print(f"::warning title=Temat pominięty: {topic}::{type(e).__name__}: {str(e)[:400]}")
        with DONE.open("a") as f:
            f.write(topic + "\n")
    if not made:
        print("::error title=Brak nowych poradników::" + (", ".join(todo) or "kolejka pusta"))
        sys.exit(1)


if __name__ == "__main__":
    main()

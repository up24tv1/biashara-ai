#!/usr/bin/env python3
"""Design-gate audit: scores UI source for generic "AI slop" patterns.

Usage:
    python3 audit.py <file-or-dir> [...]
    python3 audit.py src/ --json
    python3 audit.py index.html --quiet      # score + exit code only

Exit codes: 0 = pass, 1 = hard ban present or score < 70, 2 = nothing to scan.
No third-party dependencies. Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXTS = {".html", ".htm", ".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".astro", ".css", ".scss"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "vendor",
             "__pycache__", ".venv", "venv", ".svelte-kit", "coverage"}

# (id, penalty, compiled regex, message, fix)
HARD = [
    ("purple-blue-gradient", 14,
     re.compile(r"(from-(purple|violet|indigo|fuchsia)-\d{3}[\s\S]{0,40}?to-(blue|indigo|cyan|violet|purple)-\d{3})"
                r"|(from-(blue|cyan)-\d{3}[\s\S]{0,40}?to-(purple|violet|indigo|fuchsia)-\d{3})"
                r"|(linear-gradient\([^)]*#(8b5cf6|a855f7|6366f1|7c3aed)[^)]*#(3b82f6|2563eb|0ea5e9|60a5fa))"
                r"|(linear-gradient\([^)]*#(3b82f6|2563eb|0ea5e9|60a5fa)[^)]*#(8b5cf6|a855f7|6366f1|7c3aed))", re.I),
     "purple/violet -> blue gradient", "One hue family, OKLCH-derived. See references/tokens.md"),

    ("gradient-text", 12,
     re.compile(r"bg-clip-text[\s\S]{0,60}?text-transparent|text-transparent[\s\S]{0,60}?bg-clip-text"
                r"|-webkit-background-clip\s*:\s*text", re.I),
     "gradient text (bg-clip-text + text-transparent)",
     "Solid ink. If the headline is weak, the typeface is weak."),

    ("emoji-icons", 10,
     re.compile(r"[\U0001F680✨\U0001F4A1\U0001F512\U0001F4C8\U0001F3AF\U0001F525⚡\U0001F389"
                r"\U0001F4AA\U0001F31F\U0001F4A5\U0001F680]"),
     "emoji used as iconography",
     "One icon set with consistent stroke, or mono numerals (01/02/03)."),

    ("uniform-card-chrome", 10,
     re.compile(r"rounded-2xl[^\"'`]{0,80}?shadow-lg|shadow-lg[^\"'`]{0,80}?rounded-2xl", re.I),
     "rounded-2xl + shadow-lg uniform card chrome",
     "Two surface treatments max. Hairline borders over gap-px beat shadows."),

    ("slop-copy", 12,
     re.compile(r"\b(elevate your|seamlessly|unlock the power|supercharge|revolutioniz\w+|"
                r"take (your|it) \w+ to the next level|in today'?s fast[- ]paced|game[- ]chang\w+|"
                r"cutting[- ]edge|robust solution|effortlessly|transform your \w+ with)\b", re.I),
     "marketing slop phrasing",
     "Name the specific mechanism and a number. See references/anti-slop.md §10."),

    ("fake-social-proof", 10,
     re.compile(r"★{3,}|⭐{3,}|(?:&#9733;){3,}|via\.placeholder\.com|i\.pravatar\.cc|randomuser\.me"),
     "star rows / stock avatars / placeholder social proof",
     "Real quotes or omit the section. Never fabricate a customer."),

    ("lorem", 10,
     re.compile(r"\blorem ipsum\b|\bdolor sit amet\b", re.I),
     "lorem ipsum placeholder copy",
     "Write the real pitch even in a prototype."),

    ("generic-cta-pair", 8,
     re.compile(r"(get started)[\s\S]{0,200}?(learn more)|(learn more)[\s\S]{0,200}?(get started)", re.I),
     '"Get Started" + "Learn More" CTA pair',
     "One CTA whose verb names the outcome."),

    ("black-shadow", 6,
     re.compile(r"box-shadow\s*:[^;]*rgba?\(\s*0\s*,\s*0\s*,\s*0", re.I),
     "untinted black box-shadow",
     "Tint shadows with the brand hue — black shadows read muddy."),

    ("pure-black-dark", 6,
     re.compile(r"(background(-color)?\s*:\s*(#000000|#000|black)\b)|\bbg-black\b", re.I),
     "pure black background",
     "Near-black tinted to the brand hue: oklch(14% 0.018 <h>)."),
]

SOFT = [
    ("inter-display", 7,
     re.compile(r"font-(family)?[^;{}]{0,30}(Inter|Roboto|Open\s?Sans|Lato|Montserrat|Poppins|Nunito\s?Sans)"
                r"[^;{}]{0,60}(?:\n|;|\})", re.I),
     "Inter/Roboto/Poppins family declared — confirm it is NOT the display face",
     "Display needs a face with a voice; these are workhorses only."),

    ("uniform-section-rhythm", 8,
     re.compile(r"\bpy-20\b"),
     "repeated py-20 section rhythm",
     "Vary section rhythm and container width. See references/anti-slop.md §8."),

    ("container-monotony", 6,
     re.compile(r"max-w-7xl mx-auto"),
     "every section in max-w-7xl mx-auto",
     "Alternate full-bleed, 6xl, and 68ch measures."),

    ("glass-only", 5,
     re.compile(r"backdrop-blur(-\w+)?[^\"'`]{0,40}bg-(white|black)/\d{1,2}", re.I),
     "backdrop-blur glass as the visual idea",
     "Glass is an accent on one surface, not a style."),

    ("timid-display-type", 6,
     re.compile(r"<h1[^>]*class=\"[^\"]*\btext-(xl|2xl|3xl|4xl)\b"),
     "h1 set below text-5xl",
     "Display step >= 4x body. Use clamp() and go large."),
]

# id -> (weight, regex, message) ; absence is penalised
REQUIRED = [
    ("reduced-motion", 10, re.compile(r"prefers-reduced-motion"),
     "no prefers-reduced-motion handling",
     "Required floor item 4. Static fallback must still look designed."),
    ("dark-mode", 8, re.compile(r"prefers-color-scheme|data-theme|\bdark:"),
     "no dark-mode handling",
     "Tokens on :root, redefined for dark — never inverted."),
    ("focus-visible", 6, re.compile(r":focus-visible|focus-visible:"),
     "no :focus-visible styling",
     "Visible focus rings on every interactive element."),
    ("fluid-type", 6, re.compile(r"clamp\s*\("),
     "no clamp() fluid type",
     "Display type should scale with the viewport."),
    ("depth-move", 10,
     re.compile(r"three|THREE|@react-three|r3f|Canvas|<canvas|feTurbulence|WebGL|shader|"
                r"perspective|translate3d|parallax|mix-blend-mode", re.I),
     "no depth move detected (no 3D, shader, texture, parallax, or blend)",
     "Floor item 2. See the web-3d skill."),
]

HTMLISH = {".html", ".htm", ".tsx", ".jsx", ".vue", ".svelte", ".astro"}


def iter_files(targets):
    for t in targets:
        p = Path(t)
        if p.is_file():
            if p.suffix.lower() in EXTS:
                yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in EXTS \
                        and not any(part in SKIP_DIRS for part in f.parts):
                    yield f


def lines_for(text, rx, cap=6):
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if rx.search(line):
            hits.append(i)
            if len(hits) >= cap:
                break
    if not hits and rx.search(text):
        hits.append(0)  # multiline-only match
    return hits


def scan(paths):
    findings = []
    corpus_parts, markup_parts, scanned = [], [], []
    for f in paths:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned.append(f)
        corpus_parts.append(text)
        if f.suffix.lower() in HTMLISH:
            markup_parts.append(text)
        for sev, rules in (("hard", HARD), ("soft", SOFT)):
            for rid, pen, rx, msg, fix in rules:
                hits = lines_for(text, rx)
                if hits:
                    findings.append({"severity": sev, "id": rid, "penalty": pen,
                                     "file": str(f), "lines": hits, "message": msg, "fix": fix})
    return findings, "\n".join(corpus_parts), bool(markup_parts), scanned


def main(argv=None):
    ap = argparse.ArgumentParser(description="Design-gate distinctiveness audit")
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--min-score", type=int, default=70)
    a = ap.parse_args(argv)

    paths = list(iter_files(a.targets))
    if not paths:
        print("design-gate: no scannable files (.html/.tsx/.jsx/.vue/.svelte/.astro/.css)",
              file=sys.stderr)
        return 2

    findings, corpus, has_markup, scanned = scan(paths)

    # Required checks run against the whole corpus, and only where markup exists.
    if has_markup:
        for rid, pen, rx, msg, fix in REQUIRED:
            if not rx.search(corpus):
                findings.append({"severity": "missing", "id": rid, "penalty": pen,
                                 "file": "<project>", "lines": [], "message": msg, "fix": fix})

    # Penalty is charged once per rule id, not per occurrence.
    charged, score = {}, 100
    for f in findings:
        if f["id"] not in charged:
            charged[f["id"]] = f["penalty"]
            score -= f["penalty"]
    score = max(0, score)

    hard = [f for f in findings if f["severity"] == "hard"]
    passed = not hard and score >= a.min_score

    if a.json:
        print(json.dumps({"score": score, "passed": passed,
                          "files_scanned": len(scanned), "findings": findings}, indent=2))
        return 0 if passed else 1

    order = {"hard": 0, "missing": 1, "soft": 2}
    label = {"hard": "BAN    ", "missing": "MISSING", "soft": "SIGNAL "}
    if not a.quiet:
        print(f"\ndesign-gate — {len(scanned)} file(s) scanned\n" + "─" * 64)
        if not findings:
            print("  no findings.")
        for f in sorted(findings, key=lambda x: (order[x["severity"]], -x["penalty"])):
            loc = f["file"]
            if f["lines"]:
                shown = ",".join(str(n) for n in f["lines"] if n) or "multi-line"
                loc += f":{shown}"
            print(f"  {label[f['severity']]} -{f['penalty']:<3} {f['message']}")
            print(f"           {loc}")
            print(f"           → {f['fix']}")
        print("─" * 64)

    verdict = "PASS" if passed else "FAIL"
    print(f"design-gate score: {score}/100  [{verdict}]  "
          f"(bans: {len(hard)}, threshold: {a.min_score})")
    if not passed:
        print("Not shippable. Fix the findings above, then re-run.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

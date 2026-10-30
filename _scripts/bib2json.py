#!/usr/bin/env python3
"""Convert quasylab.bib into _data/publications.json for the Publications page.

Usage (from the repository root):

    python3 _scripts/bib2json.py [quasylab.bib] [_data/publications.json]

Only the Python standard library is used. Authors whose name matches a
member or alumnus listed in _data/people.yml are flagged so the page can
highlight them.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TYPE_LABELS = {
    "article": "Journal",
    "inproceedings": "Conference",
    "incollection": "Chapter",
    "proceedings": "Editorship",
    "book": "Book",
    "phdthesis": "Thesis",
    "misc": "Other",
}

ACCENTS = {
    "'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308",
    "~": "\u0303", "=": "\u0304", ".": "\u0307", "c": "\u0327",
    "v": "\u030c", "u": "\u0306", "H": "\u030b", "k": "\u0328",
}

SYMBOLS = {
    "ss": "ß", "i": "ı", "j": "ȷ", "o": "ø", "O": "Ø", "ae": "æ", "AE": "Æ",
    "aa": "å", "AA": "Å", "l": "ł", "L": "Ł", "oe": "œ", "OE": "Œ",
    "mu": "μ", "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
    "lambda": "λ", "pi": "π", "sigma": "σ", "tau": "τ", "omega": "ω",
    "textbackslash": "\\",
}


# --------------------------------------------------------------------------
# BibTeX parsing
# --------------------------------------------------------------------------

def read_braced(text, i):
    """Return (content, next_index) for a {...} group starting at text[i]."""
    depth = 0
    start = i + 1
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    raise ValueError("unbalanced braces")


def read_quoted(text, i):
    depth = 0
    i += 1
    start = i
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == '"' and depth == 0:
            return text[start:i], i + 1
        i += 1
    raise ValueError("unterminated string")


def parse_bib(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{", text):
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            continue
        body, _ = read_braced(text, m.end() - 1)
        key, _, rest = body.partition(",")
        fields = {}
        i = 0
        while i < len(rest):
            fm = re.compile(r"\s*([\w-]+)\s*=\s*").match(rest, i)
            if not fm:
                break
            name = fm.group(1).lower()
            i = fm.end()
            if rest[i] == "{":
                value, i = read_braced(rest, i)
            elif rest[i] == '"':
                value, i = read_quoted(rest, i)
            else:
                vm = re.compile(r"[^,\s]+").match(rest, i)
                value, i = vm.group(0), vm.end()
            fields[name] = value
            cm = re.compile(r"\s*,?").match(rest, i)
            i = cm.end()
        entries.append({"type": etype, "key": key.strip(), "fields": fields})
    return entries


# --------------------------------------------------------------------------
# LaTeX to plain text
# --------------------------------------------------------------------------

def latex_to_text(s):
    s = re.sub(r"\s+", " ", s).strip()
    # Math delimiters: keep the content.
    s = s.replace("\\(", "").replace("\\)", "")
    s = re.sub(r"(?<!\\)\$", "", s)
    # Accents such as \'{e}, \'e, \c{c}, \'{\i}.
    def accent(m):
        base = m.group(2) or m.group(3)
        base = {"\\i": "i", "\\j": "j"}.get(base, base)
        return unicodedata.normalize("NFC", base + ACCENTS[m.group(1)])
    s = re.sub(r"\\(['`^\"~=.]|[cvuHk](?=[{\s]))\s*(?:\{(\\?[A-Za-z])\}|(\\?[A-Za-z]))", accent, s)
    # Formatting commands with an argument: keep the argument.
    s = re.sub(r"\\(?:emph|textit|textbf|textsc|texttt|textrm|mathrm|mathit|mathbf|mathcal|url)\s*\{", "{", s)
    # Named symbols.
    s = re.sub(r"\\([A-Za-z]+)\b\s?", lambda m: SYMBOLS.get(m.group(1), m.group(0)), s)
    # Escaped characters.
    s = re.sub(r"\\([&%$#_{}])", r"\1", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("---", "—").replace("--", "–").replace("~", " ")
    return re.sub(r"\s+", " ", s).strip()


def split_names(s):
    return [latex_to_text(n) for n in re.split(r"\s+and\s+", s.strip()) if n.strip()]


def normalize_url(u):
    return re.sub(r"\\([&%#_])", r"\1", u.strip())


# --------------------------------------------------------------------------
# Group members
# --------------------------------------------------------------------------

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)).lower()


def load_people(path):
    names = re.findall(r"^\s*-\s*name:\s*(.+?)\s*$", path.read_text(encoding="utf-8"), re.M)
    return [n.strip("\"'") for n in names]


def make_matcher(people):
    """Match on surname plus first given name (so 'Diletta Cacciagrano'
    matches 'Diletta Romana Cacciagrano')."""
    keys = set()
    for p in people:
        parts = strip_accents(p).split()
        keys.add((parts[0], parts[-1]))
    def is_member(name):
        parts = strip_accents(re.sub(r"\s+\d{4}$", "", name)).split()
        return len(parts) >= 2 and (parts[0], parts[-1]) in keys
    return is_member


# --------------------------------------------------------------------------
# Venue formatting
# --------------------------------------------------------------------------

def venue(etype, f):
    t = {k: latex_to_text(v) for k, v in f.items() if k not in ("url", "doi", "biburl")}
    parts = []
    if etype == "article":
        j = t.get("journal", "")
        if j == "CoRR" and t.get("eprint"):
            return f"arXiv:{t['eprint']}"
        vol = t.get("volume", "")
        if t.get("number"):
            vol += f"({t['number']})"
        parts = [j, vol]
    elif etype in ("inproceedings", "incollection"):
        series = t.get("series", "")
        if series and t.get("volume"):
            series += f" {t['volume']}"
        parts = [t.get("booktitle", ""), series]
    elif etype == "proceedings":
        series = t.get("series", "")
        if series and t.get("volume"):
            series += f" {t['volume']}"
        parts = [series, t.get("publisher", "")]
    else:
        parts = [t.get("publisher", "") or t.get("howpublished", "")]
    if t.get("pages"):
        parts.append(f"pp. {t['pages']}")
    return ", ".join(p for p in parts if p)


def convert(entry, is_member):
    f = entry["fields"]
    etype = entry["type"]
    names = split_names(f.get("author") or f.get("editor", ""))
    pub = {
        "key": entry["key"],
        "type": etype,
        "label": TYPE_LABELS.get(etype, "Other"),
        "year": int(re.sub(r"\D", "", f.get("year", "0")) or 0),
        "title": latex_to_text(f.get("title", "")).rstrip("."),
        "authors": [{"name": re.sub(r"\s+\d{4}$", "", n), "member": is_member(n)} for n in names],
        "editors": "author" not in f,
        "venue": venue(etype, f),
    }
    if f.get("doi"):
        pub["doi"] = normalize_url(f["doi"])
    if f.get("url"):
        pub["url"] = normalize_url(f["url"])
    if f.get("biburl"):
        pub["dblp"] = normalize_url(f["biburl"]).removesuffix(".bib")
    return pub


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "quasylab.bib"
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "_data" / "publications.json"
    is_member = make_matcher(load_people(ROOT / "_data" / "people.yml"))

    pubs = [convert(e, is_member) for e in parse_bib(src.read_text(encoding="utf-8"))]

    # Drop duplicates (same DOI, or same normalized title and year).
    seen, unique = set(), []
    for p in pubs:
        ident = (p.get("doi") or "").lower() or (strip_accents(p["title"]), p["year"])
        if ident in seen:
            print(f"skipping duplicate: {p['key']}", file=sys.stderr)
            continue
        seen.add(ident)
        unique.append(p)

    unique.sort(key=lambda p: (-p["year"], p["title"].lower()))
    dst.write_text(json.dumps(unique, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(unique)} publications to {dst.relative_to(ROOT) if dst.is_relative_to(ROOT) else dst}")


if __name__ == "__main__":
    main()

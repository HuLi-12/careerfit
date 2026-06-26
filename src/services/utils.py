import json, re
from pathlib import Path


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def normalize_text(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_lines(text: str):
    return [x.strip(" \t-•*") for x in normalize_text(text).splitlines() if x.strip()]


def contains_any(text: str, keys):
    low = (text or "").lower()
    return any(k.lower() in low for k in keys)


def unique(items):
    seen = set()
    out = []
    for x in items:
        x = str(x).strip()
        if x and x.lower() not in seen:
            seen.add(x.lower())
            out.append(x)
    return out


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


def extract_between(text, starts, ends):
    low = text.lower()
    sp = -1
    sl = 0
    for s in starts:
        p = low.find(s.lower())
        if p != -1 and (sp == -1 or p < sp):
            sp = p
            sl = len(s)
    if sp == -1:
        return ""
    begin = sp + sl
    ep = len(text)
    for e in ends:
        p = low.find(e.lower(), begin)
        if p != -1:
            ep = min(ep, p)
    return text[begin:ep].strip("：:\n ")

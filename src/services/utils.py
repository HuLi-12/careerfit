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


def deduplicate_requirements(items, taxonomy):
    """按技能分类合并同类要求，同簇只保留优先级最高的那条"""
    if not items or not taxonomy:
        return items

    # 构建 member → cluster 反向映射
    member_to_cluster = {}
    cluster_info = {}
    for cid, info in taxonomy.items():
        cluster_info[cid] = info
        for m in info.get("members", []):
            m_lower = m.lower().replace(" ", "").replace("-", "").replace("_", "")
            member_to_cluster[m_lower] = cid

    merged = {}
    for item in items:
        key = item.requirement
        # 提取技能关键词（去除"具备"/"相关能力"/"相关经验优先"）
        skill = key.replace("具备 ", "").replace(" 相关能力", "").replace(" 相关经验优先", "")
        skill_key = skill.lower().replace(" ", "").replace("-", "").replace("_", "")

        cid = member_to_cluster.get(skill_key)
        if cid and cluster_info[cid].get("merge_strategy") == "representative":
            rep = cluster_info[cid].get("representative", skill)
            if cid in merged:
                existing = merged[cid]
                # 保留优先级更高的
                pri_order = {"high": 0, "medium": 1, "low": 2}
                if pri_order.get(item.priority, 1) < pri_order.get(existing.priority, 1):
                    item.requirement = f"具备 {rep} 相关能力"
                    merged[cid] = item
                existing.keywords = list(set(existing.keywords + item.keywords))
            else:
                item.requirement = f"具备 {rep} 相关能力"
                merged[cid] = item
        else:
            # 不在分类中的直接保留
            merged[f"_raw_{id(item)}"] = item

    return list(merged.values())


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

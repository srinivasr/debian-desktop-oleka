"""Ranking for the search box. No GUI code here."""
import os

from . import recents


def score(query, text):
    """How well does `query` match `text`? Higher is better, None is no match.

    From best to worst:
      1. text starts with the query
      2. a word in the text starts with the query
      3. the query appears somewhere inside
      4. the query letters appear in order (fuzzy, "ffx" finds "Firefox")
    Shorter text wins a tie.
    """
    q = query.lower()
    t = text.lower()
    if not q:
        return 0
    if t.startswith(q):
        base = 400
    elif any(word.startswith(q) for word in t.replace("-", " ").split()):
        base = 300
    elif q in t:
        base = 200
    elif in_order(q, t):
        base = 100
    else:
        return None
    return base - len(t)


def in_order(q, t):
    """True if every letter of q appears in t, in the same order."""
    pos = 0
    for ch in q:
        pos = t.find(ch, pos)
        if pos == -1:
            return False
        pos += 1
    return True


def rank(query, apps, limit=8, counts=None):
    """Return up to `limit` apps best matching the query.

    `counts` maps desktop file name to launch count (see recents.py).
    With an empty query, most used apps come first, then alphabetical.
    The name counts fully; the comment only counts a little.
    """
    counts = counts or {}
    if not query.strip():
        by_use = sorted(apps, key=lambda a: -counts.get(os.path.basename(a.path), 0))
        return by_use[:limit]
    scored = []
    for app in apps:
        best = score(query, app.name)
        comment = score(query, app.comment) if app.comment else None
        if comment is not None and (best is None or comment - 150 > best):
            best = comment - 150
        if best is not None:
            best += recents.bonus(app, counts)
            scored.append((best, app))
    scored.sort(key=lambda pair: -pair[0])
    return [app for _, app in scored[:limit]]

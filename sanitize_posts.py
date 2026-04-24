#!/usr/bin/env python3
"""
Sanitize blog posts to remove AI tells.
Targets prose content only (p, li, blockquote tags) — not titles or meta.
"""

import re
import os
import glob

# Files to process
POST_FILES = glob.glob("blog/*.html")
POST_FILES = [f for f in POST_FILES if "_post-template" not in f and "index.html" not in f]

# ── Phrase replacements ─────────────────────────────────────────────────────
# Applied inside prose tags. Order matters — more specific first.
PHRASE_REPLACEMENTS = [
    # Weasel openers — just delete them and let the sentence start
    (r"[Ii]t(?:'|')s worth noting that\s+",       ""),
    (r"[Ii]t is worth noting that\s+",             ""),
    (r"[Ii]t(?:'|')s worth noting\s+",             ""),
    (r"[Ii]t(?:'|')s important to note that\s+",  ""),
    (r"[Ii]t is important to note that\s+",        ""),

    # Transition openers — delete and let the sentence start
    (r"^Furthermore,\s+",    ""),
    (r"^Moreover,\s+",       ""),
    (r"^Additionally,\s+",   ""),
    (r"\. Furthermore,\s+",  ". "),
    (r"\. Moreover,\s+",     ". "),
    (r"\. Additionally,\s+", ". "),

    # Conclusion markers
    (r"[Ii]n conclusion,?\s+",  ""),
    (r"[Tt]o summarise,?\s+",   ""),
    (r"[Tt]o summarize,?\s+",   ""),
    (r"[Tt]o conclude,?\s+",    ""),

    # Banned vocabulary
    (r"\bdelve into\b",           "look at"),
    (r"\bdelves into\b",          "looks at"),
    (r"\bdelved into\b",          "looked at"),
    (r"\bdive deep into\b",       "look closely at"),
    (r"\bdive into\b",            "look at"),
    (r"\bdeep dive\b",            "close look"),
    (r"\bunpack\b",               "examine"),
    (r"\bcutting-edge\b",         "new"),
    (r"\bcutting edge\b",         "new"),
    (r"\bgame-changing\b",        "significant"),
    (r"\bgame-changer\b",         "significant shift"),
    (r"\bgame changer\b",         "significant shift"),
    (r"\brobust\b",               "solid"),
    (r"\bseamlessly\b",           "cleanly"),
    (r"\bseamless\b",             "smooth"),
    (r"\bneedle(?:ss)? to say\b", ""),
    (r"\bat the end of the day\b","ultimately"),
    (r"\bleverage\b(?=\s+(?:AI|technology|data|tools|capabilities|existing|this|that|your|our|the|its|their|these|those|a |an ))", "use"),
    (r"\bleverages\b(?=\s+(?:AI|technology|data|tools|capabilities|existing|this|that|your|our|the|its|their|these|those|a |an ))", "uses"),
    (r"\bleveraged\b(?=\s+(?:AI|technology|data|tools|capabilities|existing|this|that|your|our|the|its|their|these|those|a |an ))", "used"),
    (r"\beveraging\b(?=\s+(?:AI|technology|data|tools|capabilities|existing|this|that|your|our|the|its|their|these|those|a |an ))", "using"),
    (r"\blandscape\b(?=\s+of\b)",  "world"),
    (r"\bAI landscape\b",          "AI field"),
    (r"\btechnology landscape\b",  "technology market"),
    (r"\bdigital landscape\b",     "digital world"),
    (r"\bnavigate\b(?=\s+(?:the\s+)?(?:complexity|challenges|change|uncertainty|transition|shift))", "handle"),
    (r"\bnavigating\b(?=\s+(?:the\s+)?(?:complexity|challenges|change|uncertainty|transition|shift))", "handling"),
    (r"\btransformative\b",        "significant"),
    (r"\bstreamline\b",            "simplify"),
    (r"\bstreamlined\b",           "simplified"),
    (r"\bstreamlines\b",           "simplifies"),
    (r"\bstreamlining\b",          "simplifying"),
    (r"\becosystem\b",             "environment"),
]

# ── Em dash replacements inside prose ──────────────────────────────────────
# Replace contextual em dash patterns with cleaner punctuation.
# Applied only inside prose content blocks.
EM_DASH_REPLACEMENTS = [
    # Em dash before common conjunctions/prepositions → comma
    (r" — (and |but |or |so |yet |while |whereas |though |although )",  r", \1"),
    (r" — (not |never |rather than |instead of )",                      r", \1"),
    (r" — (which |who |that |when |where |whether )",                   r", \1"),
    (r" — (including |such as |for example |for instance )",            r", \1"),
    (r" — (meaning |making |creating |allowing |enabling |helping )",   r", \1"),
    (r" — (with |without |using |via |through |by |from |to )",         r" \1"),
    (r" — (at |in |on |as |if |after |before |because |since |until )", r" \1"),
    # Em dash before present participles (verb+ing that isn't above)
    (r" — ([a-z]+ing )",  r", \1"),
    # Em dash before past participles / adjectives
    (r" — ([a-z]+ed )",   r", \1"),
    # Any remaining em dash between two lowercase words → comma
    (r"(?<=[a-z,]) — (?=[a-z])",  ", "),
]


def apply_to_prose_blocks(html: str, fn) -> str:
    """Apply fn() to the text content inside prose tags only."""
    PROSE_TAGS = re.compile(
        r'(<(?:p|li|blockquote|td|dd)[^>]*>)(.*?)(</(?:p|li|blockquote|td|dd)>)',
        re.DOTALL | re.IGNORECASE
    )
    def replace_block(m):
        open_tag, content, close_tag = m.group(1), m.group(2), m.group(3)
        return open_tag + fn(content) + close_tag
    return PROSE_TAGS.sub(replace_block, html)


def apply_replacements(text: str, rules: list) -> str:
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def count_prose_em_dashes(html: str) -> int:
    prose = re.findall(r'<(?:p|li|blockquote)[^>]*>(.*?)</(?:p|li|blockquote)>', html, re.DOTALL | re.IGNORECASE)
    return sum(block.count("—") for block in prose)


def sanitize_file(path: str) -> tuple[int, int, bool]:
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    before_dashes = count_prose_em_dashes(original)

    # Apply phrase replacements to prose blocks
    result = apply_to_prose_blocks(original, lambda t: apply_replacements(t, PHRASE_REPLACEMENTS))
    # Apply em dash replacements to prose blocks
    result = apply_to_prose_blocks(result, lambda t: apply_replacements(t, EM_DASH_REPLACEMENTS))

    after_dashes = count_prose_em_dashes(result)
    changed = result != original

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(result)

    return before_dashes, after_dashes, changed


def main():
    print(f"Processing {len(POST_FILES)} posts...\n")
    total_dash_before = 0
    total_dash_after = 0
    changed_count = 0

    for path in sorted(POST_FILES):
        before, after, changed = sanitize_file(path)
        total_dash_before += before
        total_dash_after += after
        if changed:
            changed_count += 1
            name = os.path.basename(path)
            print(f"  {name:50s}  dashes {before:2d} → {after:2d}")

    print(f"\nDone. {changed_count}/{len(POST_FILES)} files changed.")
    print(f"Total prose em dashes: {total_dash_before} → {total_dash_after} ({total_dash_before - total_dash_after} removed)")


if __name__ == "__main__":
    main()

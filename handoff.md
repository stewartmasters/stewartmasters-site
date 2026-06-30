# StewartMasters.me — Handoff

> **Rule:** Update this file after every meaningful session. It is the single source of truth for repo state.

---

## Repo Overview

- **Purpose:** Personal site — speaking, bio, blog, glossary, FAQ
- **Production:** https://stewartmasters.me
- **Staging:** Netlify preview per PR
- **Framework:** HTML/CSS static site + Python scripts for blog/speaking generation
- **Infra:** Netlify (static)
- **Repo:** stewartmasters/stewartmasters-site (local path: stewartmasters-site/)

---

## Current Status

- **Production:** ✅ Stable
- **Blog:** ✅ Active (recent posts published)
- **GSC:** ⚠️ Monitor — fixed .html → clean URL redirects to resolve duplicate canonical errors; fixed feed.xml URLs
- **RSS feed:** ✅ Fixed (feed.xml URLs match canonical tags — no .html extension)

---

## Active Workstreams

### GSC duplicate canonical cleanup
- **Status:** Done
- **Last:** Forced .html → clean URL redirects (netlify.toml) to resolve GSC duplicate canonical errors; fixed feed.xml URLs
- **Next:** Monitor GSC re-crawl
- **Key files:** `netlify.toml`, `feed.xml`

### Blog
- **Status:** Active
- **Last:** Published 2026-05-05 post; em dash cleanup; bio accuracy fixes; speaking page repetition fixed
- **Next:** Regular posting cadence via `publish.py`

---

## Last Session Summary (2026-06-30)

- New profile photo across hero + all 30 blog avatars + JSON-LD (optimized JPEG ~100KB; `.png` kept as fallback)
- Rebranded accent: electric cyan `#00D4FF` → deep teal **`#14B8A6`** site-wide (all pages, blog thumbnail SVGs, OG image, Tailwind token, cookie banner, and the 3 Python generators so future content matches)
- Cookie banner restyled to brand palette (was off-brand indigo `#1a1a2e` / blue `#4f8ef7`)
- UX/a11y: mobile hero portrait added (phones previously showed no photo), `:focus-visible` rings, `prefers-reduced-motion`
- handoff.md now committed to the repo (was previously untracked/local-only)
- **Repo note:** old local working copy was git-corrupted (missing objects). Re-cloned fresh; corrupt copy preserved as `../stewartmasters-site.corrupt-backup-20260630-091045` (safe to delete once happy)
- **Pushed:** main up to `4e9f7fd`
- **Next (optional, discussed):** stronger contact CTA copy; real testimonial headshots/logos; concrete outcome metrics in case cards

---

## Known Bugs / Risks

| Issue | Severity | Area | Workaround | Fix |
|-------|----------|------|-----------|-----|
| .html → clean URL duplicates (historical) | High | SEO | netlify.toml redirects | Fixed |
| feed.xml URL mismatch (historical) | Medium | SEO/RSS | Fixed feed.xml | Done |

---

## Architecture Notes

- **Static HTML** — not Next.js
- **Blog generation:** `publish.py` — reads from `_drafts/`, publishes to `blog/`
- **FAQ generation:** `publish_faq.py`
- **Speaking generation:** `generate_speaking.py` reads `speaking-topics.json`
- **Content sanitization:** `sanitize_posts.py` — em dash cleanup etc.
- **RSS feed:** `feed.xml` — must use clean URLs (no .html)
- **Key pages:** `index.html`, `speaking.html`, `contact.html`, `glossary.html`
- **Logos:** Local SVG/PNG (ClassPass, Enzo Ventures, ESADE, IE Business School, etc.)

---

## Commands

```bash
# Publish a blog post
python3 publish.py

# Publish FAQ
python3 publish_faq.py

# Generate speaking page
python3 generate_speaking.py

# Sanitize posts (em dashes, clichés)
python3 sanitize_posts.py

# Local preview (simple HTTP server)
python3 -m http.server 8000
```

---

## Environment Variables

No server-side env vars (fully static site). Netlify build is a simple file copy.

---

## QA Checklist

- [ ] Blog post URLs are clean (no .html)
- [ ] feed.xml URLs match canonical tags
- [ ] netlify.toml has .html → clean URL redirects
- [ ] Speaking page has no repetition
- [ ] Bio is accurate
- [ ] No em dashes in content (use sanitize_posts.py)
- [ ] GSC shows no duplicate canonical errors

---

## SEO Notes

- Clean URLs (no .html) — netlify.toml redirects enforce this
- feed.xml is the RSS source — URLs must match canonicals
- GSC: monitor for duplicate canonical issues after any URL structure changes

---

## Rules / Guardrails

- **NEVER** link to .html URLs in internal links — always clean URLs
- **ALWAYS** run sanitize_posts.py after generating new content
- **NEVER** use `git add -A` — stage specific files only
- **NEVER** change URL structure without updating netlify.toml redirects AND feed.xml

#!/usr/bin/env python3
"""
Weekly FAQ publisher for stewartmasters.me
Runs via GitHub Actions daily. Publishes if a FAQ is scheduled for today.

Logic per run:
  1. Find today's scheduled FAQ in faq/schedule.json
  2. Generate the FAQ HTML page in faq/
  3. Insert a card at the top of faq/index.html grid
  4. Insert the URL into sitemap.xml
"""

import json
import os
import re
import sys
import datetime

SCHEDULE_FILE = "faq/schedule.json"
FAQ_DIR = "faq"
FAQ_INDEX = "faq/index.html"
SITEMAP_FILE = "sitemap.xml"


def load_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def format_date_display(iso_date):
    """Convert 2026-04-21 to '21 Apr 2026'"""
    d = datetime.date.fromisoformat(iso_date)
    return d.strftime("%-d %b %Y")


def sections_html(sections):
    parts = []
    for section in sections:
        parts.append(f'    <h2 class="font-heading" style="font-size:1.5rem;font-weight:700;color:#fff;margin-top:2.5rem;margin-bottom:1rem;line-height:1.25;">{section["heading"]}</h2>')
        parts.append(f'    <p style="color:#aaa;font-size:17px;line-height:1.85;margin-bottom:1.5rem;">{section["content"]}</p>')
        if section.get("bullets"):
            parts.append('    <ul style="color:#aaa;font-size:17px;line-height:1.85;padding-left:1.5rem;margin-bottom:1.5rem;">')
            for bullet in section["bullets"]:
                parts.append(f'      <li style="margin-bottom:0.5rem;">{bullet}</li>')
            parts.append('    </ul>')
    return "\n".join(parts)


def related_cards_html(related_posts):
    cards = []
    for post in related_posts:
        cards.append(f"""      <a href="/blog/{post['slug']}.html" style="background:#121212;border:1px solid #1e1e1e;border-radius:8px;padding:24px;text-decoration:none;display:block;transition:border-color 0.3s;" onmouseover="this.style.borderColor='#2a2a2a'" onmouseout="this.style.borderColor='#1e1e1e'">
        <span style="font-size:10px;color:#00D4FF;letter-spacing:2px;text-transform:uppercase;display:block;margin-bottom:8px;">{post['category']}</span>
        <span class="font-heading" style="font-weight:600;color:#fff;font-size:15px;line-height:1.4;display:block;">{post['title']}</span>
      </a>""")
    return "\n".join(cards)


def faq_grid_card_html(entry):
    slug = entry["slug"]
    question = entry["question"]
    category = entry["category"]
    date_display = format_date_display(entry["date"])
    intro_short = entry["intro"][:120].rstrip() + "…" if len(entry["intro"]) > 120 else entry["intro"]

    return f"""      <a href="/faq/{slug}.html" class="faq-card" data-aos="fade-up">
        <span style="font-size:10px;font-weight:500;letter-spacing:2px;text-transform:uppercase;color:#00D4FF;display:block;margin-bottom:10px;">{category}</span>
        <h3 class="font-heading font-semibold text-white mb-3" style="font-size:16px;line-height:1.4;">{question}</h3>
        <p style="color:#777;font-size:13px;line-height:1.7;margin-bottom:16px;">{intro_short}</p>
        <span style="font-size:12px;color:#555;">{date_display}</span>
      </a>"""


def generate_faq_page(entry):
    slug = entry["slug"]
    question = entry["question"]
    meta_desc = entry["meta_description"]
    category = entry["category"]
    intro = entry["intro"]
    sections = entry["sections"]
    closing = entry["closing"]
    related_posts = entry["related_posts"]
    date_str = entry["date"]
    date_display = format_date_display(date_str)
    url = f"https://stewartmasters.me/faq/{slug}.html"

    schema_faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": intro + " " + " ".join(
                        s["content"] for s in sections
                    ) + " " + closing
                }
            }
        ]
    }

    schema_breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://stewartmasters.me"},
            {"@type": "ListItem", "position": 2, "name": "FAQ", "item": "https://stewartmasters.me/faq/"},
            {"@type": "ListItem", "position": 3, "name": question, "item": url}
        ]
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{question} — Stewart Masters</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{url}">

  <meta property="og:title" content="{question} — Stewart Masters">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Stewart Masters">

  <script type="application/ld+json">
  {json.dumps(schema_faq, indent=2)}
  </script>
  <script type="application/ld+json">
  {json.dumps(schema_breadcrumb, indent=2)}
  </script>

  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-T3GCWLRLH7"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('consent', 'default', {{'analytics_storage': 'denied'}});
    gtag('js', new Date());
    gtag('config', 'G-T3GCWLRLH7');
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">

  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background-color: #0D0D0D;
      color: #ffffff;
      font-family: 'Inter', sans-serif;
      -webkit-font-smoothing: antialiased;
    }}
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: #0D0D0D; }}
    ::-webkit-scrollbar-thumb {{ background: #2a2a2a; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #00D4FF; }}

    .font-heading {{ font-family: 'Space Grotesk', sans-serif; }}
    .max-container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}
    .prose {{ max-width: 720px; margin: 0 auto; }}

    nav {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      backdrop-filter: blur(24px);
      background: rgba(13, 13, 13, 0.85);
      border-bottom: 1px solid #1c1c1c;
    }}
    .nav-link {{ font-size: 14px; color: #aaa; text-decoration: none; transition: color 0.2s; }}
    .nav-link:hover {{ color: #ffffff; }}
    .btn-primary {{
      display: inline-block; background: #00D4FF; color: #0D0D0D;
      font-family: 'Space Grotesk', sans-serif; font-weight: 600;
      padding: 10px 22px; border-radius: 4px; text-decoration: none; font-size: 14px;
    }}
    .btn-primary:hover {{ background: #ffffff; }}

    .post-tag {{
      display: inline-block;
      font-size: 10px; font-weight: 500; letter-spacing: 2px;
      text-transform: uppercase; color: #00D4FF;
      border: 1px solid #00D4FF33; padding: 5px 12px; border-radius: 20px;
    }}
  </style>
  <link rel="alternate" type="application/rss+xml" title="Stewart Masters" href="https://stewartmasters.me/feed.xml">
</head>

<body>

<!-- Nav -->
<nav>
  <div class="max-container py-4 flex items-center justify-between">
    <a href="/" class="font-heading font-semibold text-white text-lg tracking-tight">Stewart Masters</a>
    <div class="hidden md:flex items-center gap-8">
      <a href="/#about" class="nav-link">About</a>
      <a href="/#services" class="nav-link">Where I Help</a>
      <a href="/blog/" class="nav-link">Thinking</a>
      <a href="/contact.html" class="nav-link">Contact</a>
    </div>
    <a href="/contact.html" class="btn-primary">Get in touch</a>
  </div>
</nav>


<!-- Article header -->
<header class="pt-40 pb-12 px-6">
  <div class="prose">
    <nav style="font-size: 12px; color: #333; margin-bottom: 24px;">
      <a href="/" style="color: #444; text-decoration: none;">Home</a>
      <span style="margin: 0 8px;">·</span>
      <a href="/faq/" style="color: #444; text-decoration: none;">FAQ</a>
      <span style="margin: 0 8px;">·</span>
      <span style="color: #555;">{category}</span>
    </nav>

    <span class="post-tag">{category}</span>

    <h1 class="font-heading text-4xl md:text-5xl font-bold leading-tight mt-5 mb-6">
      {question}
    </h1>

    <div style="display: flex; align-items: center; gap: 16px; font-size: 13px; color: #444; padding-bottom: 24px; border-bottom: 1px solid #1e1e1e;">
      <span>Stewart Masters</span>
      <span>·</span>
      <span>{date_display}</span>
    </div>
  </div>
</header>


<!-- Article body -->
<article class="px-6 pb-20">
  <div class="prose">

    <p style="color:#aaa;font-size:17px;line-height:1.85;margin-bottom:1.5rem;">
      {intro}
    </p>

{sections_html(sections)}

    <hr style="border:none;border-top:1px solid #1e1e1e;margin:3rem 0;">

    <p style="color: #777; font-size: 15px;">
      <strong style="color: #888;">Want to talk through any of this?</strong><br>
      {closing}<br><br>
      <a href="/contact.html" style="color: #00D4FF; text-decoration: underline; text-decoration-color: #00D4FF44;">Get in touch →</a>
    </p>

  </div>
</article>


<!-- Author box -->
<section class="px-6 pb-20">
  <div class="prose">
    <div style="background:#121212;border:1px solid #1e1e1e;border-radius:10px;padding:28px;display:flex;gap:20px;align-items:flex-start;">
      <div style="width:56px;height:56px;border-radius:50%;background:#1e1e1e;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:11px;color:#333;">SM</div>
      <div>
        <div class="font-heading font-semibold mb-1">Stewart Masters</div>
        <p style="color:#555;font-size:14px;line-height:1.6;margin:0;">
          Strategic advisor to founders and operators. Chief Digital Officer at Honest Greens. Guest lecturer at IE Business School and ESADE. Based in Barcelona.
          <a href="https://www.linkedin.com/in/stewartmasters/" style="color:#00D4FF;text-decoration:none;">Connect on LinkedIn →</a>
        </p>
      </div>
    </div>
  </div>
</section>


<!-- Related posts -->
<section class="px-6 pb-24" style="border-top: 1px solid #1a1a1a; padding-top: 48px;">
  <div class="prose">
    <h2 class="font-heading text-2xl font-bold mb-6" style="margin-top: 0;">Related reading</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
{related_cards_html(related_posts)}
    </div>
    <div style="text-align: center; margin-top: 24px;">
      <a href="/faq/" style="color: #444; font-size: 14px; text-decoration: none;">← All questions</a>
    </div>
  </div>
</section>


<!-- Footer -->
<footer class="py-10 px-6" style="border-top: 1px solid #141414;">
  <div class="max-container flex flex-col md:flex-row items-center justify-between gap-4">
    <span class="font-heading font-semibold" style="color: #888;">Stewart Masters</span>
    <div class="flex gap-6" style="font-size: 13px;">
      <a href="/#about" class="nav-link">About</a>
      <a href="/#services" class="nav-link">Where I Help</a>
      <a href="/blog/" class="nav-link">Thinking</a>
      <a href="/faq/" class="nav-link" style="color:#fff;">FAQ</a>
      <a href="/contact.html" class="nav-link">Contact</a>
    </div>
    <a href="https://www.linkedin.com/in/stewartmasters/" target="_blank" rel="noopener" class="nav-link" style="font-size: 13px;">LinkedIn →</a>
  </div>
  <div class="max-container mt-10 text-center" style="font-size: 11px; color: #888; letter-spacing: 2px; padding-top: 1.5rem;">BARCELONA · LONDON · MADRID</div>
</footer>

<script src="/cookie-consent.js"></script>
</body>
</html>"""

    return html


def update_faq_index(entry):
    with open(FAQ_INDEX, "r", encoding="utf-8") as f:
        html = f.read()

    new_card = faq_grid_card_html(entry)
    html = html.replace(
        "<!-- FAQ_GRID_START -->",
        f"<!-- FAQ_GRID_START -->\n\n{new_card}\n",
        1,
    )

    with open(FAQ_INDEX, "w", encoding="utf-8") as f:
        f.write(html)


def update_sitemap(entry):
    slug = entry["slug"]
    date_str = entry["date"]
    url = f"https://stewartmasters.me/faq/{slug}.html"

    new_url_block = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>"""

    with open(SITEMAP_FILE, "r", encoding="utf-8") as f:
        sitemap = f.read()

    sitemap = sitemap.replace(
        "<!-- FAQ_URLS_START -->",
        f"<!-- FAQ_URLS_START -->\n{new_url_block}",
        1,
    )

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap)


def main():
    today = datetime.date.today().isoformat()
    print(f"Running publish_faq.py for date: {today}")

    schedule = load_schedule()
    today_entry = next((e for e in schedule if e["date"] == today), None)

    if not today_entry:
        print(f"No FAQ scheduled for {today}. Nothing to publish.")
        sys.exit(0)

    slug = today_entry["slug"]
    out_path = os.path.join(FAQ_DIR, f"{slug}.html")

    if os.path.exists(out_path):
        print(f"FAQ already published: {slug}.html — skipping.")
        sys.exit(0)

    print(f"Publishing FAQ: {today_entry['question']}")

    html = generate_faq_page(today_entry)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Generated faq/{slug}.html")

    update_faq_index(today_entry)
    print(f"✓ Updated faq/index.html")

    update_sitemap(today_entry)
    print(f"✓ Updated sitemap.xml")

    print(f"\n✓ FAQ published: {today_entry['question']}")


if __name__ == "__main__":
    main()

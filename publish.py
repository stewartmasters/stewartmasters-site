#!/usr/bin/env python3
"""
Daily post publisher for stewartmasters.me
Runs via GitHub Actions at 08:00 UTC (09:00 CET / 10:00 CEST)

Logic per run:
  1. Find today's scheduled post in schedule.json
  2. Move the post HTML from blog/drafts/ to blog/ (if not already there)
  3. Replace the featured section in blog/index.html with today's post
  4. Insert the previous featured post as a grid card at the top of the grid
  5. Regenerate feed.xml with all published posts

Future posts are stored in blog/drafts/ so they are not publicly accessible
until their scheduled publish date.
"""

import json
import os
import re
import shutil
import sys
import datetime
from email.utils import format_datetime
from datetime import timezone

SCHEDULE_FILE = "blog/schedule.json"
BLOG_INDEX = "blog/index.html"
HOMEPAGE = "index.html"
FEED_FILE = "feed.xml"
BLOG_DIR = "blog"
DRAFTS_DIR = "blog/drafts"
BLOG_SKIP = {"index.html", "_post-template.html"}


def load_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def format_date_display(iso_date):
    """Convert 2026-03-20 to '20 Mar 2026'"""
    d = datetime.date.fromisoformat(iso_date)
    return d.strftime("%-d %b %Y")


def featured_html(entry):
    slug = entry["slug"]
    title = entry["title"]
    category = entry["category"]
    excerpt = entry["excerpt"]
    read_time = entry["read_time"]
    date_display = format_date_display(entry["date"])

    return f"""    <a href="{slug}.html" class="featured-card" data-aos="fade-up">
      <div class="featured-thumb">
        <img src="images/{slug}.svg" alt="{title}" style="width:100%;height:100%;object-fit:cover;">
      </div>
      <div class="p-10 flex flex-col justify-between">
        <div>
          <span style="font-size: 10px; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; color: #00D4FF; display: block; margin-bottom: 14px;">Latest · {category}</span>
          <h2 class="font-heading text-2xl md:text-3xl font-bold leading-snug mb-4">
            {title}
          </h2>
          <p style="color: #777; font-size: 15px; line-height: 1.7; margin-bottom: 24px;">
            {excerpt}
          </p>
        </div>
        <div class="flex items-center justify-between">
          <span style="font-size: 12px; color: #555;">{date_display} · {read_time} min read</span>
          <span class="blog-arrow">→</span>
        </div>
      </div>
    </a>"""


def grid_card_html(entry):
    slug = entry["slug"]
    title = entry["title"]
    category = entry["category"]
    excerpt = entry["excerpt"]
    read_time = entry["read_time"]
    date_display = format_date_display(entry["date"])

    return f"""      <a href="{slug}.html" class="blog-card" data-aos="fade-up" data-aos-delay="0">
        <div class="blog-thumb" style="background:none;padding:0;">
          <img src="images/{slug}.svg" alt="" style="width:100%;height:100%;object-fit:cover;">
        </div>
        <div class="p-6">
          <span class="post-tag">{category}</span>
          <h3 class="font-heading text-base font-semibold mt-1 mb-2 leading-snug text-white">{title}</h3>
          <p style="color: #777; font-size: 13px; line-height: 1.7;">{excerpt}</p>
          <div class="flex items-center justify-between mt-5">
            <span style="font-size: 12px; color: #555;">{date_display} · {read_time} min</span>
            <span class="blog-arrow">→</span>
          </div>
        </div>
      </a>"""


def homepage_card_html(entry, delay):
    slug = entry["slug"]
    title = entry["title"]
    category = entry["category"]
    excerpt = entry["excerpt"]
    read_time = entry["read_time"]
    date_display = format_date_display(entry["date"])

    return f"""      <a href="blog/{slug}.html" class="blog-card" data-aos="fade-up" data-aos-delay="{delay}">
        <div class="blog-thumb" style="background:none;padding:0;">
          <img src="blog/images/{slug}.svg" alt="" style="width:100%;height:100%;object-fit:cover;">
        </div>
        <div class="p-6">
          <span class="blog-tag">{category}</span>
          <h3 class="font-heading text-base font-semibold mt-3 mb-2 leading-snug text-white">{title}</h3>
          <p style="color: #B0B0B0; font-size: 13px; line-height: 1.7;">{excerpt}</p>
          <div class="flex items-center justify-between mt-5">
            <span style="font-size: 12px; color: #777;">{date_display} · {read_time} min read</span>
            <span class="blog-arrow">→</span>
          </div>
        </div>
      </a>"""


def _extract_post_meta(path):
    """Extract title, description and datePublished from a blog post HTML file."""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    title_m = re.search(r"<title>(.+?)</title>", html)
    title = title_m.group(1) if title_m else os.path.basename(path)
    title = re.sub(r"\s*[\u2014\u2013-]+\s*Stewart Masters\s*$", "", title).strip()
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    description = desc_m.group(1) if desc_m else ""
    date_m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})"', html)
    date_str = date_m.group(1) if date_m else None
    if not date_str:
        vis_m = re.search(r"(\d{1,2}\s+\w{3}\s+20\d{2})", html)
        if vis_m:
            try:
                d = datetime.datetime.strptime(vis_m.group(1), "%d %b %Y")
                date_str = d.strftime("%Y-%m-%d")
            except ValueError:
                pass
    return title, description, date_str or "2025-12-01"


def generate_feed():
    """Regenerate feed.xml from all published blog posts."""
    posts = []
    for fname in os.listdir(BLOG_DIR):
        if not fname.endswith(".html") or fname in BLOG_SKIP:
            continue
        slug = fname[:-5]
        path = os.path.join(BLOG_DIR, fname)
        title, description, date_str = _extract_post_meta(path)
        posts.append({"slug": slug, "title": title, "description": description, "date": date_str})

    posts.sort(key=lambda x: x["date"], reverse=True)
    if not posts:
        return

    latest_date = posts[0]["date"]

    def rfc822(date_str):
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return format_datetime(d)

    def escape_xml(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    items = ""
    for p in posts:
        url = f"https://stewartmasters.me/blog/{p['slug']}.html"
        items += f"""
  <item>
    <title>{escape_xml(p['title'])}</title>
    <link>{url}</link>
    <description>{escape_xml(p['description'])}</description>
    <pubDate>{rfc822(p['date'])}</pubDate>
    <guid isPermaLink="true">{url}</guid>
  </item>"""

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Stewart Masters</title>
    <link>https://stewartmasters.me</link>
    <description>Operator perspectives on AI adoption, digital operations, and product execution inside real businesses.</description>
    <language>en</language>
    <atom:link href="https://stewartmasters.me/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{rfc822(latest_date)}</lastBuildDate>
    <image>
      <url>https://stewartmasters.me/favicon-32x32.png</url>
      <title>Stewart Masters</title>
      <link>https://stewartmasters.me</link>
    </image>{items}
  </channel>
</rss>"""

    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"\u2713 Regenerated feed.xml ({len(posts)} posts)")


def main():
    # Use UTC date — GitHub Actions runs at 08:00 UTC
    today = datetime.date.today().isoformat()
    print(f"Running publish.py for date: {today}")

    schedule = load_schedule()

    # Sort by date
    schedule_sorted = sorted(schedule, key=lambda e: e["date"])

    # Find today's entry
    today_entry = next((e for e in schedule_sorted if e["date"] == today), None)
    if not today_entry:
        print(f"No post scheduled for {today}. Nothing to publish.")
        sys.exit(0)

    slug = today_entry["slug"]
    post_path = os.path.join(BLOG_DIR, f"{slug}.html")
    draft_path = os.path.join(DRAFTS_DIR, f"{slug}.html")

    # Move from drafts/ to blog/ if needed
    if not os.path.exists(post_path):
        if os.path.exists(draft_path):
            shutil.move(draft_path, post_path)
            print(f"Moved {slug}.html from drafts/ to blog/")
        else:
            print(f"ERROR: Post file not found in blog/ or blog/drafts/: {slug}.html")
            print("Add the post HTML to blog/drafts/ before its scheduled date.")
            sys.exit(1)
    elif not os.path.exists(draft_path):
        print(f"ERROR: {slug}.html is already published but has a new schedule.json entry for {today}.")
        print("This is a duplicate schedule entry. Remove the duplicate from schedule.json.")
        sys.exit(1)

    print(f"Publishing: {today_entry['title']}")

    # Find previous published entry (last entry with date < today that has an HTML file)
    prev_entry = None
    for e in reversed(schedule_sorted):
        if e["date"] < today:
            prev_path = os.path.join(BLOG_DIR, f"{e['slug']}.html")
            if os.path.exists(prev_path):
                prev_entry = e
                break

    # Read blog/index.html
    with open(BLOG_INDEX, "r", encoding="utf-8") as f:
        html = f.read()

    # Replace featured section
    new_featured = featured_html(today_entry)
    html = re.sub(
        r"<!-- FEATURED_START -->.*?<!-- FEATURED_END -->",
        f"<!-- FEATURED_START -->\n{new_featured}\n<!-- FEATURED_END -->",
        html,
        flags=re.DOTALL,
    )

    # Insert previous post as first grid card (it was featured, now moves to grid)
    if prev_entry:
        new_card = grid_card_html(prev_entry)
        html = html.replace(
            "<!-- GRID_START -->",
            f"<!-- GRID_START -->\n\n{new_card}\n",
            1,
        )

    # Write updated blog/index.html
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Updated blog/index.html")
    print(f"✓ Featured: {today_entry['title']}")
    if prev_entry:
        print(f"✓ Added to grid: {prev_entry['title']}")

    # Update homepage (index.html) — replace the 3 most-recent published posts
    published = [
        e for e in schedule_sorted
        if e["date"] <= today and os.path.exists(os.path.join(BLOG_DIR, f"{e['slug']}.html"))
    ]
    recent_three = list(reversed(published))[:3]

    if recent_three:
        delays = [0, 80, 160]
        cards = "\n".join(
            homepage_card_html(e, delays[i]) for i, e in enumerate(recent_three)
        )
        with open(HOMEPAGE, "r", encoding="utf-8") as f:
            hp = f.read()
        hp = re.sub(
            r"<!-- HOMEPAGE_POSTS_START -->.*?<!-- HOMEPAGE_POSTS_END -->",
            f"<!-- HOMEPAGE_POSTS_START -->\n{cards}\n<!-- HOMEPAGE_POSTS_END -->",
            hp,
            flags=re.DOTALL,
        )
        with open(HOMEPAGE, "w", encoding="utf-8") as f:
            f.write(hp)
        print(f"✓ Updated index.html homepage posts")

    # Regenerate RSS feed
    generate_feed()


if __name__ == "__main__":
    main()

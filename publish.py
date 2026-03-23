#!/usr/bin/env python3
"""
Daily post publisher for stewartmasters.me
Runs via GitHub Actions at 08:00 UTC (09:00 CET / 10:00 CEST)

Logic per run:
  1. Find today's scheduled post in schedule.json
  2. Move the post HTML from blog/drafts/ to blog/ (if not already there)
  3. Replace the featured section in blog/index.html with today's post
  4. Insert the previous featured post as a grid card at the top of the grid

Future posts are stored in blog/drafts/ so they are not publicly accessible
until their scheduled publish date.
"""

import json
import os
import re
import shutil
import sys
import datetime

SCHEDULE_FILE = "blog/schedule.json"
BLOG_INDEX = "blog/index.html"
BLOG_DIR = "blog"
DRAFTS_DIR = "blog/drafts"


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


if __name__ == "__main__":
    main()

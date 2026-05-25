# Create a new blog post

## 1. Write the post HTML
Create `blog/drafts/{slug}.html` following the existing post structure (copy an existing post for the template).

Apply all blog writing rules from CLAUDE.md:
- No banned phrases (no "delve into", "cutting-edge", "game-changing", etc.)
- Max 2 em dashes per article
- Voice: direct, specific, first-person, like Stewart talking to a senior exec at dinner
- Mixed sentence lengths, opinions stated as opinions, specific numbers

## 2. Schedule the post
Add an entry to `blog/schedule.json`:
```json
{ "date": "YYYY-MM-DD", "slug": "post-slug", "title": "Post Title" }
```

## 3. Rebuild CSS if needed
```bash
npm run build:css
```

## 4. Test locally
Open `blog/drafts/{slug}.html` in a browser to verify layout.

## 5. Commit the draft
```bash
git add blog/drafts/{slug}.html blog/schedule.json
git commit -m "Add draft: {post title}"
git pull --rebase && git push
```

The post will go live automatically on its scheduled date via GitHub Actions.

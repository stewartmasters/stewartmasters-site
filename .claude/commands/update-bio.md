# Update bio or homepage content

## 1. Edit index.html
Open `index.html` and find the section to update (bio, current role, links, logos).

Current role: CDO at Honest Greens, Barcelona.

## 2. Rebuild CSS if Tailwind classes changed
```bash
npm run build:css
```

## 3. Commit and push
```bash
git add index.html styles.css
git commit -m "Update bio: {describe change}"
git pull --rebase && git push
```

Netlify deploys automatically on push to main.

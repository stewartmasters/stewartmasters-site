# Add a speaking topic

## 1. Edit speaking-topics.json
Add the new topic object to `speaking-topics.json`.

## 2. Regenerate speaking pages
```bash
python3 generate_speaking.py
```

This regenerates both `speaking.html` (English) and `ponente.html` (Spanish).

## 3. Commit and push
```bash
git add speaking-topics.json speaking.html ponente.html
git commit -m "Add speaking topic: {topic name}"
git pull --rebase && git push
```

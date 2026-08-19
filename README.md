# Migration notes

This is a corrected skeleton for your project. It doesn't include your
`style.css` (I never saw its contents) — just copy your existing one into
`frontend/style.css`, it doesn't need any changes.

## 1. Clean up your existing repo

Since this is already on GitHub, `venv/` and `.env` may already be tracked.
From your **existing** repo root:

```bash
git rm -r --cached venv
git rm --cached backend/.env
```

Then copy the `.gitignore` from this skeleton into your repo root, commit:

```bash
git add .gitignore
git commit -m "Remove venv and .env from tracking, restructure project"
```

**If `.env` was ever pushed to GitHub, rotate your `GEMINI_API_KEY` in
Google AI Studio now.** Removing it from tracking doesn't erase it from
git history — anyone who cloned the repo already has the old key. Rotating
is the only real fix; rewriting history (`git filter-repo`) is optional
extra cleanup but doesn't help if the repo was ever public or cloned.

## 2. Replace your file layout with this one

Copy `backend/`, `frontend/`, `tests/`, `pytest.ini`, and `render.yaml`
from this skeleton into your repo, replacing the old `main.py`/`test.py`.
Keep your real `style.css` and put it in `frontend/`.

## 3. Local setup

```bash
cd backend
cp .env.example .env      # fill in your real GEMINI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

Visit `http://localhost:8000` — the frontend is served from the same app now.

Run tests from the repo root:

```bash
pip install -r backend/requirements.txt
pytest
```

## 4. Render setup

1. In the Render dashboard: **New > Blueprint**, point it at your repo.
   Render will read `render.yaml` and create the service automatically.
2. In the service's **Environment** tab, set `GEMINI_API_KEY` to your real
   key (this is why it's `sync: false` in render.yaml — it's never in git).
3. In **Settings > Deploy Hook**, copy the deploy hook URL.

## 5. GitHub Actions setup (the actual CI/CD gate)

1. In your GitHub repo: **Settings > Secrets and variables > Actions**,
   add a secret named `RENDER_DEPLOY_HOOK` with the URL from step 4.3 above.
2. Push to `main`. The workflow will:
   - Install deps and run `pytest`
   - Only if tests pass, call the Render deploy hook

`autoDeploy: false` in `render.yaml` means Render will **not** deploy on
every push by itself — only GitHub Actions triggers a deploy, and only
after tests pass. This is the actual CI/CD pipeline: broken code never
reaches Render.

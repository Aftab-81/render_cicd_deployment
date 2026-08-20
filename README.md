# Gemini API Backend — Render CI/CD Deployment

This document describes how this project is deployed to [Render](https://render.com) and how the GitHub Actions CI/CD pipeline is configured to automatically test and deploy on every push to `main`.

---

## 1. Project Overview

- **Backend:** FastAPI (`backend/app/main.py`), served with `uvicorn`
- **Frontend:** Static files served from the same service (`frontend/`)
- **Hosting:** Render Web Service
- **CI/CD:** GitHub Actions → Render Deploy Hook

### Key Endpoints

| Endpoint          | Method | Description                              |
|-------------------|--------|-------------------------------------------|
| `/api/health`      | GET    | Health check                              |
| `/api/summarize`   | POST   | Summarizes provided text via Gemini       |
| `/api/explain-image` | POST | Explains an uploaded image via Gemini    |
| `/api/chat`        | POST   | Simple QA chat endpoint                   |
| `/api/status`      | GET    | Confirms CI/CD pipeline is deploying correctly |

---

## 2. Render Setup

### 2.1 Create the Web Service

1. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**.
2. Connect your GitHub repository (`Aftab-81/render_cicd_deployment`).
3. Configure:
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.2 Environment Variables

Go to your service → **Environment** tab → add:

| Key             | Value                        |
|-----------------|-------------------------------|
| `GEMINI_API_KEY` | Your actual Gemini API key   |

### 2.3 Auto-Deploy Setting

Since deployments are triggered explicitly through GitHub Actions (see below), set:

- **Settings → Build → Auto-Deploy:** `Off`

This ensures deploys only happen **after tests pass** in CI, rather than on every raw push.

> If you'd rather let Render deploy on every push automatically, set Auto-Deploy to `On Commit` instead, and remove the `deploy` job from the GitHub Actions workflow (see 3.3) to avoid duplicate deploys.

### 2.4 Deploy Hook

1. Go to **Settings → Deploy → Deploy Hook**.
2. Click the eye icon to reveal the private URL and copy it.
3. This URL will be stored as a GitHub secret (see 3.2) and triggered by the CI/CD pipeline to start a new deploy.

---

## 3. GitHub Actions CI/CD Setup

### 3.1 Workflow File

Located at `.github/workflows/ci-cd.yml`. It has two jobs:

- **`test`** — installs dependencies and runs `pytest`
- **`deploy`** — runs only if `test` passes and the push is to `main`; triggers the Render deploy hook

```yaml
jobs:
  test:
    steps:
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        env:
          GEMINI_API_KEY: test-key-for-ci
        run: pytest

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render deploy
        run: curl -f "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

> **Note:** Render's deploy hook expects a `GET` request. Do **not** use `-X POST` — it will return a `405 Method Not Allowed` error.

### 3.2 Adding GitHub Secrets

1. Go to your repo on GitHub → **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. Add:

| Name                  | Value                                      |
|------------------------|---------------------------------------------|
| `RENDER_DEPLOY_HOOK`   | The deploy hook URL copied from Render (2.4) |
| `GEMINI_API_KEY`       | (Optional) Real Gemini key, if CI tests need it |

### 3.3 How the Pipeline Runs

1. Push a commit to `main`.
2. GitHub Actions runs the `test` job (installs deps, runs `pytest`).
3. If tests pass, the `deploy` job fires a `GET` request to the Render deploy hook.
4. Render pulls the latest commit, rebuilds, and deploys.

---

## 4. Verifying a Deployment

### 4.1 Check GitHub Actions

- Go to the **Actions** tab in the repo.
- Confirm both `test` and `deploy` jobs are green.

### 4.2 Check Render

1. Go to your service → **Events** tab.
2. Confirm a new deploy event appears with a timestamp matching the GitHub Actions run.
3. Click into the event to see the deployed commit SHA — compare it to `git log -1` on `main` to confirm it matches.
4. Check **Logs** for `Your service is live`.

### 4.3 Check the Live Endpoint

Once the deploy is live, hit the status endpoint to confirm the pipeline is working end-to-end:

```bash
curl https://<your-service>.onrender.com/api/status
```

Expected response:

```json
{"message": "CICD Pipeline is working Fine on it"}
```

---

## 5. Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/api/health` to confirm the app is running locally.

---

## 6. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `curl: (22) ... error: 405` in deploy job | Deploy hook called with `-X POST` | Remove `-X POST`; Render deploy hooks expect `GET` |
| New route returns 404 or serves static file | Route defined **after** `app.mount("/", StaticFiles(...))` | Move all `/api/...` routes above the `StaticFiles` mount |
| Deploy job doesn't run | Push wasn't to `main`, or `test` job failed | Check the `if` condition and confirm `test` passed |
| Secret not found in Action logs | Secret name mismatch | Ensure secret name in GitHub exactly matches `secrets.RENDER_DEPLOY_HOOK` in the yml |
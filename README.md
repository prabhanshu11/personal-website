# Personal Website

A minimal personal profile site using Python and FastHTML. Currently it serves a simple “Hello, World” page and is intended as a foundation to grow into a full portfolio/profile.

## Quick Start (local)

Recommended: use `uv` for Python and fish shell.

- Ensure uv is installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Create a project env and add the web dependency:
  - If the package is `python-fasthtml`: `uv add python-fasthtml`
  - If it’s published as `fasthtml`: `uv add fasthtml`
  - Tip: run `uv search fasthtml` to confirm the exact package name.
- Run the app: `uv run python app.py`
- Open: http://127.0.0.1:8000/

Fish venv fallback (if not using uv):

- `python -m venv .venv && source .venv/bin/activate.fish`
- `pip install python-fasthtml` (or `pip install fasthtml`)
- `python app.py`

## Project Status

- Routes: only `/` returning a static heading.
- No tests yet. Add `pytest` as the app grows.

## Next Steps

- Choose hosting:
  - Dynamic Python app: Render, Railway, Fly.io, or similar.
  - Pure static profile (no Python): GitHub Pages (repo `prabhanshu11.github.io`).
- Add a proper project layout (`src/`), templates/content, and basic tests.
- Set up dependency management with `uv` (`pyproject.toml`, `uv.lock`).

## Deploy Options

GitHub Pages (static only):

- If you want a static site, move content to static HTML/CSS/JS and push to a repo named `prabhanshu11.github.io`. Pages enables automatic HTTPS.

Render/Railway/Fly.io (runs Python server):

- Make sure dependencies are declared with `uv`.
- Typical start commands:
  - Using the built-in server: `uv run python app.py` (the `serve()` helper should bind to `$PORT`).
  - Or with Uvicorn (if needed): `uv run uvicorn app:app --host 0.0.0.0 --port $PORT`.
- Connect your GitHub repo, set the start command, and deploy. These providers auto‑provision TLS when you add a custom domain.

## SSL/HTTPS – How To Check

After deploying to a domain (example: `yourdomain.com`):

- Browser: visit `https://yourdomain.com` and check the lock icon; view the certificate details.
- CLI (headers): `curl -I https://yourdomain.com` (expect `HTTP/2 200` or a 3xx to your site).
- CLI (certificate):
  - `openssl s_client -connect yourdomain.com:443 -servername yourdomain.com -showcerts </dev/null | openssl x509 -noout -issuer -subject -dates`
- Online scanner: SSL Labs — https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

Notes for GitHub Pages + custom domain:

- Add your domain in repo Settings → Pages.
- Set DNS: `CNAME` to `prabhanshu11.github.io` (or `ALIAS/ANAME/A` per docs).
- Check “Enforce HTTPS” — it appears once the cert is ready (can take minutes to a few hours).

## GitHub Remote & Push

- Create a repo on GitHub (e.g., `personal-website`) under `prabhanshu11` and share the URL.
- Then run:
  - `git remote add origin <YOUR_URL>`
  - `git push -u origin main`

If you want this to be a GitHub Pages user site instead, create `prabhanshu11.github.io` and we can convert this to a static site.

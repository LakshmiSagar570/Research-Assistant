# Deployment Guide — Supabase + Vercel

This deploys:
- **Database** → Supabase (Postgres)
- **Backend** → Vercel (Python serverless function, via Mangum adapter)
- **Frontend** → Vercel (static React build)

Two separate Vercel projects (backend and frontend) — this is normal and expected,
not a mistake. They get two different `.vercel.app` URLs, and the frontend is
configured to call the backend URL.

---

## 1. Supabase: get your connection string

1. In your Supabase project: **Project Settings → Database → Connection string**.
2. Choose **Connection pooling**, mode **Transaction**. Copy the URI — looks like:
   ```
   postgresql://postgres.xxxxxxxx:[YOUR-PASSWORD]@aws-0-xx-xxxx-1.pooler.supabase.com:6543/postgres
   ```
   (Use the **pooled** connection, not the direct one — serverless functions open
   many short-lived connections per minute, and Supabase's pgbouncer pooler is
   built for exactly that; a direct connection will exhaust its connection limit
   quickly under real traffic.)
3. Replace `[YOUR-PASSWORD]` with your actual database password.
4. Keep this string somewhere safe — you'll paste it into Vercel as `DATABASE_URL`
   in step 2. **Never commit it to git.**

Tables are created automatically on first backend startup (`init_db()` in
`main.py`) — you don't need to run any SQL manually in Supabase.

---

## 2. Backend → Vercel

From the `backend/` folder:

```powershell
cd backend
npx vercel login
npx vercel
```

Follow the prompts (link to a new project, accept defaults). This does a first
deploy, but it will **fail to actually work** until you set environment variables
— that's expected, do that next.

### Set environment variables

In the Vercel dashboard for this backend project → **Settings → Environment Variables**,
add (use `.env.production.example` in this repo as your checklist):

| Key | Value |
|---|---|
| `DATABASE_URL` | the Supabase pooled connection string from step 1 |
| `JWT_SECRET` | a long random string — generate with `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ENV` | `production` |
| `SEED_DEMO_USER` | `false` |
| `CORS_ORIGINS` | `["https://YOUR-FRONTEND-PROJECT.vercel.app"]` — you'll get this URL in step 3, come back and update this after |

Redeploy after setting variables:
```powershell
npx vercel --prod
```

Note your backend's production URL, e.g. `https://ai-research-assistant-backend.vercel.app`.
Test it: open `https://YOUR-BACKEND-URL.vercel.app/health` in a browser — should return
`{"status":"ok"}`.

---

## 3. Frontend → Vercel

From the `frontend/` folder, first point it at your live backend:

Edit `frontend/.env.production` (create this file):
```
VITE_API_URL=https://YOUR-BACKEND-URL.vercel.app
```

Then deploy:
```powershell
cd frontend
npx vercel login
npx vercel --prod
```

Note the frontend's URL, e.g. `https://ai-research-assistant.vercel.app`.

---

## 4. Close the loop: update backend CORS

Go back to the **backend** Vercel project's environment variables and update
`CORS_ORIGINS` to the real frontend URL from step 3:
```
["https://ai-research-assistant.vercel.app"]
```
Redeploy the backend once more:
```powershell
cd backend
npx vercel --prod
```

---

## 5. Create your real account

Since `SEED_DEMO_USER=false` in production, there is no demo login on the live
site (intentional — you don't want a publicly known password on a real
deployment). Register your own account via the app's UI, or directly:

```powershell
curl -X POST https://YOUR-BACKEND-URL.vercel.app/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Your Name\",\"email\":\"you@college.edu\",\"password\":\"a-strong-password\",\"role\":\"faculty\"}'
```

---

## 6. Verify end-to-end on the live URLs

Open your frontend URL, register/log in, and walk through: search → summarize →
save reference → generate review → export docx → approve. Same checklist as
local testing, just against the live deployment.

## Troubleshooting

**CORS errors in the browser console** — `CORS_ORIGINS` on the backend doesn't
exactly match your frontend's URL (including `https://`, no trailing slash).
Update and redeploy the backend.

**401 on every request after login** — check `JWT_SECRET` is actually set in
Vercel's env vars for the backend project (not just typed locally) and that
you redeployed after setting it.

**"relation does not exist" / DB errors** — the backend hasn't successfully
connected to Supabase yet, usually a wrong `DATABASE_URL` (check the password
is URL-encoded if it contains special characters) or you're using the direct
connection string instead of the pooled one.

**Review generation works but docx download fails** — this uses an in-memory
single-request flow specifically so it works on serverless (see
`services/review_export.py` for why); if this breaks, check the Vercel function
logs (`npx vercel logs`) for the actual Python traceback.

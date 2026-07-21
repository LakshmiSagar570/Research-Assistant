"""
Vercel serverless entrypoint.

Vercel's Python runtime expects a WSGI/ASGI-compatible handler at a
known path. Mangum adapts our ASGI FastAPI app to the AWS
Lambda-style event format Vercel's Python functions use under the
hood. This file is the target referenced in vercel.json - it does not
run locally; local dev still uses `uvicorn app.main:app --reload`.
"""
from mangum import Mangum
from app.main import app

# lifespan="auto" ensures FastAPI's startup event (which calls init_db() to
# create tables) actually runs on cold start. Mangum defaults to "off" for
# lifespan handling since not all serverless platforms support it the same
# way; Vercel's Python runtime does, so we opt in explicitly rather than
# rely on an implicit default that could silently skip table creation.
handler = Mangum(app, lifespan="auto")

"""P15/16 live-stack launcher (test only, deleted after validation)."""
import os

os.environ["MONGODB_URL"] = "mongodb://127.0.0.1:27099/tax_shield_live"
os.environ["MONGODB_DB_NAME"] = "tax_shield_live"
os.environ["SECRET_KEY"] = "p16-live-test-only-not-a-secret-abcdef1234567890"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["ADMIN_EMAILS"] = "ca.admin@example.com"

import uvicorn

uvicorn.run("app.main:app", host="127.0.0.1", port=8000, workers=1)

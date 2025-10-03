import json, time, os, datetime as dt
import pytest
from httpx import AsyncClient
from nimbus.main import app
from tests.testutils import hmac_sig, ensure_project, count_events

@pytest.mark.asyncio
async def test_ingest_event_success():
    pid = await ensure_project()
    body = {
        "project_id": pid,
        "events": [
            {"name": "page_view", "ts": dt.datetime.now(dt.timezone.utc).isoformat(), "props": {"k": "v"}}
        ],
    }
    body_s = json.dumps(body, separators=(",", ":"))
    ts = int(time.time())
    key_id = os.getenv("INGEST_API_KEY_ID", "local-key-id")
    secret = os.getenv("INGEST_API_KEY_SECRET", "local-super-secret")
    sig = hmac_sig(ts, "POST", "/v1/events", body_s, secret)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post(
            "/v1/events",
            headers={
                "content-type": "application/json",
                "X-Api-Key-Id": key_id,
                "X-Api-Timestamp": str(ts),
                "X-Api-Signature": sig,
            },
            content=body_s,
        )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["count"] == 1
    assert await count_events(pid) >= 1

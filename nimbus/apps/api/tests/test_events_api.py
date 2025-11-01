import json, time, os, datetime as dt
import pytest
from httpx import AsyncClient, ASGITransport
from nimbus.main import app
from tests.testutils import hmac_sig, ensure_project, count_events

@pytest.mark.asyncio
async def test_ingest_event_success():
    pid, key_id = await ensure_project()
    body = {
        "project_id": pid,
        "events": [
            {"name": "page_view", "ts": dt.datetime.now(dt.timezone.utc).isoformat(), "props": {"k": "v"}}
        ],
    }
    body_s = json.dumps(body, separators=(",", ":"))
    ts = int(time.time())
    secret = os.getenv("INGEST_API_KEY_SECRET", "local-super-secret")
    sig = hmac_sig(ts, "POST", "/v1/events", body_s, secret)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
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
    assert data["accepted"] == 1
    assert data["rejected"] == 0
    assert await count_events(pid) >= 1

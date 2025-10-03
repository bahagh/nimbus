import json, time, os, datetime as dt
import pytest
from httpx import AsyncClient
from nimbus.main import app
from nimbus.security.auth import create_token
from tests.testutils import hmac_sig, ensure_project

@pytest.mark.asyncio
async def test_metrics_flow_after_ingest():
    pid = await ensure_project()
    # ingest a few events across the last couple minutes
    now = dt.datetime.now(dt.timezone.utc)
    events = [
        {"name": "pv", "ts": (now - dt.timedelta(minutes=1)).isoformat(), "props": {}},
        {"name": "pv", "ts": now.isoformat(), "props": {}},
        {"name": "pv", "ts": now.isoformat(), "props": {}},
    ]
    body = {"project_id": pid, "events": events}
    body_s = json.dumps(body, separators=(",", ":"))
    ts = int(time.time())
    key_id = os.getenv("INGEST_API_KEY_ID", "local-key-id")
    secret = os.getenv("INGEST_API_KEY_SECRET", "local-super-secret")
    sig = hmac_sig(ts, "POST", "/v1/events", body_s, secret)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r1 = await ac.post(
            "/v1/events",
            headers={
                "content-type": "application/json",
                "X-Api-Key-Id": key_id,
                "X-Api-Timestamp": str(ts),
                "X-Api-Signature": sig,
            },
            content=body_s,
        )
        assert r1.status_code == 200

        # auth for metrics
        token = create_token("user@example.com", 60)
        r2 = await ac.get(
            f"/v1/metrics?project_id={pid}&time_range=2 minutes&window=minute",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert r2.status_code == 200
    payload = r2.json()
    assert isinstance(payload, list)
    assert all("ts" in p and "value" in p for p in payload)

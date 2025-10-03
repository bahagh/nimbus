from nimbus_worker.config import settings

def test_settings_loads():
    assert settings.database_url and settings.redis_url

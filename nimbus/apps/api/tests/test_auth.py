from nimbus.security.auth import create_token, decode_token


def test_token_cycle():
    token = create_token("user@example.com", 60)
    payload = decode_token(token)
    assert payload and payload["sub"] == "user@example.com"

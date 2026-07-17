import importlib


def test_config_uses_grok_env(monkeypatch):
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.setenv("GROK_API_KEY", "grok-test-key")

    import config

    reloaded = importlib.reload(config)
    assert reloaded.GROK_API_KEY == "grok-test-key"


def test_build_grok_payload_includes_image_and_prompt(tmp_path):
    from ai_service import build_grok_payload

    image_path = tmp_path / "bill.jpg"
    image_path.write_bytes(b"fake-image-bytes")

    payload = build_grok_payload("Extract the bill details", image_path=str(image_path))

    assert payload["model"] == "grok-2-vision-1212"
    assert payload["messages"][0]["role"] == "user"

    content = payload["messages"][0]["content"]
    assert any(item.get("type") == "text" for item in content)
    assert any(item.get("type") == "image_url" for item in content)

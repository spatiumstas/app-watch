from backend.notifier import NotificationHandler


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"ok": True}


def test_telegram_custom_emoji_is_sent_inline_as_html(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
        return FakeResponse()

    monkeypatch.setattr("backend.notifier.requests.post", fake_post)
    notifier = NotificationHandler()
    content = '<tg-emoji emoji-id="5368324170671202286">📲</tg-emoji> **Update** App'

    success, error = notifier.send_notification(
        {"type": "telegram", "bot_token": "token", "chat_id": "-1001234567890_7"},
        "App",
        "1.0.0",
        "",
        content,
    )

    assert success is True
    assert error is None
    _, payload, _ = calls[0]
    assert payload["parse_mode"] == "HTML"
    assert payload["message_thread_id"] == 7
    assert payload["text"] == '<tg-emoji emoji-id="5368324170671202286">📲</tg-emoji> <b>Update</b> App'


def test_custom_emoji_tag_uses_fallback_outside_telegram(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append(json)
        return FakeResponse()

    monkeypatch.setattr("backend.notifier.requests.post", fake_post)
    notifier = NotificationHandler()

    success, error = notifier.send_notification(
        {"type": "discord", "webhook_url": "https://discord.com/api/webhooks/id/token"},
        "App",
        "1.0.0",
        "",
        '<tg-emoji emoji-id="5368324170671202286">📲</tg-emoji> Update',
    )

    assert success is True
    assert error is None
    assert calls[0]["content"] == "📲 Update"

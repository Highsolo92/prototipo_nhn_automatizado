import os, httpx

SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def notify(text: str):
    try:
        if SLACK_URL:
            httpx.post(SLACK_URL, json={"text": text}, timeout=10)
        if DISCORD_URL:
            httpx.post(DISCORD_URL, json={"content": text}, timeout=10)
    except Exception:
        pass

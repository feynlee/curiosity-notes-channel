#!/usr/bin/env python3
"""One-time TikTok login for the Curiosity Notes Publisher.

Prints a refresh token for the cloud environment. Nothing is written to disk.
Use the Sandbox client key and secret while the app is unreviewed.
"""
import getpass
import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
REDIRECT_URI = "https://feynlee.github.io/curiosity-notes-channel/app/callback"
SCOPES = "user.info.basic,video.upload"


def authorize_url(client_key, state):
    query = urllib.parse.urlencode({
        "client_key": client_key,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "disable_auto_auth": 1,
    })
    return f"{AUTHORIZE_URL}?{query}"


def read_answer(text, state):
    answer = json.loads(text)
    if answer.get("state") != state:
        raise SystemExit("The sign-in state does not match. Start again.")
    return answer["code"]


def exchange_code(client_key, client_secret, code):
    body = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }).encode()
    request = urllib.request.Request(
        TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        return json.load(error)


def main():
    client_key = input("Client key: ").strip()
    client_secret = getpass.getpass("Client secret (hidden): ").strip()
    state = secrets.token_urlsafe(24)
    url = authorize_url(client_key, state)
    print(f"\nOpen this page and approve with the Curiosity Notes account:\n{url}\n")
    webbrowser.open(url)
    answer = input("Paste the text from the sign-in page: ")
    tokens = exchange_code(client_key, client_secret, read_answer(answer, state))
    if "refresh_token" not in tokens:
        raise SystemExit(f"TikTok refused the login: {tokens.get('error')}: {tokens.get('error_description')}")
    print(f"\nGranted scopes: {tokens.get('scope')}")
    print(f"Refresh token lasts {tokens.get('refresh_expires_in', 0) // 86400} days.")
    print(f"TIKTOK_REFRESH_TOKEN={tokens['refresh_token']}")


if __name__ == "__main__":
    main()

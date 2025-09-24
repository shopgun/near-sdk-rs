#!/usr/bin/env python3
# check_github_token_logs.py
# Safe test script to show in logs if GITHUB_TOKEN is present
# Does NOT modify environment variables

import os
import hashlib
import urllib.request
import urllib.error

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("TOKEN_MISSING")
        return

    print("TOKEN_PRESENT")
    print(f"TOKEN_LEN={len(token)}")
    print(f"TOKEN_SHA256={sha256_hex(token)}")

    # Optional: check if token can access the repo API
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print("NO_GITHUB_REPOSITORY_IN_ENV")
        return

    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "User-Agent": "github-token-logger"
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"TOKEN_API_STATUS={resp.getcode()}")
            scopes = resp.headers.get("X-Oauth-Scopes") or ""
            if scopes:
                print(f"TOKEN_SCOPES={scopes}")
    except urllib.error.HTTPError as e:
        print(f"TOKEN_API_STATUS={e.code}")
    except Exception as e:
        print(f"TOKEN_API_ERROR={type(e).__name__}: {e}")

if __name__ == "__main__":
    main()

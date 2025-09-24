#!/usr/bin/env python3
# check_token.py
# Safe token presence + API test for use in CI runs triggered by untrusted PRs.
# NEVER prints the token itself.

import os
import sys
import hashlib
import urllib.request
import urllib.error

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def print_and_exit(msg: str, code: int = 0):
    print(msg, flush=True)
    sys.exit(code)

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print_and_exit("TOKEN_MISSING")

    # Safe metadata only
    token_len = len(token)
    token_hash = sha256_hex(token)  # safe one-way fingerprint

    print(f"TOKEN_PRESENT")
    print(f"TOKEN_LEN={token_len}")
    print(f"TOKEN_SHA256={token_hash}")

    # Optional: try a harmless API call to check token validity.
    repo = os.environ.get("GITHUB_REPOSITORY")  # e.g. "owner/repo"
    if not repo:
        print_and_exit("NO_GITHUB_REPOSITORY_IN_ENV - skipped API test")

    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "User-Agent": "token-checker-script"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            # Try to show scopes if present (useful to know permission level)
            scopes = resp.headers.get("X-Oauth-Scopes") or resp.headers.get("X-OAuth-Scopes") or ""
            print(f"TOKEN_API_STATUS={status}")
            if scopes:
                # Print scopes but redact long lists if necessary
                print(f"TOKEN_SCOPES={scopes}")
            # success
            sys.exit(0)
    except urllib.error.HTTPError as e:
        # 401/403 indicate token missing/insufficient or blocked
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        print(f"TOKEN_API_STATUS={e.code}")
        # keep body short/partial to avoid noisy logs
        excerpt = (body[:300] + "...") if len(body) > 300 else body
        if excerpt:
            print(f"TOKEN_API_BODY_EXCERPT={excerpt}")
        sys.exit(0)
    except Exception as e:
        # network problems, DNS, blocked egress, etc.
        print(f"TOKEN_API_ERROR={type(e).__name__}: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()

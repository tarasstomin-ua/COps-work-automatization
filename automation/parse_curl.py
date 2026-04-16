#!/usr/bin/env python3
"""
Parse a cURL command (from browser DevTools) and extract cookies
as a base64-encoded JSON string ready to use as BOLT_COOKIES secret.

Usage:
  1. Open admin-panel.bolt.eu in your browser
  2. F12 → Network → any request → Right-click → Copy as cURL
  3. Run: python parse_curl.py
  4. Paste the cURL command and press Enter twice
  5. Copy the output and set it as the BOLT_COOKIES secret in GitHub
"""

import base64
import json
import re
import sys


def parse_curl(curl_text: str) -> list[dict]:
    cookies = []
    cookie_headers = re.findall(
        r"-H\s+['\"]cookie:\s*([^'\"]+)['\"]",
        curl_text,
        re.IGNORECASE,
    )
    for header in cookie_headers:
        pairs = header.split(";")
        for pair in pairs:
            pair = pair.strip()
            if "=" in pair:
                name, _, value = pair.partition("=")
                cookies.append({
                    "name": name.strip(),
                    "value": value.strip(),
                    "domain": ".bolt.eu",
                    "path": "/",
                })
    return cookies


def main():
    print("Paste your cURL command below (press Enter twice when done):")
    lines = []
    empty = 0
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            empty += 1
            if empty >= 1 and lines:
                break
        else:
            empty = 0
            lines.append(stripped)

    curl_text = " ".join(lines)
    if not curl_text:
        sys.exit("No input provided")

    cookies = parse_curl(curl_text)
    if not cookies:
        sys.exit("No cookies found in the cURL command. Make sure you copied the full cURL.")

    print(f"\nFound {len(cookies)} cookies.")
    b64 = base64.b64encode(json.dumps(cookies).encode()).decode()
    print("\n=== BOLT_COOKIES value (copy everything below) ===\n")
    print(b64)
    print("\n=== END ===")
    print("\nSet this as a GitHub Secret:")
    print("  1. Go to https://github.com/tarasstomin-ua/COps-work-automatization/settings/secrets/actions")
    print("  2. Click 'New repository secret'")
    print("  3. Name: BOLT_COOKIES")
    print("  4. Value: paste the string above")
    print("  5. Click 'Add secret'")


if __name__ == "__main__":
    main()

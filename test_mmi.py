#!/usr/bin/env python3
"""
test_mmi.py — MapmyIndia OAuth2 + Reverse Geocode Validation
=============================================================
CausaFlow AI  ·  Gridlock 2.0 Hackathon  ·  Data‑Engineering (R1)

Purpose
-------
Validate end‑to‑end connectivity with MapmyIndia (Mappls) APIs:
  1. Obtain an OAuth 2.0 access token via client_credentials grant.
  2. Call the reverse‑geocode endpoint for a known location
     (Silk Board Junction, Bengaluru — 12.9343, 77.6133).
  3. Print HTTP status and formatted_address from the first result.

Exit codes
----------
  0  — success (token obtained AND reverse‑geocode returned a result)
  1  — any failure (details printed to stderr)
"""

import sys
import requests

# ── MapmyIndia OAuth 2.0 credentials ─────────────────────────────────────────
CLIENT_ID = (
    "96dHZVzsAuvKpFOIkUIT40J0n4gH6i6xy-HnmGr-XhR1zJ5QRnUu"
    "-FNqWHvq1vYYRkS17-pzeSBlJ1J9bb5x96WpjDMHtYpa"
)
CLIENT_SECRET = (
    "lrFxI-iSEg_UKwlZtW_vUHLVaAo2F7EZYBw7PJvrS8mfjJQ6XAmlwomTK"
    "_OTOW08LE_leYk6k8mG60tSxAW5zNEKSK6EzmCe90t2PjNuJKU="
)
TOKEN_URL = "https://outpost.mapmyindia.com/api/security/oauth/token"

# ── Test coordinates: Silk Board Junction, Bengaluru ──────────────────────────
TEST_LAT = 12.9343
TEST_LNG = 77.6133
REVERSE_GEOCODE_URL = "https://apis.mapmyindia.com/advancedmaps/v1/{token}/rev_geocode"


def get_access_token() -> str:
    """
    Obtain an OAuth 2.0 access token from the Mappls token endpoint
    using the client_credentials grant type.

    Returns
    -------
    str
        The bearer access token.

    Raises
    ------
    RuntimeError
        If the token request fails or the response is malformed.
    """
    print("[1/2] Requesting OAuth access token …")
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    resp = requests.post(TOKEN_URL, data=payload, timeout=15)

    print(f"      Token endpoint status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"      ✗ FAILED — full response:\n{resp.text}", file=sys.stderr)
        raise RuntimeError(f"Token request returned HTTP {resp.status_code}")

    body = resp.json()
    token = body.get("access_token")
    if not token:
        print(f"      ✗ No access_token in response:\n{body}", file=sys.stderr)
        raise RuntimeError("access_token missing from token response")

    expires_in = body.get("expires_in", "?")
    token_type = body.get("token_type", "?")
    print(f"      ✓ Token obtained  (type={token_type}, expires_in={expires_in}s)")
    print(f"      Token preview: {token[:20]}…{token[-10:]}")
    return token


def reverse_geocode(token: str, lat: float, lng: float) -> dict:
    """
    Call Mappls reverse‑geocode for a (lat, lng) pair.

    Parameters
    ----------
    token : str
        Valid Mappls OAuth bearer token.
    lat, lng : float
        WGS‑84 coordinates.

    Returns
    -------
    dict
        The full JSON response body.

    Raises
    ------
    RuntimeError
        If the HTTP call fails.
    """
    print(f"\n[2/2] Reverse geocoding ({lat}, {lng}) …")

    # Mappls rev_geocode accepts the token in the URL path
    url = REVERSE_GEOCODE_URL.format(token=token)
    params = {"lat": lat, "lng": lng}
    resp = requests.get(url, params=params, timeout=15)

    print(f"      Rev‑geocode status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"      ✗ FAILED — full response:\n{resp.text}", file=sys.stderr)
        raise RuntimeError(f"Reverse geocode returned HTTP {resp.status_code}")

    return resp.json()


def main() -> None:
    """Run the end‑to‑end test."""
    print("=" * 65)
    print("  CausaFlow AI — MapmyIndia API Connectivity Test")
    print("=" * 65)

    try:
        # Step 1: OAuth token
        token = get_access_token()

        # Step 2: Reverse geocode
        data = reverse_geocode(token, TEST_LAT, TEST_LNG)

        # Extract formatted_address from first result
        results = data.get("results", [])
        if results:
            address = results[0].get("formatted_address", "(no formatted_address)")
            print(f"\n  ✓ Formatted address: {address}")
        else:
            # Some Mappls endpoints return flat JSON instead of a results array
            address = data.get("formatted_address", None)
            if address:
                print(f"\n  ✓ Formatted address: {address}")
            else:
                print(f"\n  ⚠ No 'results' array — full response:\n{data}")

        print("\n" + "=" * 65)
        print("  TEST PASSED ✓")
        print("=" * 65)

    except Exception as exc:
        print(f"\n  ✗ TEST FAILED: {exc}", file=sys.stderr)
        print("=" * 65, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Inspect and optionally attach an App Store Connect build to a version."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import jwt


API_BASE = "https://api.appstoreconnect.apple.com/v1"


class AppStoreConnectError(RuntimeError):
    pass


class AppStoreConnectClient:
    def __init__(self, issuer_id: str, key_id: str, private_key: str) -> None:
        now = int(time.time())
        self.token = jwt.encode(
            {
                "iss": issuer_id,
                "iat": now,
                "exp": now + 10 * 60,
                "aud": "appstoreconnect-v1",
            },
            private_key,
            algorithm="ES256",
            headers={"kid": key_id, "typ": "JWT"},
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> dict[str, Any] | None:
        url = f"{API_BASE}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
                return json.loads(payload) if payload else None
        except urllib.error.HTTPError as error:
            if allow_not_found and error.code == 404:
                return None
            raw = error.read().decode("utf-8", errors="replace")
            detail = f"HTTP {error.code}"
            try:
                errors = json.loads(raw).get("errors", [])
                messages = [
                    ": ".join(
                        part
                        for part in (item.get("title"), item.get("detail"))
                        if part
                    )
                    for item in errors
                ]
                if messages:
                    detail = f"{detail}: {'; '.join(messages)}"
            except (json.JSONDecodeError, AttributeError):
                pass
            raise AppStoreConnectError(detail) from error
        except urllib.error.URLError as error:
            raise AppStoreConnectError(f"Network error: {error.reason}") from error


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise AppStoreConnectError(f"Missing environment variable: {name}")
    return value


def one_resource(payload: dict[str, Any] | None, label: str) -> dict[str, Any]:
    resources = [] if payload is None else payload.get("data", [])
    if not resources:
        raise AppStoreConnectError(f"No {label} found")
    if len(resources) > 1:
        raise AppStoreConnectError(f"More than one {label} matched")
    return resources[0]


def find_release(
    client: AppStoreConnectClient,
    bundle_id: str,
    version_string: str,
    build_number: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    app = one_resource(
        client.request(
            "GET",
            "/apps",
            params={"filter[bundleId]": bundle_id, "limit": "2"},
        ),
        f"app for bundle ID {bundle_id}",
    )

    version = one_resource(
        client.request(
            "GET",
            f"/apps/{app['id']}/appStoreVersions",
            params={
                "filter[platform]": "IOS",
                "filter[versionString]": version_string,
                "limit": "2",
            },
        ),
        f"iOS App Store version {version_string}",
    )

    builds_payload = client.request(
        "GET",
        "/builds",
        params={
            "filter[app]": app["id"],
            "filter[version]": build_number,
            "sort": "-uploadedDate",
            "limit": "2",
            "fields[builds]": (
                "version,uploadedDate,processingState,expired,"
                "usesNonExemptEncryption,buildAudienceType"
            ),
        },
    )
    builds = [] if builds_payload is None else builds_payload.get("data", [])
    if not builds:
        raise AppStoreConnectError(f"No build {build_number} found")
    build = builds[0]
    return app, version, build


def attached_build_id(
    client: AppStoreConnectClient, version_id: str
) -> str | None:
    payload = client.request(
        "GET",
        f"/appStoreVersions/{version_id}/relationships/build",
        allow_not_found=True,
    )
    if not payload:
        return None
    relationship = payload.get("data")
    return relationship.get("id") if isinstance(relationship, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("status", "attach"), default="status")
    parser.add_argument("--bundle-id", default="app.mingpattern.life")
    parser.add_argument("--version", default="1.0")
    parser.add_argument("--build", default="2")
    args = parser.parse_args()

    private_key = Path(require_env("APP_STORE_CONNECT_API_KEY_PATH")).read_text(
        encoding="utf-8"
    )
    client = AppStoreConnectClient(
        require_env("APP_STORE_CONNECT_ISSUER_ID"),
        require_env("APP_STORE_CONNECT_API_KEY_ID"),
        private_key,
    )

    app, version, build = find_release(
        client, args.bundle_id, args.version, args.build
    )
    build_attributes = build.get("attributes", {})
    version_attributes = version.get("attributes", {})
    current_build_id = attached_build_id(client, version["id"])

    print(f"App: {app.get('attributes', {}).get('name', args.bundle_id)}")
    print(
        "Version: "
        f"{version_attributes.get('versionString', args.version)} "
        f"({version_attributes.get('appStoreState', 'UNKNOWN')})"
    )
    print(
        "Build: "
        f"{build_attributes.get('version', args.build)} "
        f"({build_attributes.get('processingState', 'UNKNOWN')})"
    )
    print(f"Uploaded: {build_attributes.get('uploadedDate', 'UNKNOWN')}")
    print(
        "Export compliance answered: "
        f"{build_attributes.get('usesNonExemptEncryption') is not None}"
    )
    print(f"Already attached: {current_build_id == build['id']}")

    if args.action == "status":
        return 0

    if build_attributes.get("processingState") != "VALID":
        raise AppStoreConnectError(
            "Build cannot be attached until processingState is VALID"
        )
    if current_build_id == build["id"]:
        print("No change needed; build is already attached.")
        return 0
    if current_build_id:
        raise AppStoreConnectError(
            "The App Store version already has a different build attached"
        )

    client.request(
        "PATCH",
        f"/appStoreVersions/{version['id']}/relationships/build",
        body={"data": {"type": "builds", "id": build["id"]}},
    )
    if attached_build_id(client, version["id"]) != build["id"]:
        raise AppStoreConnectError("Build attachment could not be verified")
    print(f"Attached build {args.build} to iOS version {args.version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AppStoreConnectError, OSError) as error:
        print(f"App Store Connect release check failed: {error}", file=sys.stderr)
        raise SystemExit(1)

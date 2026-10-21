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


def build_number(client: AppStoreConnectClient, build_id: str | None) -> str | None:
    if not build_id:
        return None
    payload = client.request(
        "GET",
        f"/builds/{build_id}",
        params={"fields[builds]": "version"},
    )
    if not payload or not isinstance(payload.get("data"), dict):
        return None
    return payload["data"].get("attributes", {}).get("version")


def resources(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not payload or not isinstance(payload.get("data"), list):
        return []
    return payload["data"]


def relationship_id(resource: dict[str, Any], name: str) -> str | None:
    relationship = resource.get("relationships", {}).get(name, {}).get("data")
    return relationship.get("id") if isinstance(relationship, dict) else None


def review_submission_items(
    client: AppStoreConnectClient, submission_id: str
) -> list[dict[str, Any]]:
    payload = client.request(
        "GET",
        f"/reviewSubmissions/{submission_id}/items",
        params={
            "include": "appStoreVersion",
            "fields[reviewSubmissionItems]": "state,appStoreVersion",
            "limit": "200",
        },
    )
    return resources(payload)


def find_or_create_review_submission(
    client: AppStoreConnectClient,
    app_id: str,
    version_id: str,
) -> tuple[dict[str, Any], bool]:
    payload = client.request(
        "GET",
        f"/apps/{app_id}/reviewSubmissions",
        params={
            "filter[platform]": "IOS",
            "fields[reviewSubmissions]": "platform,state,submittedDate",
            "limit": "200",
        },
    )
    ready_submission: dict[str, Any] | None = None
    for submission in resources(payload):
        state = submission.get("attributes", {}).get("state")
        if state not in (
            "READY_FOR_REVIEW",
            "WAITING_FOR_REVIEW",
            "IN_REVIEW",
            "UNRESOLVED_ISSUES",
        ):
            continue
        items = review_submission_items(client, submission["id"])
        if any(
            relationship_id(item, "appStoreVersion") == version_id for item in items
        ):
            return submission, True
        if state == "READY_FOR_REVIEW" and ready_submission is None:
            ready_submission = submission

    if ready_submission is not None:
        return ready_submission, False

    created = client.request(
        "POST",
        "/reviewSubmissions",
        body={
            "data": {
                "type": "reviewSubmissions",
                "attributes": {"platform": "IOS"},
                "relationships": {
                    "app": {"data": {"type": "apps", "id": app_id}}
                },
            }
        },
    )
    if not created or not isinstance(created.get("data"), dict):
        raise AppStoreConnectError("Review submission was not created")
    return created["data"], False


def print_preflight(
    client: AppStoreConnectClient,
    app: dict[str, Any],
    version: dict[str, Any],
) -> None:
    app_attributes = app.get("attributes", {})
    version_attributes = version.get("attributes", {})
    print("\nPreflight metadata")
    print(f"Primary locale: {app_attributes.get('primaryLocale', 'UNKNOWN')}")
    print(
        "Content rights answered: "
        f"{bool(app_attributes.get('contentRightsDeclaration'))}"
    )
    print(f"Copyright present: {bool(version_attributes.get('copyright'))}")
    print(f"Release type: {version_attributes.get('releaseType', 'UNKNOWN')}")
    print(f"Uses IDFA: {version_attributes.get('usesIdfa', 'UNKNOWN')}")

    review_payload = client.request(
        "GET",
        f"/appStoreVersions/{version['id']}/appStoreReviewDetail",
        allow_not_found=True,
    )
    review = review_payload.get("data") if review_payload else None
    review_attributes = review.get("attributes", {}) if isinstance(review, dict) else {}
    contact_complete = all(
        review_attributes.get(field)
        for field in (
            "contactFirstName",
            "contactLastName",
            "contactPhone",
            "contactEmail",
        )
    )
    print(f"Review contact complete: {contact_complete}")
    print(
        "Demo account required: "
        f"{review_attributes.get('demoAccountRequired', 'UNKNOWN')}"
    )
    print(f"Review notes present: {bool(review_attributes.get('notes'))}")

    localization_payload = client.request(
        "GET",
        f"/appStoreVersions/{version['id']}/appStoreVersionLocalizations",
        params={"limit": "50"},
    )
    localizations = resources(localization_payload)
    print(f"Version localizations: {len(localizations)}")
    for localization in localizations:
        attributes = localization.get("attributes", {})
        locale = attributes.get("locale", "UNKNOWN")
        print(
            f"Localization {locale}: "
            f"description={bool(attributes.get('description'))}, "
            f"keywords={bool(attributes.get('keywords'))}, "
            f"support_url={bool(attributes.get('supportUrl'))}"
        )
        sets_payload = client.request(
            "GET",
            f"/appStoreVersionLocalizations/{localization['id']}/appScreenshotSets",
            params={"limit": "50"},
        )
        screenshot_sets = resources(sets_payload)
        if not screenshot_sets:
            print(f"Screenshots {locale}: NONE")
        for screenshot_set in screenshot_sets:
            screenshot_payload = client.request(
                "GET",
                f"/appScreenshotSets/{screenshot_set['id']}/appScreenshots",
                params={"limit": "50"},
            )
            display_type = screenshot_set.get("attributes", {}).get(
                "screenshotDisplayType", "UNKNOWN"
            )
            print(
                f"Screenshots {locale}/{display_type}: "
                f"{len(resources(screenshot_payload))}"
            )

    infos_payload = client.request(
        "GET", f"/apps/{app['id']}/appInfos", params={"limit": "50"}
    )
    infos = resources(infos_payload)
    print(f"App info records: {len(infos)}")
    for info in infos:
        info_localizations_payload = client.request(
            "GET",
            f"/appInfos/{info['id']}/appInfoLocalizations",
            params={"limit": "50"},
        )
        for localization in resources(info_localizations_payload):
            attributes = localization.get("attributes", {})
            print(
                f"App info {attributes.get('locale', 'UNKNOWN')}: "
                f"name={bool(attributes.get('name'))}, "
                f"subtitle={bool(attributes.get('subtitle'))}, "
                f"privacy_url={bool(attributes.get('privacyPolicyUrl'))}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=("status", "preflight", "attach", "submit"),
        default="status",
    )
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
    current_build_number = build_number(client, current_build_id)

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
    print(f"Attached build: {current_build_number or 'NONE'}")
    print(f"Target build attached: {current_build_id == build['id']}")

    if args.action in ("preflight", "submit"):
        print_preflight(client, app, version)
        if args.action == "preflight":
            return 0

    if args.action == "submit":
        if build_attributes.get("processingState") != "VALID":
            raise AppStoreConnectError(
                "Build cannot be submitted until processingState is VALID"
            )
        if current_build_id != build["id"]:
            raise AppStoreConnectError(
                f"Build {args.build} must be attached before submission"
            )
        if version_attributes.get("appStoreState") not in (
            "PREPARE_FOR_SUBMISSION",
            "READY_FOR_REVIEW",
        ):
            raise AppStoreConnectError(
                "Version cannot be added to a draft review submission; current state is "
                f"{version_attributes.get('appStoreState', 'UNKNOWN')}"
            )

        submission, version_already_added = find_or_create_review_submission(
            client, app["id"], version["id"]
        )
        submission_state = submission.get("attributes", {}).get("state")
        if version_already_added and submission_state != "READY_FOR_REVIEW":
            print(
                "Version is already in a submitted review. Submission state: "
                f"{submission_state or 'UNKNOWN'}"
            )
            return 0

        if not version_already_added:
            client.request(
                "POST",
                "/reviewSubmissionItems",
                body={
                    "data": {
                        "type": "reviewSubmissionItems",
                        "relationships": {
                            "reviewSubmission": {
                                "data": {
                                    "type": "reviewSubmissions",
                                    "id": submission["id"],
                                }
                            },
                            "appStoreVersion": {
                                "data": {
                                    "type": "appStoreVersions",
                                    "id": version["id"],
                                }
                            },
                        },
                    }
                },
            )
            print("Added iOS version 1.0 to the draft review submission.")

        client.request(
            "PATCH",
            f"/reviewSubmissions/{submission['id']}",
            body={
                "data": {
                    "type": "reviewSubmissions",
                    "id": submission["id"],
                    "attributes": {"submitted": True},
                }
            },
        )
        time.sleep(3)
        submitted = client.request(
            "GET",
            f"/reviewSubmissions/{submission['id']}",
        )
        submitted_state = (
            submitted.get("data", {}).get("attributes", {}).get("state", "UNKNOWN")
            if submitted
            else "UNKNOWN"
        )
        submitted_version = client.request(
            "GET",
            f"/appStoreVersions/{version['id']}",
            params={"fields[appStoreVersions]": "appStoreState,versionString"},
        )
        submitted_attributes = (
            submitted_version.get("data", {}).get("attributes", {})
            if submitted_version
            else {}
        )
        print(
            "Submission accepted by App Store Connect. Submission state: "
            f"{submitted_state}; version state: "
            f"{submitted_attributes.get('appStoreState', 'UNKNOWN')}"
        )
        return 0

    if args.action == "status":
        return 0

    if build_attributes.get("processingState") != "VALID":
        raise AppStoreConnectError(
            "Build cannot be attached until processingState is VALID"
        )
    if current_build_id == build["id"]:
        print("No change needed; build is already attached.")
        return 0

    client.request(
        "PATCH",
        f"/appStoreVersions/{version['id']}/relationships/build",
        body={"data": {"type": "builds", "id": build["id"]}},
    )
    if attached_build_id(client, version["id"]) != build["id"]:
        raise AppStoreConnectError("Build attachment could not be verified")
    if current_build_number:
        print(
            f"Replaced build {current_build_number} with build {args.build} "
            f"for iOS version {args.version}."
        )
    else:
        print(f"Attached build {args.build} to iOS version {args.version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AppStoreConnectError, OSError) as error:
        print(f"App Store Connect release check failed: {error}", file=sys.stderr)
        raise SystemExit(1)

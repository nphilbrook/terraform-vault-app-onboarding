#!/usr/bin/env python3
"""
Create an HCP Terraform workspace with VCS integration, set variables,
and trigger a run — all via the HCP Terraform API.

Prerequisites:
  - Set TFE_TOKEN env var to an HCP Terraform API token with org-level access.

Usage:
  export TFE_TOKEN="your-token-here"
  python3 scripts/create_workspace.py <name>
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from typing import Optional

TFC_BASE = "https://app.terraform.io/api/v2"
ORG = "philbrook"
REPO_IDENTIFIER = "nphilbrook/terraform-vault-app-onboarding"
GHAIN_ID = "ghain-ieieBWKoaGhWE3rE"
PROJECT_ID = "prj-Xw1f6AN6tisDhK2f"

VARIABLES = [
    {
        "key": "bound_iam_instance_profile_arns",
        "value": '["arn:aws:iam::590184029125:instance-profile/bastion-profile"]',
        "category": "terraform",
        "hcl": True,
        "sensitive": False,
        "description": "IAM instance profile ARNs allowed to authenticate",
    },
]


def get_token() -> str:
    token = os.environ.get("TFE_TOKEN")
    if not token:
        print("ERROR: Set the TFE_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)
    return token


def api(method: str, path: str, body: Optional[dict] = None, token: str = "") -> dict:
    """Make an HCP Terraform API request and return the parsed JSON response."""
    url = f"{TFC_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode()) if resp.status != 204 else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        print(f"API {method} {path} failed ({exc.code}):\n{detail}", file=sys.stderr)
        sys.exit(1)


def create_workspace(token: str, name: str) -> str:
    """Create a VCS-backed workspace and return its ID."""
    payload = {
        "data": {
            "type": "workspaces",
            "attributes": {
                "name": name,
                "auto-apply": False,
                "vcs-repo": {
                    "identifier": REPO_IDENTIFIER,
                    "github-app-installation-id": GHAIN_ID,
                    "branch": "",
                    "default-branch": True,
                },
            },
            "relationships": {
                "project": {
                    "data": {
                        "id": PROJECT_ID,
                        "type": "projects",
                    }
                }
            },
        }
    }
    resp = api("POST", f"/organizations/{ORG}/workspaces", body=payload, token=token)
    ws_id = resp["data"]["id"]
    print(f"Created workspace '{name}' (id={ws_id})")
    return ws_id


def set_variables(token: str, workspace_id: str, name: str) -> None:
    """Create Terraform variables on the workspace."""
    all_vars = [
        {
            "key": "name",
            "value": name,
            "category": "terraform",
            "hcl": False,
            "sensitive": False,
            "description": "Name of the AWS auth role",
        },
    ] + VARIABLES
    for var in all_vars:
        payload = {
            "data": {
                "type": "vars",
                "attributes": {
                    "key": var["key"],
                    "value": var["value"],
                    "category": var["category"],
                    "hcl": var["hcl"],
                    "sensitive": var["sensitive"],
                    "description": var["description"],
                },
                "relationships": {
                    "workspace": {
                        "data": {"id": workspace_id, "type": "workspaces"}
                    }
                },
            }
        }
        api("POST", f"/workspaces/{workspace_id}/vars", body=payload, token=token)
        print(f"  Set variable '{var['key']}'")


def trigger_run(token: str, workspace_id: str) -> str:
    """Queue a plan on the workspace and return the run ID."""
    payload = {
        "data": {
            "type": "runs",
            "attributes": {
                "message": "Triggered via API script",
            },
            "relationships": {
                "workspace": {
                    "data": {"id": workspace_id, "type": "workspaces"}
                }
            },
        }
    }
    resp = api("POST", "/runs", body=payload, token=token)
    run_id = resp["data"]["id"]
    print(f"Triggered run (id={run_id})")
    return run_id


def get_or_create_run(token: str, workspace_id: str, timeout: int = 10) -> str:
    """Check for an auto-triggered run; if none appears within timeout, create one."""
    start = time.time()
    while time.time() - start < timeout:
        resp = api("GET", f"/workspaces/{workspace_id}/runs", token=token)
        runs = resp.get("data", [])
        if runs:
            run_id = runs[0]["id"]
            status = runs[0]["attributes"]["status"]
            print(f"  Found existing run {run_id} (status: {status})")
            return run_id
        print("  No runs yet, waiting...")
        time.sleep(3)
    print("  No auto-triggered run found, creating one...")
    return trigger_run(token, workspace_id)


def poll_run(token: str, run_id: str, timeout: int = 600) -> None:
    """Poll until the run reaches a terminal state, auto-applying when confirmable."""
    terminal = {
        "planned_and_finished",
        "applied",
        "errored",
        "discarded",
        "canceled",
        "force_canceled",
    }
    confirmable = {"planned", "cost_estimated", "policy_checked", "post_plan_completed"}
    start = time.time()

    while time.time() - start < timeout:
        resp = api("GET", f"/runs/{run_id}", token=token)
        status = resp["data"]["attributes"]["status"]
        print(f"  Run status: {status}")
        if status in terminal:
            break
        if status in confirmable:
            print("  Applying run...")
            apply_run(token, run_id)
            # Continue polling until applied or terminal
            time.sleep(5)
            continue
        time.sleep(5)
    else:
        print("  Timed out waiting for run to complete.")


def apply_run(token: str, run_id: str) -> None:
    """Confirm (apply) a run."""
    payload = {"comment": "Auto-applied via API script"}
    api("POST", f"/runs/{run_id}/actions/apply", body=payload, token=token)
    print(f"  Apply confirmed for run {run_id}")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <name>", file=sys.stderr)
        sys.exit(1)
    name = sys.argv[1]
    token = get_token()

    print(f"Creating workspace '{name}'...")
    workspace_id = create_workspace(token, name)

    print("\nSetting workspace variables...")
    set_variables(token, workspace_id, name)

    print("\nLooking for a run...")
    run_id = get_or_create_run(token, workspace_id)

    print("\nPolling run status...")
    poll_run(token, run_id)

    print("\nDone.")
    print(f"  Workspace: https://app.terraform.io/app/{ORG}/workspaces/{name}")
    print(f"  Run:       https://app.terraform.io/app/{ORG}/workspaces/{name}/runs/{run_id}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Create and apply a destroy run on an HCP Terraform workspace, then delete it.

Prerequisites:
  - Set TFE_TOKEN env var to an HCP Terraform API token with workspace access.

Usage:
  export TFE_TOKEN="your-token-here"
  python3 scripts/delete_workspace.py <workspace-id>
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


def get_workspace_name(token: str, workspace_id: str) -> str:
    """Fetch and return the workspace name for display purposes."""
    resp = api("GET", f"/workspaces/{workspace_id}", token=token)
    return resp["data"]["attributes"]["name"]


def trigger_destroy_run(token: str, workspace_id: str) -> str:
    """Queue a destroy run on the workspace and return the run ID."""
    payload = {
        "data": {
            "type": "runs",
            "attributes": {
                "is-destroy": True,
                "message": "Destroy triggered via delete_workspace.py",
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
    print(f"Triggered destroy run (id={run_id})")
    return run_id


def apply_run(token: str, run_id: str) -> None:
    """Confirm (apply) a run."""
    payload = {"comment": "Auto-confirmed via delete_workspace.py"}
    api("POST", f"/runs/{run_id}/actions/apply", body=payload, token=token)
    print(f"  Apply confirmed for run {run_id}")


def poll_run(token: str, run_id: str, timeout: int = 600) -> str:
    """Poll until the run reaches a terminal state, auto-applying when confirmable.

    Returns the final status string.
    """
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
            return status
        if status in confirmable:
            print("  Confirming destroy...")
            apply_run(token, run_id)
            time.sleep(5)
            continue
        time.sleep(5)

    print("  Timed out waiting for destroy run to complete.", file=sys.stderr)
    sys.exit(1)


def delete_workspace(token: str, workspace_id: str, name: str) -> None:
    """Delete the workspace via the API."""
    api("DELETE", f"/workspaces/{workspace_id}", token=token)
    print(f"Deleted workspace '{name}' (id={workspace_id})")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <workspace-id>", file=sys.stderr)
        sys.exit(1)
    workspace_id = sys.argv[1]
    token = get_token()

    name = get_workspace_name(token, workspace_id)
    print(f"Workspace: '{name}' (id={workspace_id})")

    print("\nTriggering destroy run...")
    run_id = trigger_destroy_run(token, workspace_id)

    print("\nPolling run status...")
    final_status = poll_run(token, run_id)

    if final_status not in {"applied", "planned_and_finished"}:
        print(
            f"\nERROR: Destroy run ended with status '{final_status}'. "
            "Workspace will NOT be deleted.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nDestroy run completed ({final_status}). Deleting workspace...")
    delete_workspace(token, workspace_id, name)

    print("\nDone.")


if __name__ == "__main__":
    main()

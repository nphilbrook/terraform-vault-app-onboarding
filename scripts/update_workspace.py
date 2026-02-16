#!/usr/bin/env python3
"""
Update an existing HCP Terraform workspace to enable KV and set kv_path
to match the existing 'name' variable, then trigger and apply a run.

Prerequisites:
  - Set TFE_TOKEN env var to an HCP Terraform API token with workspace access.

Usage:
  export TFE_TOKEN="your-token-here"
  python3 scripts/update_workspace.py <workspace-id>
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


def get_workspace_vars(token: str, workspace_id: str) -> list:
    """Return all variables for a workspace."""
    resp = api("GET", f"/workspaces/{workspace_id}/vars", token=token)
    return resp.get("data", [])


def find_var(variables: list, key: str) -> Optional[dict]:
    """Find a variable by key in a list of workspace variables."""
    for var in variables:
        if var["attributes"]["key"] == key:
            return var
    return None


def upsert_var(token: str, workspace_id: str, existing_var: Optional[dict],
               key: str, value: str, hcl: bool = False, description: str = "") -> None:
    """Create or update a workspace variable."""
    attrs = {
        "key": key,
        "value": value,
        "category": "terraform",
        "hcl": hcl,
        "sensitive": False,
        "description": description,
    }
    if existing_var:
        var_id = existing_var["id"]
        payload = {"data": {"type": "vars", "id": var_id, "attributes": attrs}}
        api("PATCH", f"/workspaces/{workspace_id}/vars/{var_id}", body=payload, token=token)
        print(f"  Updated variable '{key}'")
    else:
        payload = {
            "data": {
                "type": "vars",
                "attributes": attrs,
                "relationships": {
                    "workspace": {
                        "data": {"id": workspace_id, "type": "workspaces"}
                    }
                },
            }
        }
        api("POST", f"/workspaces/{workspace_id}/vars", body=payload, token=token)
        print(f"  Created variable '{key}'")


def trigger_run(token: str, workspace_id: str) -> str:
    """Queue a plan on the workspace and return the run ID."""
    payload = {
        "data": {
            "type": "runs",
            "attributes": {
                "message": "Triggered via update_workspace.py",
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


def apply_run(token: str, run_id: str) -> None:
    """Confirm (apply) a run."""
    payload = {"comment": "Auto-applied via update_workspace.py"}
    api("POST", f"/runs/{run_id}/actions/apply", body=payload, token=token)
    print(f"  Apply confirmed for run {run_id}")


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
            time.sleep(5)
            continue
        time.sleep(5)
    else:
        print("  Timed out waiting for run to complete.")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <workspace-id>", file=sys.stderr)
        sys.exit(1)
    workspace_id = sys.argv[1]
    token = get_token()

    print(f"Fetching variables for workspace {workspace_id}...")
    variables = get_workspace_vars(token, workspace_id)

    name_var = find_var(variables, "name")
    if not name_var:
        print("ERROR: 'name' variable not found on workspace.", file=sys.stderr)
        sys.exit(1)
    name_value = name_var["attributes"]["value"]
    print(f"  Found name = '{name_value}'")

    print("\nSetting variables...")
    create_kv_var = find_var(variables, "create_kv")
    upsert_var(token, workspace_id, create_kv_var,
               key="create_kv", value="true", hcl=True,
               description="Whether to create a KV policy for this role")

    kv_path_var = find_var(variables, "kv_path")
    upsert_var(token, workspace_id, kv_path_var,
               key="kv_path", value=name_value,
               description="Path within the KV mount to grant access to")

    print("\nTriggering run...")
    run_id = trigger_run(token, workspace_id)

    print("\nPolling run status...")
    poll_run(token, run_id)

    print("\nDone.")


if __name__ == "__main__":
    main()

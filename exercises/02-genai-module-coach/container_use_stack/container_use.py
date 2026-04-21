from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_workflow(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ModuleNotFoundError:
        return parse_minimal_yaml(path.read_text(encoding="utf-8"))


def parse_minimal_yaml(text: str) -> dict:
    workflow: dict = {"steps": []}
    current_step: dict | None = None
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            key = line[:-1]
            if key == "steps":
                workflow["steps"] = []
            else:
                workflow[key] = {}
            continue
        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            workflow[key] = value.strip()
            continue

        if indent == 2 and line.startswith("- "):
            current_step = {}
            workflow["steps"].append(current_step)
            key, value = line[2:].split(":", 1)
            current_step[key.strip()] = value.strip()
            current_list_key = None
            continue

        if current_step is None:
            continue

        if indent == 4 and line.endswith(":"):
            current_list_key = line[:-1]
            current_step[current_list_key] = []
            continue
        if indent == 4 and ":" in line:
            key, value = line.split(":", 1)
            current_step[key.strip()] = parse_scalar(value.strip())
            current_list_key = None
            continue
        if indent == 6 and line.startswith("- ") and current_list_key:
            current_step[current_list_key].append(line[2:].strip())

    return workflow


def parse_scalar(value: str):
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def run_step(step: dict, repo_root: Path, stack_dir: Path) -> None:
    name = step["name"]
    image = step["image"]
    command = step["command"]
    mount_docker_socket = bool(step.get("mount_docker_socket", False))

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{stack_dir}:/workspace",
        "-w",
        "/workspace",
    ]
    if mount_docker_socket:
        docker_cmd.extend(["-v", "/var/run/docker.sock:/var/run/docker.sock"])
    docker_cmd.extend([image, "sh", "-c", command])

    print(f"\n==> {name}")
    print(" ".join(docker_cmd))
    subprocess.run(docker_cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tiny container-use style workflow runner")
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()

    workflow_path = args.workflow.resolve()
    stack_dir = workflow_path.parents[1]
    repo_root = stack_dir.parents[2]
    workflow = parse_workflow(workflow_path)

    print(f"Running workflow: {workflow.get('name', workflow_path.name)}")
    for step in workflow["steps"]:
        run_step(step, repo_root, stack_dir)

    print("\nWorkflow complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Step failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)

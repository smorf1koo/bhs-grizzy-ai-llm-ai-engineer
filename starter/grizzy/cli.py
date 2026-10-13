"""Command line interface. Rename commands and flags freely; document them in README."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from grizzy.config import Config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="grizzy", description="Text request -> validated Godot project edits")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="print the project index as JSON")
    p_index.add_argument("--project", type=Path, required=True)

    p_run = sub.add_parser("run", help="process one request (the project itself is not modified)")
    p_run.add_argument("--project", type=Path, required=True)
    p_run.add_argument("--request", required=True)
    p_run.add_argument("--out", type=Path, default=Path("runs/manual"))
    p_run.add_argument("--budget", type=int, default=None, help="context budget in tokens (default 3000)")
    p_run.add_argument("--model", default=None)

    p_bench = sub.add_parser("bench", help="run benchmark requests, each on a clean copy")
    p_bench.add_argument("--project", type=Path, required=True)
    p_bench.add_argument("--requests", type=Path, required=True)
    p_bench.add_argument("--ids", default=None, help="comma separated ids; default: base_requests from the file")
    p_bench.add_argument("--out", type=Path, default=Path("runs"))
    p_bench.add_argument("--dry-run", action="store_true", help="only list the requests")

    args = parser.parse_args(argv)
    cfg = Config.from_env(budget_tokens=getattr(args, "budget", None), model=getattr(args, "model", None))

    if args.command == "index":
        from grizzy.index import build_index
        print(json.dumps(build_index(args.project), ensure_ascii=False, indent=2))
        return 0

    from grizzy.pipeline import run_request

    if args.command == "run":
        result = run_request(cfg, args.project, args.request, args.out)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    data = yaml.safe_load(args.requests.read_text(encoding="utf-8"))
    ids = args.ids.split(",") if args.ids else data.get("base_requests", [])
    chosen = [r for r in data["requests"] if r["id"] in ids]
    for req in chosen:
        print(f"{req['id']} [{req['difficulty']}]: {req['request']}")
        if not args.dry_run:
            # Only the request text goes to the tool; the evaluation fields of the YAML must NOT.
            run_request(cfg, args.project, req["request"], args.out / req["id"])
    return 0

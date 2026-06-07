#!/usr/bin/env python3
"""Meso-Cosmos Agent — CLI entry point.

Usage:
    meso run --query "长江江豚种群数量变化趋势"
    meso serve --host 0.0.0.0 --port 8080
    meso health --interval 60
"""

import argparse
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))


def cmd_run(args):
    """Execute a single query through the 6-phase pipeline."""
    from src.pipeline.orchestrator import MesoOrchestrator

    orch = MesoOrchestrator()
    result = orch.run(args.query)

    print(f"\n{'='*60}")
    print(f"  Meso-Cosmos Pipeline Result")
    print(f"{'='*60}")
    print(f"  Query:    {result.query[:80]}")
    print(f"  Phases:   {' → '.join(result.phases_executed)}")
    print(f"  Routes:   {len(result.route_decisions)} project(s)")
    for r in result.route_decisions:
        print(f"    → {r.target_project} ({r.skill}) confidence={r.confidence:.1%}")
    print(f"  Verified: {sum(1 for t in result.verification_tags if t.status.value == 'verified')} claims")
    print(f"  Errors:   {len(result.errors)}")
    for e in result.errors:
        print(f"    ⚠ {e[:100]}")
    print(f"  Elapsed:  {result.elapsed_sec:.2f}s")
    print(f"{'='*60}\n")

    if result.synthesis:
        print(result.synthesis)


def cmd_serve(args):
    """Start API server (stub)."""
    print(f"Meso-Cosmos API server starting on {args.host}:{args.port}...")
    print("(API server not yet implemented — use 'meso run' for CLI mode)")


def cmd_health(args):
    """Run health check across all projects."""
    from src.monitor.health_check import check_all_projects
    report = check_all_projects()
    print(f"\n  S-T-V-P Health Check")
    print(f"  {'─'*40}")
    for proj, status in report.items():
        icon = "✅" if status.get("healthy") else "❌"
        print(f"  {icon} {proj}: {status.get('status', 'unknown')}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="meso",
        description="Meso-Cosmos Agent — S-T-V-P execution hub",
    )
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Execute a research query")
    p_run.add_argument("--query", "-q", required=True, help="Research question")
    p_run.set_defaults(func=cmd_run)

    # serve
    p_serve = sub.add_parser("serve", help="Start API server")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8080)
    p_serve.set_defaults(func=cmd_serve)

    # health
    p_health = sub.add_parser("health", help="Health check all projects")
    p_health.add_argument("--interval", type=int, default=60)
    p_health.set_defaults(func=cmd_health)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()

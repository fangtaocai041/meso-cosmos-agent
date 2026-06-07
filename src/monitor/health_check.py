"""
Health Check — monitors all S-T-V-P projects.

Usage:
    from src.monitor.health_check import check_all_projects
    report = check_all_projects()
"""

from pathlib import Path


def check_project(project_path: str) -> dict:
    """Check if a project directory exists and has minimal structure."""
    path = Path(project_path)
    if not path.exists():
        return {"healthy": False, "status": "not_found", "path": str(path)}

    has_config = (path / "config").exists()
    has_src = (path / "src").exists() or (path / ".reasonix").exists()

    return {
        "healthy": has_config or has_src,
        "status": "ok" if (has_config or has_src) else "empty",
        "has_config": has_config,
        "has_src": has_src,
        "path": str(path),
    }


def check_all_projects() -> dict[str, dict]:
    """Check all S-T-V-P projects from workspace root."""
    root = Path(__file__).resolve().parent.parent.parent.parent  # meso-cosmos-agent/
    projects = {
        "fish-ecology-assistant (S)": root / "fish-ecology-assistant",
        "porpoise-agent (P)": root / "porpoise-agent",
        "cognitive-search-engine (V)": root / "cognitive-search-engine",
    }

    report = {}
    for name, path in projects.items():
        report[name] = check_project(str(path))

    return report

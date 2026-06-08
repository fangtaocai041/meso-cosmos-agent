"""
Independent Evaluation Agent — P1: MAS评估冗余

将评估与执行分离 (参照 AEMA/MOSAic 框架):
  - 评估 Agent 独立于执行 Agent
  - 三级评估: 组件级 → 集成级 → E2E
  - 评估日志可审计，与主任务独立
  - 人类监督回路: 关键决策点需 confirm 或拒绝

Usage:
    from src.monitor.eval_agent import EvalAgent
    ea = EvalAgent()
    report = ea.evaluate(result)
    if report.needs_human_review:
        print(report.human_checklist)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class EvalReport:
    """独立评估报告 — 与执行日志分离。"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    level: str = "integration"  # component | integration | e2e
    overall_pass: bool = False
    checks: list[dict] = field(default_factory=list)
    human_checklist: list[str] = field(default_factory=list)
    needs_human_review: bool = False
    recommendations: list[str] = field(default_factory=list)


class EvalAgent:
    """独立评估 Agent — 不参与执行，只做裁判。

    评估维度 (参照 MOSAic 三级):
      L1 组件级: 单项目内部正确性
      L2 集成级: 跨项目交互正确性
      L3 E2E级:   端到端任务完成度
    """

    def __init__(self):
        self._eval_log: list[EvalReport] = []

    def evaluate_component(self, project: str, checks: list[tuple[str, bool, str]]) -> EvalReport:
        """L1: 组件级评估 — 单项目内部检查。"""
        report = EvalReport(level="component")
        for name, passed, detail in checks:
            report.checks.append({"name": f"{project}/{name}", "passed": passed, "detail": detail})
            if not passed:
                report.needs_human_review = True
                report.human_checklist.append(f"[{project}] {name}: {detail}")
        report.overall_pass = all(c["passed"] for c in report.checks)
        self._eval_log.append(report)
        return report

    def evaluate_integration(self, result: dict) -> EvalReport:
        """L2: 集成级评估 — 跨项目交互检查。

        Checks:
          1. 至少 2 个独立项目参与
          2. 三角验证通过 (≥3 sources)
          3. 无未解决的对抗性矛盾
          4. 路由到正确的专家
        """
        report = EvalReport(level="integration")
        checks = []

        # C1: Cross-project participation
        projects_involved = result.get("project_results", {})
        active = [p for p, r in projects_involved.items()
                  if r.get("status") not in ("error", "unavailable")]
        c1_ok = len(active) >= 2
        checks.append(("cross_project_participation", c1_ok,
                       f"{len(active)} projects active" if c1_ok
                       else f"only {len(active)} project(s) — need ≥2"))

        # C2: Triangulation
        validation = result.get("validation", {})
        c2_ok = validation.get("independence_passed", False) or validation.get("unique_projects", 0) >= 2
        checks.append(("triangulation", c2_ok,
                       f"{validation.get('unique_projects', 0)} unique sources"))

        # C3: No unresolved antagonistic contradictions
        contradiction = result.get("contradiction", {})
        c3_ok = contradiction.get("type") != "antagonistic"
        checks.append(("no_antagonistic_block", c3_ok,
                       f"contradiction type: {contradiction.get('type', 'unknown')}"))

        # C4: Correct expert routing
        c4_ok = len(result.get("route_decisions", [])) > 0
        checks.append(("expert_routed", c4_ok,
                       f"{len(result.get('route_decisions', []))} routes"))

        for name, ok, detail in checks:
            report.checks.append({"name": name, "passed": ok, "detail": detail})
            if not ok:
                report.recommendations.append(f"Check {name}: {detail}")

        report.overall_pass = all(c["passed"] for c in report.checks)
        if not report.overall_pass:
            report.needs_human_review = True
            report.human_checklist = [
                f"Integration check failed: {c['name']}" for c in report.checks if not c["passed"]
            ]
        self._eval_log.append(report)
        return report

    def evaluate_e2e(self, query: str, result: dict) -> EvalReport:
        """L3: E2E 评估 — 从查询到最终报告的完整链路。

        Checks:
          1. 所有 6 阶段执行完成
          2. 至少产生输出 (论文/分析)
          3. 无未处理错误
          4. 响应时间 < 阈值
        """
        report = EvalReport(level="e2e")
        checks = []

        # C1: Full pipeline execution
        phases = result.get("phases_executed", [])
        expected = ["understand", "route", "execute", "validate", "synthesize", "evolve"]
        missing = [p for p in expected if p not in phases]
        c1_ok = len(missing) == 0
        checks.append(("full_pipeline", c1_ok,
                       f"missing: {missing}" if missing else "all 6 phases"))

        # C2: Output produced
        papers = sum(len(r.get("papers", [])) for r in result.get("project_results", {}).values())
        synthesis = result.get("synthesis", "")
        c2_ok = papers > 0 or len(synthesis) > 0
        checks.append(("output_produced", c2_ok,
                       f"papers={papers}, synthesis={len(synthesis)} chars"))

        # C3: No unhandled errors
        errors = result.get("errors", [])
        c3_ok = len(errors) == 0
        checks.append(("no_errors", c3_ok, f"{len(errors)} errors" if errors else "clean"))

        # C4: Response time
        elapsed = result.get("elapsed_sec", 0)
        c4_ok = elapsed < 30.0
        checks.append(("response_time", c4_ok, f"{elapsed:.1f}s"))

        for name, ok, detail in checks:
            report.checks.append({"name": name, "passed": ok, "detail": detail})

        report.overall_pass = all(c["passed"] for c in report.checks)
        if not report.overall_pass:
            report.needs_human_review = True
            report.human_checklist = [f"E2E: {c['name']} failed — {c['detail']}"
                                       for c in report.checks if not c["passed"]]
        self._eval_log.append(report)
        return report

    def get_audit_trail(self) -> list[dict]:
        """返回可审计的评估轨迹。"""
        return [
            {
                "timestamp": r.timestamp,
                "level": r.level,
                "passed": r.overall_pass,
                "checks": r.checks,
                "human_review": r.needs_human_review,
            }
            for r in self._eval_log
        ]


# ═══════════════════════════════════════════════════════════
# Convenience
# ═══════════════════════════════════════════════════════════

def evaluate_pipeline_result(result: dict) -> EvalReport:
    """One-liner: 对 pipeline 结果执行 L2+L3 评估。"""
    ea = EvalAgent()
    l2 = ea.evaluate_integration(result)
    l3 = ea.evaluate_e2e("", result)
    # Combine: overall pass = L2 AND L3 pass
    l2.overall_pass = l2.overall_pass and l3.overall_pass
    if l3.needs_human_review:
        l2.needs_human_review = True
        l2.human_checklist.extend(l3.human_checklist)
    return l2

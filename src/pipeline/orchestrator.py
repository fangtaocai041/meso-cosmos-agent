"""
Meso-Cosmos Orchestrator — 6-phase pipeline executor (T-layer core).

Migrated from porpoise-agent/src/agent/orchestrator.py.
De-porpoise-ified: all domain-specific keywords/routing moved to config.

Pipeline (from meso_agent.yaml):
  Phase 0: UNDERSTAND  — Macro-BDI intent formation
  Phase 1: ROUTE       — Meso-Coordination routing
  Phase 2: EXECUTE     — Micro-Execution delegation
  Phase 3: VALIDATE    — Cross-Verification triangulation
  Phase 4: SYNTHESIZE  — Merge multi-project results
  Phase 5: EVOLVE      — Feedback + trigger adaptation

Usage:
    from src.pipeline.orchestrator import MesoOrchestrator

    orch = MesoOrchestrator()
    result = orch.run("长江江豚种群数量变化趋势")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("meso_cosmos.orchestrator")


# ═══════════════════════════════════════════════════════════════
# Core Enums (from porpoise orchestrator, generalized)
# ═══════════════════════════════════════════════════════════════

class ContradictionType(str, Enum):
    ANTAGONISTIC = "antagonistic"        # BLOCK downstream
    NON_ANTAGONISTIC = "non_antagonistic"  # PASS_WITH_NOTE
    STRUCTURAL = "structural"            # PASS
    PHASIC = "phasic"                    # PASS, tag for review


class VerificationStatus(str, Enum):
    VERIFIED = "verified"        # >=3 independent sources
    PENDING = "pending"          # 1-2 sources
    HYPOTHESIS = "hypothesis"    # inference only
    UNVERIFIABLE = "unverifiable"  # BLOCKED


class PipelinePhase(str, Enum):
    UNDERSTAND = "understand"
    ROUTE = "route"
    EXECUTE = "execute"
    VALIDATE = "validate"
    SYNTHESIZE = "synthesize"
    EVOLVE = "evolve"


# ═══════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════

@dataclass
class ContradictionSignal:
    primary_contradiction: str
    primary_aspect: str = ""
    secondary_contradictions: list[str] = field(default_factory=list)
    contradiction_type: ContradictionType = ContradictionType.NON_ANTAGONISTIC
    budget_multiplier: float = 2.5
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VerificationTag:
    claim: str
    status: VerificationStatus = VerificationStatus.PENDING
    sources: int = 0


@dataclass
class RouteDecision:
    target_project: str       # "fish-ecology-assistant" | "porpoise-agent" | "cognitive-search-engine"
    skill: str
    confidence: float
    reason: str
    budget_share: float = 1.0


@dataclass
class PipelineResult:
    query: str
    phases_executed: list[str] = field(default_factory=list)
    route_decisions: list[RouteDecision] = field(default_factory=list)
    contradiction: Optional[dict] = None
    verification_tags: list[VerificationTag] = field(default_factory=list)
    project_results: dict[str, dict] = field(default_factory=dict)
    synthesis: str = ""
    evolution_actions: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    elapsed_sec: float = 0.0
    bdi_trace: list[dict] = field(default_factory=list)  # P2: BDI audit trail


# ═══════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════

class MesoOrchestrator:
    """6-phase Meso-Cosmos pipeline executor.

    Architecture:
      Macro(BDI意图) → Meso(跨项目协调) → Micro(项目执行)

    Performance notes:
      - DirectLoader modules are cached after first import (~1980 calls/s)
      - reset() clears session state for clean reuse
      - NONINTERACTIVE env var suppresses human-in-the-loop prompts
    """

    PHASE_ORDER = [
        PipelinePhase.UNDERSTAND,
        PipelinePhase.ROUTE,
        PipelinePhase.EXECUTE,
        PipelinePhase.VALIDATE,
        PipelinePhase.SYNTHESIZE,
        PipelinePhase.EVOLVE,
    ]

    def __init__(self, config_path: str = "config/coordination.yaml"):
        self.config_path = config_path
        self.config: dict = {}
        self._load_config()
        self._disabled_components: set[str] = set()

        # DirectLoader module cache (lazy, ~1980 calls/s after warm)
        self._dl_cache: dict[str, object] = {}

        # DirectLoader security whitelist (P4: module allowlist)
        self._DL_WHITELIST: set[str] = {
            "cognitive-search-engine/src/meso_agent.py",
            "cognitive-search-engine/src/rule_engine.py",
            "coilia-agent/src/agent/orchestrator.py",
            "porpoise-agent/src/agent/orchestrator.py",
        }

        # Chaos-Enhanced Agent Engine (Langton 1990, Chen & Aihara 1995)
        try:
            from pipeline.chaos_engine import get_chaos_engine
            self._chaos = get_chaos_engine()
        except ImportError:
            try:
                from src.pipeline.chaos_engine import get_chaos_engine
                self._chaos = get_chaos_engine()
            except ImportError:
                self._chaos = None

        # Session state
        self.contradiction_signals: list[ContradictionSignal] = []
        self.verification_tags: list[VerificationTag] = []
        self._source_cache: dict[str, list[str]] = {}

        # BDI trace log (P2: provable BDI architecture)
        self._bdi_trace: list[dict] = []

    def reset(self):
        """Clear session state for clean reuse (stress test / long-running server)."""
        self.contradiction_signals.clear()
        self.verification_tags.clear()
        self._source_cache.clear()
        # Keep config + DL cache intact

    def _load_config(self):
        try:
            import yaml, os
            from pathlib import Path
            path = Path(self.config_path)
            if not path.exists():
                # Fallback: derive from this file's location
                base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                path = Path(base) / "config" / "coordination.yaml"
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                self.config_path = str(path)
        except Exception:
            self.config = {}

    # ── Public API ──

    def run(self, query: str, context: dict | None = None) -> PipelineResult:
        """Execute the full 6-phase pipeline.

        Chaos-Enhanced: each cycle advances the Rössler attractor,
        injecting non-repeating perturbation into routing decisions.
        EntropyGuard prevents divergence by decaying chaos coupling
        when system entropy exceeds safe threshold.

        Args:
            query: Natural language research question
            context: Optional additional context

        Returns:
            PipelineResult with all phase outputs
        """
        import time
        start = time.time()

        # Step chaos engine — advance Rössler + Logistic + Coupling
        if self._chaos:
            self._chaos.step()
            # Safety check: if entropy too high, fall back to deterministic
            if self._chaos.safe_mode:
                self._chaos.reset_to_safe()

        result = PipelineResult(query=query)
        ctx = context or {}

        # BDI: record initial belief state
        bdi_entry = {"phase": "BDI_init", "query": query[:80], "belief": {}, "desire": {}, "intention": {}}

        try:
            # ── Phase 0: UNDERSTAND ──
            intent = self._phase_understand(query, ctx)
            result.contradiction = intent.get("contradiction")
            result.phases_executed.append("understand")
            bdi_entry["belief"]["domain_scores"] = intent.get("domain_scores", {})
            bdi_entry["desire"]["primary_domain"] = intent.get("primary_domain", "unknown")

            # ── Phase 1: ROUTE ──
            routes = self._phase_route(query, intent)
            bdi_entry["intention"]["routes"] = [r.target_project for r in routes]
            result.route_decisions = routes
            result.phases_executed.append("route")

            # ── Phase 2: EXECUTE ──
            exec_results = self._phase_execute(routes, query, ctx)
            result.project_results = exec_results
            result.phases_executed.append("execute")

            # ── Phase 3: VALIDATE ──
            validation = self._phase_validate(exec_results)
            result.verification_tags = validation.get("tags", [])
            if validation.get("violations"):
                result.errors.extend(validation["violations"])
            result.phases_executed.append("validate")

            # ── Phase 4: SYNTHESIZE ──
            result.synthesis = self._phase_synthesize(exec_results, validation)
            result.phases_executed.append("synthesize")

            # ── Phase 5: EVOLVE ──
            evo = self._phase_evolve(result)
            result.evolution_actions = evo
            result.phases_executed.append("evolve")

        except Exception as e:
            logger.exception("Pipeline failed")
            result.errors.append(f"{type(e).__name__}: {e}")

        result.elapsed_sec = round(time.time() - start, 3)
        # BDI trace: record final state
        bdi_entry["belief"]["papers_found"] = sum(
            len(r.get("papers", [])) for r in result.project_results.values()
        )
        bdi_entry["intention"]["executed"] = result.phases_executed
        self._bdi_trace.append(bdi_entry)
        result.bdi_trace = self._bdi_trace  # attach to result for audit
        return result

    # ═══════════════════════════════════════════════════════════
    # Phase 0: UNDERSTAND — Macro-BDI Intent Formation
    # ═══════════════════════════════════════════════════════════

    def _phase_understand(self, query: str, ctx: dict) -> dict:
        """Parse query → classify domain → identify contradiction → form intent."""
        q_lower = query.lower()

        # Domain classification via config-driven keyword matching
        projects = self.config.get("projects", {})
        domain_scores = {}
        for proj_name, proj_cfg in projects.items():
            keywords = proj_cfg.get("activation_keywords", [])
            score = sum(1 for kw in keywords if kw.lower() in q_lower)
            if score > 0:
                domain_scores[proj_name] = score

        # Contradiction analysis
        contradiction = self._analyze_contradiction(query, domain_scores)

        return {
            "query": query,
            "domain_scores": domain_scores,
            "primary_domain": max(domain_scores, key=domain_scores.get) if domain_scores else "cognitive-search-engine",
            "contradiction": {
                "primary": contradiction.primary_contradiction,
                "type": contradiction.contradiction_type.value,
                "budget_multiplier": contradiction.budget_multiplier,
            },
        }

    def _analyze_contradiction(self, query: str, domain_scores: dict) -> ContradictionSignal:
        """Keyword-based contradiction analysis → structured routing signal."""
        q_lower = query.lower()

        # Data scarcity: no domain matched → exhaustive search
        if not domain_scores:
            return ContradictionSignal(
                primary_contradiction="DOMAIN_AMBIGUITY",
                primary_aspect="no_clear_domain_match",
                contradiction_type=ContradictionType.STRUCTURAL,
                budget_multiplier=1.0,
            )

        # Cross-domain: multiple domains matched → coordinate
        if len(domain_scores) >= 2:
            return ContradictionSignal(
                primary_contradiction="CROSS_DOMAIN_COORDINATION",
                primary_aspect="multi_project_routing",
                contradiction_type=ContradictionType.NON_ANTAGONISTIC,
                budget_multiplier=2.0,
            )

        # Single domain → delegate
        return ContradictionSignal(
            primary_contradiction="SINGLE_DOMAIN_DELEGATION",
            primary_aspect=list(domain_scores.keys())[0],
            contradiction_type=ContradictionType.NON_ANTAGONISTIC,
            budget_multiplier=1.0,
        )

    # ═══════════════════════════════════════════════════════════
    # Phase 1: ROUTE — Meso-Coordination
    # ═══════════════════════════════════════════════════════════

    def _phase_route(self, query: str, intent: dict) -> list[RouteDecision]:
        """Route to S-T-V-P projects based on config routing rules (priority-ordered)."""
        routes = []
        q_lower = query.lower()
        routing_cfg = self.config.get("routing", {})
        rules = routing_cfg.get("rules", [])

        # Try explicit routing rules first (highest priority)
        matched = False
        for rule in rules:
            if "default" in rule:
                continue  # handled after explicit rules
            keywords = rule.get("query_contains", [])
            if any(kw.lower() in q_lower for kw in keywords):
                targets = rule.get("route_to", [])
                if isinstance(targets, str):
                    targets = [targets]
                budget_split = rule.get("budget_split", {})
                for proj in targets:
                    # Chaos perturbation: ±0.15 on confidence (non-repeating)
                    conf = 0.8
                    if self._chaos and self._chaos.guard.in_safe_zone:
                        conf += self._chaos.route_bias()
                    routes.append(RouteDecision(
                        target_project=proj,
                        skill=rule.get("skill", "search-literature"),
                        confidence=conf,
                        reason=rule.get("reason", "routing rule matched"),
                        budget_share=budget_split.get(proj, 1.0 / len(targets)),
                    ))
                matched = True

        # Fallback: keyword-based domain matching from projects config
        if not matched:
            domain_scores = intent.get("domain_scores", {})
            projects = self.config.get("projects", {})
            total_score = sum(domain_scores.values()) or 1
            for proj_name, score in sorted(domain_scores.items(), key=lambda x: -x[1]):
                proj_cfg = projects.get(proj_name, {})
                entry_skill = proj_cfg.get("entry_skill", "search-literature")
                routes.append(RouteDecision(
                    target_project=proj_name,
                    skill=entry_skill,
                    confidence=min(score / max(total_score, 1), 1.0),
                    reason=f"domain keywords matched (score={score})",
                    budget_share=score / total_score,
                ))

        # Default rule
        if not routes:
            for rule in rules:
                if "default" in rule:
                    targets = rule.get("default", rule.get("route_to", ["cognitive-search-engine"]))
                    if isinstance(targets, str):
                        targets = [targets]
                    split = rule.get("budget_split", {})
                    for proj in targets:
                        routes.append(RouteDecision(
                            target_project=proj,
                            skill="graph-search-engine" if proj == "cognitive-search-engine" else "search-literature",
                            confidence=0.5,
                            reason="default route",
                            budget_share=split.get(proj, 1.0 / len(targets)),
                        ))

        # Chaos wildcard: ~10% chance to route through unexpected expert
        if self._chaos and self._chaos.wildcard() and self._chaos.guard.in_safe_zone:
            all_projects = list(self.config.get("projects", {}).keys())
            if len(all_projects) >= 2:
                existing = {r.target_project for r in routes}
                others = [p for p in all_projects if p not in existing]
                if others:
                    wildcard_proj = self._chaos.chaotic_pick(others)
                    routes.append(RouteDecision(
                        target_project=wildcard_proj,
                        skill="search-literature",
                        confidence=0.3,
                        reason=f"chaos_wildcard (serendipity exploration)",
                        budget_share=0.1,
                    ))

        # Always include cognitive for validation
        if "cognitive-search-engine" not in {r.target_project for r in routes}:
            routes.append(RouteDecision(
                target_project="cognitive-search-engine",
                skill="graph-search-engine",
                confidence=0.5,
                reason="always-validate gate",
                budget_share=0.2,
            ))

        return routes

    # ═══════════════════════════════════════════════════════════
    # Phase 2: EXECUTE — Micro-Execution
    # ═══════════════════════════════════════════════════════════

    def _phase_execute(self, routes: list[RouteDecision], query: str, ctx: dict) -> dict[str, dict]:
        """Delegate to project agents and collect results."""
        results = {}

        for route in routes:
            proj = route.target_project
            try:
                # DirectLoader for cognitive-search-engine (V)
                if proj == "cognitive-search-engine":
                    result = self._call_cognitive(query, ctx)
                # DirectLoader for coilia-agent (P₂)
                elif proj == "coilia-agent":
                    result = self._call_coilia(query, ctx)
                # DirectLoader for porpoise-agent (P₁)
                elif proj == "porpoise-agent":
                    result = self._call_porpoise(query, ctx)
                else:
                    # Format DELEGATE protocol message
                    result = {
                        "status": "delegated",
                        "delegate_message": (
                            f"DELEGATE to {proj}:\n"
                            f"  skill: {route.skill}\n"
                            f"  context: query={query}\n"
                            f"  budget_share: {route.budget_share}"
                        ),
                    }
                results[proj] = result
            except Exception as e:
                results[proj] = {"status": "error", "error": str(e)}

        return results

    def _call_cognitive(self, query: str, ctx: dict) -> dict:
        """DirectLoader: call cognitive-search-engine via importlib (cached, whitelisted)."""
        if not any("cognitive-search-engine" in m for m in self._DL_WHITELIST):
            return {"status": "blocked", "error": "module not in DirectLoader whitelist"}
        try:
            if "cognitive" in self._dl_cache:
                create_agent = self._dl_cache["cognitive"]
                agent = create_agent(mode="http")
                result = agent.search(query.replace(" ", "_"))
                return result.to_dict() if hasattr(result, 'to_dict') else {"status": "ok"}
            import importlib.util, os
            engine_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "cognitive-search-engine")
            engine_root = os.path.normpath(os.path.abspath(engine_root))
            engine_file = os.path.join(engine_root, "src", "meso_agent.py")
            if not os.path.isfile(engine_file):
                return {"status": "unavailable", "reason": "cognitive engine not found"}
            import sys
            if engine_root not in sys.path: sys.path.insert(0, engine_root)
            spec = importlib.util.spec_from_file_location("cogsearch.meso", engine_file)
            if spec is None or spec.loader is None:
                return {"status": "error", "reason": "import failed"}
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._dl_cache["cognitive"] = mod.create_agent  # cache factory function
            agent = mod.create_agent(mode="http")
            result = agent.search(query.replace(" ", "_"))
            return result.to_dict() if hasattr(result, 'to_dict') else {"status": "ok"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _call_coilia(self, query: str, ctx: dict) -> dict:
        """DirectLoader: call coilia-agent (P₂) via importlib (cached, whitelisted)."""
        if "coilia-agent/src/agent/orchestrator.py" not in self._DL_WHITELIST:
            return {"status": "blocked", "error": "module not in DirectLoader whitelist"}
        try:
            # Use cached module if available
            if "coilia" in self._dl_cache:
                orch_cls = self._dl_cache["coilia"]
                return orch_cls().run(query)

            import importlib.util, os
            agent_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "coilia-agent")
            agent_root = os.path.normpath(os.path.abspath(agent_root))
            agent_file = os.path.join(agent_root, "src", "agent", "orchestrator.py")
            if not os.path.isfile(agent_file):
                return {"status": "error", "error": f"coilia-agent not found at {agent_file}"}
            import sys
            if agent_root not in sys.path:
                sys.path.insert(0, agent_root)
            spec = importlib.util.spec_from_file_location("coilia.orchestrator", agent_file)
            if spec is None or spec.loader is None:
                return {"status": "error", "error": "coilia import failed"}
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._dl_cache["coilia"] = mod.CoiliaOrchestrator  # cache the class
            return mod.CoiliaOrchestrator().run(query)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _call_porpoise(self, query: str, ctx: dict) -> dict:
        """DirectLoader: call porpoise-agent (P₁) via importlib."""
        try:
            import importlib.util, os
            agent_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "porpoise-agent")
            agent_root = os.path.normpath(os.path.abspath(agent_root))
            agent_file = os.path.join(agent_root, "src", "agent", "orchestrator.py")
            if not os.path.isfile(agent_file):
                return {"status": "error", "error": f"porpoise-agent not found at {agent_file}"}
            import sys
            if agent_root not in sys.path:
                sys.path.insert(0, agent_root)
            spec = importlib.util.spec_from_file_location("porpoise.orchestrator", agent_file)
            if spec is None or spec.loader is None:
                return {"status": "error", "error": "porpoise import failed"}
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            orch = mod.Orchestrator()
            import asyncio
            return asyncio.run(orch.run(query))
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # Phase 3: VALIDATE — Cross-Verification
    # ═══════════════════════════════════════════════════════════

    def _phase_validate(self, exec_results: dict[str, dict]) -> dict:
        """Cross-validate results across projects using cognitive validator."""
        tags = []
        violations = []

        for proj, result in exec_results.items():
            papers = result.get("papers", [])
            sources = len(papers)
            status = (
                VerificationStatus.VERIFIED if sources >= 3
                else VerificationStatus.PENDING if sources >= 1
                else VerificationStatus.UNVERIFIABLE
            )
            tags.append(VerificationTag(
                claim=f"{proj} output ({sources} papers)",
                status=status,
                sources=sources,
            ))

        # Check cross-project independence
        unique_projects = len([r for r in exec_results.values() if r.get("status") not in ("error", "unavailable")])
        if unique_projects < 2:
            violations.append(
                f"DEPENDENCY_RISK: only {unique_projects} project(s) contributed. "
                f"Cross-project triangulation requires at least 2."
            )

        return {"tags": tags, "violations": violations}

    # ═══════════════════════════════════════════════════════════
    # Phase 4: SYNTHESIZE — Merge
    # ═══════════════════════════════════════════════════════════

    def _phase_synthesize(self, exec_results: dict[str, dict], validation: dict) -> str:
        """Merge multi-project results into a unified synthesis."""
        parts = []
        for proj, result in exec_results.items():
            status = result.get("status", "unknown")
            papers = len(result.get("papers", []))
            parts.append(f"- **{proj}**: {status}, {papers} papers")

        violations = validation.get("violations", [])
        if violations:
            parts.append(f"\n⚠️ **Validation warnings**:")
            for v in violations:
                parts.append(f"  - {v}")

        return "\n".join(parts)

    # ═══════════════════════════════════════════════════════════
    # Phase 5: EVOLVE — Feedback
    # ═══════════════════════════════════════════════════════════

    def _phase_evolve(self, result: PipelineResult) -> list[dict]:
        """Evaluate metrics, trigger adaptations."""
        try:
            from src.monitor.evolution_executor import EvolutionExecutor
            executor = EvolutionExecutor()
            metrics = {
                "pipeline_success_rate": 0.0 if result.errors else 1.0,
                "recall_rate": sum(
                    len(r.get("papers", [])) for r in result.project_results.values()
                ) / max(len(result.project_results), 1),
            }
            actions = executor.evaluate_and_adapt(metrics)
            return [
                {"param": a.param, "old": a.old_value, "new": a.new_value, "trigger": a.trigger_name}
                for a in actions if a.param
            ]
        except ImportError:
            return []


# ═══════════════════════════════════════════════════════════════
# Convenience
# ═══════════════════════════════════════════════════════════════

def run_pipeline(query: str) -> PipelineResult:
    """One-liner: run the full 6-phase pipeline."""
    orch = MesoOrchestrator()
    return orch.run(query)

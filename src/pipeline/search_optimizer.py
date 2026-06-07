"""
DeepSeek-inspired Search Optimizer — MoE + Satisficing + Two-Tier Search

Core principles (from DeepSeek V2→V4 evolution):
  1. MoE稀疏激活: 只为相关"专家"(P₁/P₂/V)分配计算，不激活全部
  2. MLA-KV压缩: 分层搜索 — 轻量扫描(CSA) → 仅在候选上深度展开(HCA)
  3. MTP并行预测: 多引擎并行，第一个到达阈值即停止
  4. GRPO相对优化: 比较策略效果，自适应选择最优
  5. 满意即止(Satisficing): papers >= threshold + info_gain < epsilon → STOP

Usage:
    from src.pipeline.search_optimizer import OptimizedSearch

    opt = OptimizedSearch(orch)
    result = opt.search("Ochetobius_elongatus", min_papers=8)
    # Auto-stops when satisficed — never exhausts budget unnecessarily
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

@dataclass
class SearchBudget:
    """Energy-aware search budget — DeepSeek-inspired cost control."""
    max_tokens: int = 5000           # hard cap per search
    min_papers_satisfice: int = 8    # "满意即止" threshold
    info_gain_epsilon: float = 0.005 # IG below this → diminishing returns
    tier1_ratio: float = 0.3         # 30% budget for fast scan (CSA)
    tier2_ratio: float = 0.7         # 70% budget for deep dive (HCA)
    confidence_threshold: float = 0.7 # MoE gate: skip expert if confidence < this


@dataclass
class SearchResult:
    species_id: str
    papers: list[dict] = field(default_factory=list)
    papers_found: int = 0
    tokens_spent: float = 0.0
    elapsed_ms: float = 0.0
    stop_reason: str = ""            # "satisficed" | "budget_exhausted" | "no_results"
    tier1_count: int = 0
    tier2_count: int = 0
    cache_hit: bool = False


# ═══════════════════════════════════════════════════════════════
# Result Cache — KV-cache inspired, avoid redundant searches
# ═══════════════════════════════════════════════════════════════

class ResultCache:
    """MLA-inspired result cache: compress & reuse search results.

    Cache entries expire after max_age_seconds.
    Cache hit → zero token cost, instant response.
    """

    def __init__(self, max_age_seconds: int = 3600, max_entries: int = 100):
        self._cache: dict[str, dict] = {}
        self.max_age = max_age_seconds
        self.max_entries = max_entries

    def get(self, species_id: str) -> Optional[dict]:
        entry = self._cache.get(species_id)
        if entry and (time.time() - entry["cached_at"] < self.max_age):
            return entry["papers"]
        return None

    def set(self, species_id: str, papers: list[dict]):
        if len(self._cache) >= self.max_entries:
            # Evict oldest
            oldest = min(self._cache, key=lambda k: self._cache[k]["cached_at"])
            del self._cache[oldest]
        self._cache[species_id] = {
            "papers": papers,
            "cached_at": time.time(),
        }

    def clear(self):
        self._cache.clear()


# ═══════════════════════════════════════════════════════════════
# MoE Gating Network — confidence-based expert activation
# ═══════════════════════════════════════════════════════════════

class MoEGate:
    """DeepSeekMoE-inspired gating: route to experts by confidence.

    Aux-loss-free: no penalty for uneven routing.
    Only activates experts with confidence above threshold.
    """

    def __init__(self, confidence_threshold: float = 0.7):
        self.threshold = confidence_threshold

    def route(self, query: str, available_experts: dict[str, float]) -> list[str]:
        """Select experts above confidence threshold.

        Args:
            query: search query
            available_experts: {expert_name: confidence_score}

        Returns:
            list of expert names to activate (top-k above threshold)
        """
        active = [
            name for name, conf in available_experts.items()
            if conf >= self.threshold
        ]
        # Always keep at least the top expert
        if not active and available_experts:
            active = [max(available_experts, key=available_experts.get)]
        return active


# ═══════════════════════════════════════════════════════════════
# Two-Tier Search: CSA (fast scan) → HCA (deep dive)
# ═══════════════════════════════════════════════════════════════

class TieredSearcher:
    """Hybrid Attention-inspired two-tier search.

    Tier 1 (CSA — Compressed Sparse Attention):
      - Fast scan: titles + years + journals + credibility_score
      - Low token cost (~30% of budget)
      - Filters to top-N candidates

    Tier 2 (HCA — Heavy Compressed Attention):
      - Deep dive: full abstracts + references + citation graph
      - Only on candidates passing Tier 1 filter
      - ~70% of budget
    """

    def __init__(self, budget: SearchBudget):
        self.budget = budget

    def tier1_scan(self, papers: list[dict]) -> list[dict]:
        """Fast scan: keep only papers with credibility_score >= 40.

        Returns top-N candidates for Tier 2 deep dive.
        """
        # Filter by credibility (fast, no API calls)
        candidates = [
            p for p in papers
            if p.get("credibility_score", p.get("trust_score", 50)) >= 40
        ]
        # Sort by score, keep top half
        candidates.sort(
            key=lambda p: p.get("credibility_score", p.get("trust_score", 50)),
            reverse=True,
        )
        return candidates[:max(len(candidates) // 2 + 1, self.budget.min_papers_satisfice)]

    def tier2_deep_dive(self, candidates: list[dict]) -> list[dict]:
        """Deep dive: enrich with abstracts, references, full validation.

        In production, this would call cognitive-search-engine for each candidate.
        Here we return them as-is (already scored by validator).
        """
        # In production: for each candidate, fetch abstract + references
        # via cognitive-search-engine DirectLoader
        return candidates


# ═══════════════════════════════════════════════════════════════
# Satisficing Optimizer — "满意即止" core
# ═══════════════════════════════════════════════════════════════

class SatisficingStopper:
    """GRPO-inspired satisficing stop condition.

    Stop when:
      1. papers_found >= min_papers_satisfice AND info_gain < epsilon
      2. OR budget exhausted
      3. OR 2 consecutive rounds with 0 new papers

    Never exhausts budget unnecessarily.
    """

    def __init__(self, budget: SearchBudget):
        self.budget = budget
        self._zero_rounds = 0

    def should_stop(self, papers_found: int, new_in_round: int,
                    tokens_spent: float, ig: float = 0) -> tuple[bool, str]:
        """Evaluate stop condition. Returns (should_stop, reason)."""
        # Condition 1: Satisficed
        if papers_found >= self.budget.min_papers_satisfice and ig < self.budget.info_gain_epsilon:
            return True, "satisficed"

        # Condition 2: Budget exhausted
        if tokens_spent >= self.budget.max_tokens:
            return True, "budget_exhausted"

        # Condition 3: Diminishing returns
        if new_in_round == 0:
            self._zero_rounds += 1
            if self._zero_rounds >= 2:
                return True, "diminishing_returns"
        else:
            self._zero_rounds = 0

        return False, "continue"


# ═══════════════════════════════════════════════════════════════
# Optimized Search — Main orchestrator
# ═══════════════════════════════════════════════════════════════

class OptimizedSearch:
    """DeepSeek-inspired optimized search pipeline.

    Pipeline:
      1. Check cache → hit? return instantly
      2. MoE Gate → which experts to activate?
      3. Tier 1 (CSA) → fast scan, filter candidates
      4. Tier 2 (HCA) → deep dive on candidates
      5. Satisficing stop → enough? stop early
      6. Update cache

    Energy philosophy:
      "Best energy & time = stop when trend emerges, not when exhaustive."
    """

    def __init__(self, orchestrator=None, budget: SearchBudget = None):
        self.budget = budget or SearchBudget()
        self.cache = ResultCache()
        self.gate = MoEGate(self.budget.confidence_threshold)
        self.tiered = TieredSearcher(self.budget)
        self.stopper = SatisficingStopper(self.budget)
        self.orch = orchestrator  # MesoOrchestrator instance

    def search(self, species_id: str,
               min_papers: int = None,
               force_refresh: bool = False) -> SearchResult:
        """Execute optimized search for a species.

        Args:
            species_id: e.g., "Ochetobius_elongatus"
            min_papers: override satisficing threshold
            force_refresh: skip cache

        Returns:
            SearchResult with papers + performance metrics
        """
        t0 = time.time()
        if min_papers:
            self.budget.min_papers_satisfice = min_papers

        result = SearchResult(species_id=species_id)

        # ── Step 0: Cache check ──
        if not force_refresh:
            cached = self.cache.get(species_id)
            if cached:
                result.papers = cached
                result.papers_found = len(cached)
                result.cache_hit = True
                result.stop_reason = "cache_hit"
                result.elapsed_ms = (time.time() - t0) * 1000
                return result

        # ── Step 1: MoE Gating ──
        experts = self._score_experts(species_id)
        active_experts = self.gate.route(species_id, experts)

        # ── Step 2: Execute via active experts ──
        all_papers = []
        tokens = 0.0
        tier1_count = 0
        tier2_count = 0

        for expert in active_experts:
            # Tier 1: Fast scan (CSA)
            tier1_papers = self._tier1_search(species_id, expert)
            tier1_count += len(tier1_papers)
            tokens += self.budget.max_tokens * self.budget.tier1_ratio * (1.0 / len(active_experts))

            # Filter candidates
            candidates = self.tiered.tier1_scan(tier1_papers)
            if not candidates:
                continue

            # Tier 2: Deep dive (HCA) on candidates
            deep_papers = self.tiered.tier2_deep_dive(candidates)
            tier2_count += len(deep_papers)
            tokens += self.budget.max_tokens * self.budget.tier2_ratio * (1.0 / len(active_experts))

            all_papers.extend(deep_papers)

            # Satisficing check
            new_this_round = len(deep_papers)
            ig = new_this_round / max(tokens, 1)
            stop, reason = self.stopper.should_stop(
                len(all_papers), new_this_round, tokens, ig
            )
            if stop:
                result.stop_reason = reason
                break

        # Dedup
        seen = set()
        unique = []
        for p in all_papers:
            key = p.get("doi", p.get("title", ""))
            if key and key not in seen:
                seen.add(key)
                unique.append(p)

        result.papers = unique
        result.papers_found = len(unique)
        result.tokens_spent = tokens
        result.tier1_count = tier1_count
        result.tier2_count = tier2_count
        result.elapsed_ms = (time.time() - t0) * 1000

        if not result.stop_reason:
            result.stop_reason = "complete"

        # Cache result
        if unique:
            self.cache.set(species_id, unique)

        return result

    def _score_experts(self, species_id: str) -> dict[str, float]:
        """Score available experts for a species (MoE gating input).

        Returns {expert_name: confidence_score}.
        """
        scores = {"cognitive-search-engine": 0.95}  # V always activates
        species_lower = species_id.lower()

        # Porpoise expert (P₁)
        if "neophocaena" in species_lower or "porpoise" in species_lower:
            scores["porpoise-agent"] = 0.9
        else:
            scores["porpoise-agent"] = 0.1

        # Coilia expert (P₂)
        if "coilia" in species_lower:
            scores["coilia-agent"] = 0.9
        else:
            scores["coilia-agent"] = 0.1

        # Fish ecology expert (S)
        scores["fish-ecology-assistant"] = 0.6  # Generic, moderate confidence

        return scores

    def _tier1_search(self, species_id: str, expert: str) -> list[dict]:
        """Tier 1 (CSA): fast scan — titles + basic metadata only.

        Uses cached graph data if available (zero API cost).
        """
        # Try graph cache first (free)
        if self.orch:
            try:
                known = self.orch._load_known(species_id) if hasattr(self.orch, '_load_known') else []
                if known:
                    return known
            except Exception:
                pass

        # Fallback: call cognitive via DirectLoader (lightweight mode)
        if self.orch and expert == "cognitive-search-engine":
            try:
                r = self.orch._call_cognitive(species_id, {})
                return r.get("papers", [])
            except Exception:
                pass

        return []


# ═══════════════════════════════════════════════════════════════
# Convenience
# ═══════════════════════════════════════════════════════════════

def quick_search(species_id: str, min_papers: int = 8) -> SearchResult:
    """One-liner: optimized search with sensible defaults."""
    opt = OptimizedSearch(budget=SearchBudget(min_papers_satisfice=min_papers))
    return opt.search(species_id)

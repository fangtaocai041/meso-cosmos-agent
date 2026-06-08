"""
WuxingMonitor — 五行相生相克平衡监控

五行平衡 = 系统健康。任一元素过强或过弱 → 失衡告警。

Usage:
    from src.monitor.wuxing_monitor import WuxingMonitor
    wm = WuxingMonitor()
    report = wm.check_balance()
    if not report["balanced"]:
        print(report["excess"], report["deficiency"])
"""

import os
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


class WuxingMonitor:
    """五行平衡监控器。

    相生 (Generating): 木→火→土→金→水→木 — 数据流转方向
    相克 (Controlling): 木→土→水→火→金→木 — 制衡校验方向
    """

    ELEMENTS = ["木", "火", "土", "金", "水"]
    PROJECT_MAP = {
        "木": "cognitive-search-engine",
        "火": "meso-cosmos-agent",
        "土": "fish-ecology-assistant",
        "金": "porpoise-agent",
        "水": "coilia-agent",
    }
    GENERATING = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    CONTROLLING = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    def __init__(self, workspace_root: str = None):
        self.root = Path(workspace_root) if workspace_root else self._find_workspace()
        self._configs: dict[str, dict] = {}

    def _find_workspace(self) -> Path:
        """Find workspace root from this file's location."""
        p = Path(__file__).resolve()
        for _ in range(5):
            p = p.parent
            if (p / "meso-cosmos-agent").exists() and (p / "cognitive-search-engine").exists():
                return p
        return Path(".")

    def _load_config(self, element: str) -> Optional[dict]:
        if element in self._configs:
            return self._configs[element]
        if yaml is None:
            return None
        proj = self.PROJECT_MAP.get(element)
        if not proj:
            return None
        cfg_path = self.root / proj / "config" / "wuxing.yaml"
        if cfg_path.exists():
            with open(cfg_path, encoding="utf-8") as f:
                self._configs[element] = yaml.safe_load(f).get("wuxing", {})
        return self._configs.get(element)

    def check_balance(self, metrics: dict = None) -> dict:
        """检查五行平衡状态。

        Args:
            metrics: {element: score} — 外部传入的指标值
                     如果未提供，使用默认值

        Returns:
            {
                "balanced": bool,
                "scores": {element: score},
                "excess": [元素列表],    # 过强
                "deficiency": [元素列表], # 过弱
                "generating_ok": bool,    # 相生流转正常
                "controlling_ok": bool,   # 相克制衡正常
            }
        """
        metrics = metrics or {}
        scores = {}
        excess = []
        deficiency = []

        for elem in self.ELEMENTS:
            cfg = self._load_config(elem)
            if not cfg:
                scores[elem] = 0.5  # default if no config
                continue

            health = cfg.get("health", {})
            lo, hi = health.get("normal_range", [0.3, 0.9])
            score = metrics.get(elem, (lo + hi) / 2)  # default: middle of range
            scores[elem] = score

            if score > hi:
                excess.append(elem)
            elif score < lo:
                deficiency.append(elem)

        # 相生检查: 每个元素的生者不能为0
        generating_ok = all(
            scores.get(self.GENERATING.get(e, ""), 0.5) > 0.1
            for e in self.ELEMENTS
        )

        # 相克检查: 被克元素不能同时为0
        controlling_ok = all(
            scores.get(self.CONTROLLING.get(e, ""), 0.5) > 0.1
            for e in self.ELEMENTS
        )

        return {
            "balanced": len(excess) == 0 and len(deficiency) == 0,
            "scores": scores,
            "excess": excess,
            "deficiency": deficiency,
            "generating_ok": generating_ok,
            "controlling_ok": controlling_ok,
            "advice": self._generate_advice(excess, deficiency),
        }

    def _generate_advice(self, excess: list, deficiency: list) -> list[str]:
        """根据五行失衡生成调节建议。"""
        advice = []
        for elem in excess:
            cfg = self._load_config(elem)
            action = cfg.get("health", {}).get("excess_action", "")
            if action:
                advice.append(f"[{elem}过强] {action}")

        for elem in deficiency:
            cfg = self._load_config(elem)
            action = cfg.get("health", {}).get("deficiency_action", "")
            if action:
                advice.append(f"[{elem}过弱] {action}")

        # 相生相克建议
        for elem in excess:
            controlled = self.CONTROLLING.get(elem)
            if controlled and controlled in deficiency:
                advice.append(
                    f"[相克失衡] {elem}克{controlled}过强 → 扶助{controlled}"
                )

        return advice


# ═══════════════════════════════════════════════════════════
# Convenience
# ═══════════════════════════════════════════════════════════

def check_wuxing_balance() -> dict:
    """One-liner: 检查五行平衡。"""
    wm = WuxingMonitor()
    return wm.check_balance()

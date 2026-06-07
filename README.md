# 🌐 Meso-Cosmos Agent — S-T-V-P 执行中枢

> **角色**: T (Transition) — 连接 S(知识供给) + P(领域专研) + V(验证引擎)
> **架构**: Macro(BDI意图) → Meso(跨项目协调) → Micro(项目执行)
> **管辖**: fish-ecology-assistant (S) + porpoise-agent (P) + cognitive-search-engine (V)

## 项目定位

`meso-cosmos-agent` 是从 `porpoise-agent` 和 `cognitive-search-engine` 中提取的**纯协调层**：

| 来源 | 提取模块 | 行数 |
|------|---------|:---:|
| porpoise | orchestrator, dimensional_evolution, stv_core, emergence_monitor, meso_experiment, resilience_engine, deepseek_optimizer, nlg_engine | ~5,200 |
| cognitive | meso_agent, validator, evolution_executor, paper_health_check | ~1,400 |
| workspace | meso_agent.yaml, meso-orchestrator.md | ~500 |

## S-T-V-P 四体架构

```
         ┌──────────────────────────────────────┐
         │        🌐 Meso-Cosmos Agent (T)       │
         │   UNDERSTAND → ROUTE → EXECUTE →     │
         │   VALIDATE → SYNTHESIZE → EVOLVE     │
         └────┬──────────┬──────────┬───────────┘
              │          │          │
     ┌────────▼──┐ ┌────▼─────┐ ┌─▼──────────┐
     │ 🐟 fish   │ │ 🐬 porp  │ │ 🧠 cognitive│
     │  S (知识) │ │ P (专研) │ │ V (验证)   │
     └───────────┘ └──────────┘ └────────────┘
```

## 快速开始

```bash
cd meso-cosmos-agent
pip install -e .
meso run --query "长江江豚种群数量变化趋势"
```

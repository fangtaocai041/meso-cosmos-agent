# 🌐 Meso-Cosmos Agent — S-T-V-P 执行中枢

> **角色**: T (Transition) — 连接 S(知识供给) + P₁(江豚专研) + P₂(刀鲚专研) + V(验证引擎)
> **架构**: Macro(BDI意图) → Meso(跨项目协调) → Micro(项目执行)
> **管辖**: fish (S) + porpoise (P₁) + coilia (P₂) + cognitive (V)
> **版本**: v1.0.0 | **状态**: ✅ 运行中

## 项目定位

`meso-cosmos-agent` 是 S-T-V-P₁-P₂ 生态系统中的**纯协调层 (T)**。自身包含约 1,000 行核心协调代码，其余 D₃ 模块通过 DirectLoader 从原项目按需加载。

| 位置 | 模块 | 行数 |
|------|------|:--:|
| 🏠 本项目 | `pipeline/orchestrator.py` (6-phase), `monitor/validator.py`, `monitor/evolution_executor.py`, `monitor/health_check.py` | ~1,000 |
| 📡 DirectLoader | cognitive: `meso_agent.py` (BDI+ReAct), porpoise: `orchestrator.py` (5-phase FSM) | 按需加载 |
| ⚙️ 配置 | `config/coordination.yaml` (5项目注册 + 智能路由) | — |

## S-T-V-P₁-P₂ 五体架构

```
         ┌──────────────────────────────────────────┐
         │       🌐 Meso-Cosmos Agent (T)            │
         │   UNDERSTAND → ROUTE → EXECUTE →         │
         │   VALIDATE → SYNTHESIZE → EVOLVE         │
         └────┬─────────┬──────────┬──────────┬─────┘
              │         │          │          │
     ┌────────▼──┐ ┌────▼────┐ ┌───▼────┐ ┌──▼──────┐
     │ 🐟 fish   │ │🐬 porp  │ │🐟 coil │ │🧠 cogn  │
     │ S (知识)  │ │P₁(江豚) │ │P₂(刀鲚)│ │V (验证) │
     └───────────┘ └─────────┘ └────────┘ └─────────┘
```

## 快速开始

```bash
cd meso-cosmos-agent
pip install -e .
meso run --query "长江江豚种群数量变化趋势"
```

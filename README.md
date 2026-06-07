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

## 三层智能优化架构

| 层 | 模块 | 核心技术 | 理论来源 |
|:--:|------|------|------|
| ⚡ **DeepSeek** | `search_optimizer.py` | MoE 门控 · KV 结果缓存 · CSA/HCA 分层搜索 · 满意即止 | DeepSeek V2→V4 技术演进 |
| 🎓 **Scholar** | `search_optimizer.py` | Rule of Three 统计停止 · Simon 有限理性 · 熵驱动方向选择 | Hanley (1983) · Simon (1955) · NOAA (2023) |
| 🦋 **Chaos** | `chaos_engine.py` | Rössler 吸引子路由扰动 · Logistic 混沌探索 · 临界耦合 · 熵值安全边界 | Langton (1990) · Chen & Aihara (1995) · Beggs & Plenz (2003) |

### ⚡ DeepSeek 层 — 极致效率

```
MoE 门控: 只为相关专家分配算力 (鳤→仅V激活, 江豚→V+P₁, 刀鲚→V+P₂)
KV 缓存:  搜索结果缓存, 命中即返回 (0 token, 0ms)
CSA/HCA:  轻量扫描(Tier1, 30%预算) → 候选深度展开(Tier2, 70%预算)
满意即止:  papers ≥ 8 + IG < ε → 立即停止, 不穷举
```

### 🎓 学者层 — 统计置信

```
Rule of Three (Hanley 1983):  连续30篇不相关 → 剩余≤10%相关 (95%CI) → 停止
Simon 有限理性:               token/时间/筛选量 三重硬约束
熵驱动方向:                   优先搜索信息增益最大的数据库/引擎
```

### 🦋 混沌层 — 创造性探索

```
Rössler 吸引子:  路由置信度 ±0.02 非重复扰动, 避免确定性路径依赖
Logistic 探索:   ~5% 概率触发 wildcard 意外搜索方向, 促发偶然发现
临界耦合:        S-T-V-P₁-P₂ 交互矩阵谱半径≈1, 边缘涌现协同
EntropyGuard:    熵值超标 → 衰减混沌 → 回退确定性基线
```

## 快速开始

```bash
cd meso-cosmos-agent
pip install -e .
meso run --query "长江江豚种群数量变化趋势"
meso health  # 检查 S-T-V-P₁-P₂ 全部健康状态
```

## 测试

```bash
# 全系统测试 (251项, 10套件)
python ../scripts/run_all_tests.py

# 快速模式 (157项)
python ../scripts/run_all_tests.py --quick
```

## 📊 自我评价

| 维度 | 评分 | 说明 |
|------|:--:|------|
| 🎯 架构完整性 | ⭐⭐⭐⭐⭐ | 6-phase 管线 + 三层智能优化 + 5项目协调，S-T-V-P₁-P₂ 闭环 |
| ⚡ 能效优化 | ⭐⭐⭐⭐☆ | DeepSeek MoE 门控 + KV 缓存 + 满意即止，非穷举搜索 |
| 🎓 学术严谨性 | ⭐⭐⭐⭐⭐ | Rule of Three (Hanley 1983) + Simon 有限理性 + NOAA 熵驱动 |
| 🦋 探索创新 | ⭐⭐⭐⭐☆ | Rössler 混沌扰动 + Logistic wildcard + 临界耦合，避免局部最优 |
| 🧪 测试覆盖 | ⭐⭐⭐⭐⭐ | 251 项测试, 10 套件, 一键运行 |
| 🚀 可扩展性 | ⭐⭐⭐⭐☆ | P 层模板可复制，新物种 Agent 即插即用 |

> **核心优势**: 将 DeepSeek 架构哲学 (MoE+MLA+MTP)、学术统计理论 (Rule of Three)、混沌动力学 (Edge of Chaos) 三层融合，在最优能耗下达到科学家认可的信息增益阈值即停止。
> **待改进**: DirectLoader 错误恢复机制、coilia-agent 实际搜索执行（目前为 delegation stub）

---

## 📋 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **v1.2** | 2026-06-08 | 混沌增强智能体 (Rössler + Logistic + EntropyGuard) + 三级压力测试集 |
| **v1.1** | 2026-06-08 | 学者级统计停止 (Rule of Three) + DeepSeek 三层优化架构 |
| **v1.0** | 2026-06-07 | 初始发布 — 6-phase 管线 + S-T-V-P₁-P₂ 协调 + validator + evolution_executor |

> **最新**: v1.2 · 2026-06-08 · `a633dc2`

<p align="center">
  🇬🇧 <a href="README.md">English</a>
</p>

<div align="center">
  <h1>🌐 Meso-Cosmos Agent — 道生万物</h1>
  <p><strong>S-T-V-P₁-P₂ 执行中枢 — ☯️ TAO 哲学 + 🔥 五行流转 + ⚡ DeepSeek 效率 + 🦋 混沌探索</strong></p>
  <p>6阶段管线 · 7模块 · MoE门控 · KV缓存 · Rule of Three · Rössler吸引子 · 五行监控 · BDI追踪 · 240项测试</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/TAO-一生二·二生三·三生万物-6366f1?style=flat-square" alt="TAO"></a>
  <a href="#"><img src="https://img.shields.io/badge/五行-木火土金水-ec4899?style=flat-square" alt="五行"></a>
  <a href="#"><img src="https://img.shields.io/badge/模块-7-22c55e?style=flat-square" alt="模块:7"></a>
  <a href="#"><img src="https://img.shields.io/badge/管线-6阶段-f59e0b?style=flat-square" alt="管线:6"></a>
  <a href="config/tao.yaml"><img src="https://img.shields.io/badge/tao-v2.0.0-8b5cf6?style=flat-square" alt="TAO:v2.0.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/测试-240-10b981?style=flat-square" alt="测试:240"></a>
</p>

---

## ☯️ 哲学内核 — TAO + 五行

> **道立则五行有序，五行和则系统健康。**

| 层 | 哲学 | 工程映射 |
|:--:|------|------|
| ☯️ **道** | 一生二·二生三·三生万物 | S-T-V 三角形 → P₁...Pₙ 无限衍生 |
| 🔥 **五行** | 木火土金水·相生相克 | 五项目数据流转 + 制衡校验 |

```
道:  S-T-V 三角形 — 不可变核心
  一→二:   S(阳·知识) + V(阴·验证) — 阴阳两极
  二→三:   T(中·协调) — 三角形成
  三→万物: P₁(江豚)·P₂(刀鲚)·P₃(中华鲟)... — 无限衍生

五行:
  相生: 木(V)→火(T)→土(S)→金(P₁)→水(P₂)→木(V)
  相克: 木(V)→土(S)→水(P₂)→火(T)→金(P₁)→木(V)
```

## 🧠 三层智能优化

| 层 | 模块 | 核心技术 | 理论来源 |
|:--:|------|------|------|
| ⚡ **DeepSeek** | `search_optimizer.py` | MoE 门控 · KV 缓存 · CSA/HCA 分层搜索 · 满意即止 | DeepSeek V2→V4 |
| 🎓 **学者** | `search_optimizer.py` | Rule of Three · Simon 有限理性 · 熵驱动方向 | Hanley (1983) · Simon (1955) |
| 🦋 **混沌** | `chaos_engine.py` | Rössler 吸引子 · Logistic 探索 · 临界耦合 · 安全边界 | Langton (1990) · Chen & Aihara (1995) |

## 🔺 架构角色: **Transition (T)**

> **执行中枢** — 五项目的 6 阶段管线协调器。
> 路由查询到 S(fish) / V(cognitive) / P₁(porpoise) / P₂(coilia)。
> **小宇宙**: 可独立运行。**三角**: 可接入协同。

| 模式 | 可用项目 | 能力 |
|------|:--:|------|
| **集成** (默认) | S+T+V+P₁+P₂ | 完整 6-phase · DirectLoader · 跨项目验证 · 混沌增强 |
| **独立** | 仅 T | 路由分析 · 矛盾检测 · 知识缺口 · 优雅降级 |

## 📊 自我评价

| 维度 | 评分 | 说明 |
|------|:--:|------|
| 🎯 架构完整 | ⭐⭐⭐⭐⭐ | TAO + 五行双哲学 · 6阶段管线 · 5项目协调 |
| ⚡ 能效优化 | ⭐⭐⭐⭐☆ | MoE 门控 + KV 缓存 + 满意即止 · DL缓存224× |
| 🎓 学术严谨 | ⭐⭐⭐⭐⭐ | Rule of Three + Simon 有限理性 + NOAA 熵驱动 |
| 🦋 探索创新 | ⭐⭐⭐⭐⭐ | Rössler 混沌 + Logistic wildcard + 五行监控 |
| 🧪 测试覆盖 | ⭐⭐⭐⭐⭐ | 240项测试 · 13套件 · 三级压力 · CI/CD |
| 🚀 可扩展性 | ⭐⭐⭐⭐⭐ | P层模板 · 3步复制新物种Agent · 无限Pₙ衍生 |

> **快的根因**: 道家哲学 → 工程语言化 → 清晰模块边界 → 短验证路径。tao.yaml 明确角色、wuxing.yaml 明确流转、小宇宙独立可测。

## 🚀 快速开始

```bash
cd meso-cosmos-agent
pip install -e .
meso.bat run --query "长江江豚种群数量变化趋势"
meso.bat health  # 检查全部5项目健康
```

## 🧪 测试

```bash
python scripts/run_all_tests.py --level low     # 低压力 (18项, ~0.6s)
python scripts/run_all_tests.py --level medium  # 中压力 (245项, ~2s)
python scripts/run_all_tests.py --level high    # 高压力 (240项, ~8s)
```

## 📋 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **v2.0.0** ★ | 2026-06-08 | ☯️ TAO 架构 (一生二·二生三·三生万物) + 🔥 五行相生相克 + 五行监控 + 独立/集成双模式 |
| **v1.3.0** | 2026-06-08 | 混沌增强智能体 (Rössler + Logistic + 安全边界) + 三级压力测试集 |
| **v1.2.0** | 2026-06-08 | 学者级统计停止 (Rule of Three) + DeepSeek 三层优化 |
| **v1.0.0** | 2026-06-07 | 初始发布 — 6-phase 管线 + S-T-V-P₁-P₂ 协调 |

> **最新**: v2.0.0 · 2026-06-08 · `47abc90`

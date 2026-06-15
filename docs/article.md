---
title: "当全网还在聊 Prompt Engineering，我们已经把 JIT Context Assembly 部署上线了"
date: 2026-06-15
tags: [context-engineering, jit, ai-agents, prompt-engineering, agent-assembler, 开源]
status: published
author: Agent Assembler Team
---

# 当全网还在聊 Prompt Engineering，我们已经把 JIT Context Assembly 部署上线了

## 为什么你的 AI Agent 总是"失忆"或"答非所问"？

你精心调教了一个 Agent，写了 500 行 system prompt，塞了 20 个 Skill 描述，配了完整的 few-shot 示例。上线第一天，效果惊艳。

上线第一周，用户开始抱怨：

- "它怎么忘了自己是财务顾问，突然开始给我写诗？"
- "我问盈亏平衡，它把税务、合规、报表全讲了一遍，我要的只是一个数字。"
- "上下文超长了，回复越来越慢，还经常截断。"

这些问题有一个共同的名字：**Context Overload（上下文过载）**。

全网都在教你怎么写更好的 Prompt。但我们发现，**问题不在 Prompt 本身，而在你往 Prompt 里塞了什么、什么时候塞、塞多少。**

这就是 Context Engineering 要解决的事。

---

## Prompt Engineering vs Context Engineering：一次优化 vs 系统组装

**Prompt Engineering** 是手艺活。你反复调整措辞、结构、示例，试图让模型"听懂"你的意思。它的优化对象是**一段文本**。

**Context Engineering** 是系统工程。你设计的不是"一段话"，而是**一个动态组装流程**——根据用户意图，在正确的时间，注入正确的上下文。

打个比方：

| 维度 | Prompt Engineering | Context Engineering |
|------|-------------------|---------------------|
| 类比 | 写一封完美的邮件 | 设计一个智能邮件分发系统 |
| 优化对象 | 一段固定文本 | 一套组装规则 |
| 应对变化 | 改 prompt | 改配方/路由 |
| 扩展性 | Skill 越多越混乱 | Skill 越多越精准 |
| Token 效率 | 全量注入，线性增长 | 按需注入，对数增长 |

一句话总结：**Prompt Engineering 是"写好一封信"，Context Engineering 是"建好一个邮局"。**

---

## 核心发现：巨石 Skill 拆分的血泪教训

这不是纸上谈兵。让我讲一个真实的故事。

在 Agent Assembler 的早期，我们有一个叫 `financial_analysis` 的 Skill，**2000+ 行**。它试图覆盖盈亏平衡、现金流预测、合规检查、报表解读、税务计算——所有财务相关的事。

**问题接踵而至：**

1. **每次对话都加载 2000 行**。用户问"帮我算盈亏平衡点"，系统注入了全部 2000 行——其中 80% 与当前问题无关。模型在无关内容中"迷路"，回答质量断崖式下降。

2. **改一处怕三处**。修改合规性检查的规则时，不小心破坏了现金流预测的逻辑。巨石 Skill 的维护成本随规模指数增长。

3. **无法组合**。用户问"帮我做盈亏平衡分析，并检查合规性"——系统只能加载整个巨石，无法精准拼装。

**我们做了什么？**

把 2000 行巨石拆成 5 个独立 Skill：

| Skill | 行数 | 触发场景 |
|-------|------|----------|
| `break_even_analysis` | 120 | 用户提到盈亏平衡、保本点 |
| `cashflow_forecast` | 180 | 用户提到现金流、资金预测 |
| `compliance_check` | 200 | 用户提到合规、监管、法规 |
| `financial_statement` | 150 | 用户提到报表、资产负债表 |
| `tax_calculation` | 160 | 用户提到税、纳税、税率 |

**结果：**

- 平均上下文消耗 **下降 70%**
- 回答准确率 **提升 25%**
- 维护成本从"改一处怕三处"变成"各管各的"

但拆分只是第一步。拆完之后，新问题来了：**怎么知道什么时候该加载哪个 Skill？**

答案就是 JIT Context Assembly。

---

## 两层模型：基础设施层 + 任务层

JIT 不是"什么都不加载"，而是**按需加载**。我们把它分成两层：

### L0 基础设施层（无条件加载）

这是 Agent 的"操作系统"——每次对话都必须存在：

- 身份定义（你是谁、你的角色）
- 输出格式（JSON schema、Markdown 模板）
- 安全边界（拒绝策略、隐私规则）
- 核心工具描述

**判断标准**：如果去掉它，Agent 在**所有场景**下都会出错 → 放进 L0。

### L1 任务层（按需组装）

这是 Agent 的"应用程序"——只在需要时加载：

- 领域 Skill（盈亏平衡公式、合规检查清单）
- 参考文档（法规条文、API 文档）
- Few-shot 示例（特定场景的输入输出）
- 任务约束（"财务建议必须加免责声明"）

**判断标准**：如果去掉它，只在**特定场景**下出错 → 放进 L1。

用一个类比：

> JIT 就像餐厅的"按需点菜"，不是"自助全拿"。
>
> L0 是餐具、调料、基本礼仪——每桌都有，不需要点。
> L1 是你点的菜——根据口味现做，不浪费。

---

## 5 行代码看懂 JIT 核心

以下是 `mini-jit` 引擎的核心组装逻辑（完整实现见仓库 `reference/mini-jit/`）：

```python
def assemble(self, user_input: str) -> AssemblyResult:
    # Layer 1: 基础设施层 — 无条件加载
    infra = load_infrastructure_skills(self.config)

    # Layer 2: 任务层 — 按意图匹配，按需加载
    recipe = match_recipe(user_input, self.config)
    task_skills = load_recipe(recipe, self.config)["skills"] if recipe else []

    # 合并 → 最终 Prompt
    return self.build_prompt(infra + task_skills, user_input)
```

就这么简单。**三件事**：

1. 加载基础设施（永远在）
2. 匹配配方（用户说了什么关键词 → 触发哪个配方 → 加载哪些 Skill）
3. 合并输出

没有魔法，没有黑盒。核心逻辑不到 20 行。

---

## 生产验证：Agent Assembler 已上线运行

这不是 Demo，不是 PPT。

**Agent Assembler** 已经部署上线，服务真实用户。它的上下文系统完全基于 JIT 架构：

- **20+ 硬化配方**覆盖财务、法律、餐饮、直播等多个行业
- **配方路由**自动识别用户意图，精准注入领域知识
- **Token 消耗可控**——每个配方都有 `max_tokens` 上限，杜绝上下文膨胀

从"2000 行巨石 Skill"到"20 个精准配方"，我们用了 3 个月。这 3 个月踩的坑，现在全部沉淀在开源仓库里，你不需要再踩一遍。

---

## 开源发布：context-engineering-kit

我们把这套方法论和参考实现整理成了开源项目：

**👉 [github.com/your-org/context-engineering-kit](https://github.com/your-org/context-engineering-kit)**

仓库包含：

```
context-engineering-kit/
├── docs/
│   ├── two-layer-model.md       # 两层模型设计哲学
│   └── recipe-protocol.md       # 配方协议 JSON Schema 规范
├── reference/
│   └── mini-jit/                # 最小 JIT 引擎（Python 参考实现）
├── templates/                   # 可复用的 Skill / Recipe 模板
├── examples/
│   ├── break-even/              # 示例：盈亏平衡分析
│   └── compliance-check/        # 示例：合规性检查
└── scripts/
    └── validate.py              # 配方校验脚本
```

**你可以用它做什么？**

- 从零搭建自己的 JIT 上下文系统
- 把现有的"巨石 Prompt"拆分成可组合的 Skill
- 定义配方协议，实现意图驱动的上下文路由
- 接入任何 Agent 框架（LangChain / CrewAI / AutoGen / 自研）

---

## 写在最后

2024 年，大家在聊 Prompt Engineering。
2025 年，大家在聊 Loop Engineering。
2026 年，该聊聊 **Context Engineering** 了。

不是因为它更"高级"，而是因为当你的 Agent 从 Demo 走向生产，从 1 个 Skill 变成 20 个 Skill，从单场景变成多场景——**你一定会遇到上下文过载的问题**。

到那时，你会需要一套系统性的方法来解决它。

这就是 Context Engineering Kit 存在的意义。

---

**🌟 如果你觉得有用，请给仓库一个 Star。**
**🔧 如果你在用它，欢迎提交 Issue 和 PR。**
**💬 如果你想讨论，评论区见。**

当全网还在聊 Prompt Engineering 的时候，我们已经把答案开源了。

下一个问题不是"要不要做 Context Engineering"，而是"你什么时候开始"。

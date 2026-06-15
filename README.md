---
title: Context Engineering Kit
date: 2026-06-15
tags: [context-engineering, jit, ai-agents, prompt-engineering]
status: published
---

# Context Engineering Kit

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

> **JIT Context Assembly 方法论与参考实现**

## 核心理念

**按需组装，不是全量加载。**

传统 Agent 系统倾向于把所有 Skill、Memory、Tool 描述一次性塞进上下文窗口——这既浪费 token，又稀释了模型对关键指令的注意力。Context Engineering Kit 提出了一种更优雅的方案：**Just-In-Time Context Assembly**——只在需要时，注入恰好需要的上下文。

## 两层模型

我们将上下文分为两层：

| 层级 | 名称 | 注入时机 | 典型内容 |
|------|------|----------|----------|
| **L0** | 基础设施层 | 每次对话无条件注入 | 身份定义、输出格式、安全边界、核心工具描述 |
| **L1** | 任务层 | 按意图匹配按需组装 | 领域 Skill、参考文档、Few-shot 示例、约束规则 |

```
用户输入 → 意图识别 → 配方匹配 → 按需组装 L1 → 合并 L0 → 最终 Prompt
```

这种分层让系统既保持稳定的基础行为，又能灵活应对多样化任务。

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/maming0203/context-engineering-kit.git
cd context-engineering-kit

# 查看两层模型文档
cat docs/two-layer-model.md

# 查看配方协议
cat docs/recipe-protocol.md

# 运行示例
python3 scripts/validate.py examples/

# 运行 mini-jit 演示
cd reference/mini_jit
python3 demo.py
```

## 仓库结构

```
context-engineering-kit/
├── README.md                    # 本文件
├── docs/
│   ├── article.md               # 技术文章：《当全网还在聊 Prompt Engineering...》
│   ├── two-layer-model.md       # 两层模型详解
│   └── recipe-protocol.md       # 配方协议规范
├── reference/
│   └── mini_jit/                # 最小 JIT 引擎参考实现
├── templates/                   # 可复用的 Skill / Recipe 模板
├── examples/
│   ├── break-even/              # 示例：盈亏平衡分析
│   └── compliance-check/        # 示例：合规性检查
└── scripts/                     # 工具脚本
```

## 📖 核心文章

**[《当全网还在聊 Prompt Engineering，我们已经把 JIT Context Assembly 部署上线了》](docs/article.md)**

从实战角度解读 Context Engineering 与 Prompt Engineering 的本质区别，以及两层模型的由来。

## 与 Agent Assembler 的关系

本项目脱胎于 **Agent Assembler** 的实战经验。在 Agent Assembler 中，我们发现当 Skill 数量超过 15 个时，全量注入会导致：

- Token 消耗线性增长
- 模型在无关 Skill 间"迷路"
- 响应质量显著下降

Context Engineering Kit 是对这些教训的系统化总结——提供方法论、协议规范和参考实现，让任何人都能快速构建自己的 JIT 上下文系统。

Agent Assembler 是**消费者**，Context Engineering Kit 是**方法论与工具箱**。

Agent Assembler 已在生产环境验证此方法论，详见 [agent-assembler](https://github.com/maming0203/agent-assembler)。

## 路线图

- [x] 阶段 1：方法论文档 + 目录结构
- [x] 阶段 2：mini_jit 参考实现（Python）
- [ ] 阶段 3：配方可视化编辑器
- [ ] 阶段 4：与主流 Agent 框架集成（LangChain / CrewAI / AutoGen）

## 贡献

欢迎 PR！请先阅读 `docs/` 下的文档了解设计理念。

## License

MIT © 2026 Context Engineering Kit Contributors

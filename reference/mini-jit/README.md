# Mini-JIT: 最小可运行的 JIT Context Assembly 引擎

> **5 分钟看懂 JIT 怎么跑。**

## 这是什么？

Mini-JIT 是一个 **参考实现**，演示了 Context Engineering 中 "Just-In-Time Context Assembly" 的核心模式：

- **Layer 1（基础设施层）**：每次请求无条件加载 — 核心推理、输出格式化、安全护栏
- **Layer 2（任务层）**：按需加载 — 根据用户输入匹配配方（recipe），加载对应的 Skill

这就是 "JIT" 的含义：**不是一次性塞满上下文，而是按需组装**。

## 代码结构

```
mini-jit/
├── __init__.py       # 导出主要类和函数
├── config.py         # 配置：路径、基础设施 Skill 清单
├── loader.py         # 加载器：读文件、匹配配方
├── assembler.py      # 组装器：两层组装核心逻辑
├── recipes/          # (需创建) 配方 JSON 文件目录
│   └── code_review.json
├── skills/           # (需创建) Skill markdown 文件目录
│   ├── core_reasoning.md
│   ├── output_formatting.md
│   └── safety_guardrails.md
└── README.md         # 你正在读的文件
```

### 核心流程

```
用户输入
    │
    ▼
┌─────────────────────────────┐
│  Layer 1: 基础设施层 (无条件) │
│  - core_reasoning           │
│  - output_formatting        │
│  - safety_guardrails        │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  匹配配方 (trigger words)    │
│  "帮我 review 这段代码"      │
│       → code_review.json    │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Layer 2: 任务层 (按需)      │
│  - code_review skill        │
│  - git_diff skill           │
└─────────────────────────────┘
    │
    ▼
  组装好的 Prompt → 发给 LLM
```

## 使用示例

### 1. 准备目录结构

```bash
cd mini-jit
mkdir -p recipes skills
```

### 2. 创建基础设施 Skill

```bash
# skills/core_reasoning.md
cat > skills/core_reasoning.md << 'EOF'
You are a precise, helpful reasoning engine.
Think step-by-step before answering.
EOF

# skills/output_formatting.md
cat > skills/output_formatting.md << 'EOF'
Format your response clearly with headers and code blocks where appropriate.
EOF

# skills/safety_guardrails.md
cat > skills/safety_guardrails.md << 'EOF'
Never generate harmful content. Decline requests that violate safety policies.
EOF
```

### 3. 创建配方

```bash
# recipes/code_review.json
cat > recipes/code_review.json << 'EOF'
{
  "name": "code_review",
  "description": "Review code for bugs, style, and performance",
  "triggers": ["review", "code review", "审查代码", "帮我看看这段代码"],
  "skills": ["code_review_skill"]
}
EOF

# skills/code_review_skill.md
cat > skills/code_review_skill.md << 'EOF'
When reviewing code:
1. Check for bugs and logic errors
2. Evaluate code style and readability
3. Identify performance issues
4. Suggest improvements
EOF
```

### 4. 运行组装

```python
from mini_jit import ContextAssembler

assembler = ContextAssembler()

# 普通对话 — 只加载基础设施层
result = assembler.assemble("今天天气怎么样？")
print(result.prompt)
# 输出: 包含 3 个基础设施 skill + 用户输入

# 触发配方 — 加载基础设施 + 任务层
result = assembler.assemble("帮我 review 这段 Python 代码")
print(result.recipe_name)  # "code_review"
print(result.prompt)
# 输出: 包含 3 个基础设施 skill + code_review_skill + 用户输入
```

### 5. 检查组装结果

```python
result = assembler.assemble("帮我 review 这段代码: def foo(): pass")

print(f"Recipe matched: {result.recipe_name}")
print(f"Infrastructure skills: {len(result.infrastructure_skills)}")
print(f"Task skills: {len(result.task_skills)}")
print(f"Errors: {result.errors}")
print(f"Prompt length: {len(result.prompt)} chars")
```

## 如何扩展到生产环境

### 1. 配方匹配升级
- **当前**：简单的关键词匹配（`trigger in input`）
- **生产**：使用 embedding 相似度、意图分类模型、或 LLM 判断

### 2. Skill 缓存
- **当前**：每次从磁盘读取
- **生产**：内存缓存（LRU）、热更新、版本管理

### 3. 优先级与冲突解决
- **当前**：按顺序拼接
- **生产**：Skill 优先级、冲突检测、token 预算控制

### 4. 动态 Skill 生成
- **当前**：静态 markdown 文件
- **生产**：根据上下文动态生成 Skill（如 RAG 检索结果）

### 5. 可观测性
- **当前**：无
- **生产**：记录每次组装的 Skill 列表、token 数、匹配耗时

### 6. 多配方匹配
- **当前**：只匹配第一个
- **生产**：支持多配方组合、Skill 去重

## 设计原则

1. **最小依赖**：只用 Python 标准库，零外部依赖
2. **清晰分层**：基础设施 vs 任务，无条件 vs 按需
3. **可扩展**：Config 可注入，Loader 可替换
4. **可观测**：AssemblyResult 包含完整元数据
5. **容错**：Skill 加载失败不阻塞整体流程

## 下一步

- 阅读 `assembler.py` 理解核心逻辑
- 修改 `config.py` 添加你自己的 Skill
- 创建 `recipes/` 和 `skills/` 目录，放入真实内容
- 集成到你的 LLM 调用链中

---

**这就是 JIT Context Assembly 的全部核心。** 剩下的都是工程优化。

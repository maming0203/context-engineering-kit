---
title: 配方协议：Recipe Protocol
date: 2026-06-15
tags: [context-engineering, recipe, protocol, json-schema]
status: draft
---

# 配方协议：Recipe Protocol

配方（Recipe）是 JIT 上下文组装的核心单元。它定义了"当用户意图匹配时，应该注入哪些上下文"。

## 配方 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Context Recipe",
  "type": "object",
  "required": ["id", "name", "trigger_keywords", "skills"],
  "properties": {
    "id": {
      "type": "string",
      "description": "配方的唯一标识符，建议使用 kebab-case"
    },
    "name": {
      "type": "string",
      "description": "配方的可读名称"
    },
    "description": {
      "type": "string",
      "description": "配方的用途说明"
    },
    "trigger_keywords": {
      "type": "array",
      "items": { "type": "string" },
      "description": "触发此配方的关键词列表（任意匹配）"
    },
    "trigger_patterns": {
      "type": "array",
      "items": { "type": "string" },
      "description": "触发此配方的正则表达式（可选，高级用法）"
    },
    "skills": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "path"],
        "properties": {
          "name": { "type": "string" },
          "path": { "type": "string", "description": "Skill 文件的相对路径" },
          "priority": { "type": "integer", "default": 0, "description": "优先级，数字越大越优先" }
        }
      },
      "description": "需要注入的 Skill 列表"
    },
    "routing": {
      "type": "object",
      "properties": {
        "fallback_recipe": {
          "type": "string",
          "description": "当此配方无法处理时的降级配方 ID"
        },
        "exclusive": {
          "type": "boolean",
          "default": false,
          "description": "是否为独占模式（匹配后不再尝试其他配方）"
        }
      }
    },
    "constraints": {
      "type": "object",
      "properties": {
        "max_tokens": {
          "type": "integer",
          "description": "此配方组装的上下文总 token 上限"
        },
        "required_output_format": {
          "type": "string",
          "description": "强制输出格式（如 json、markdown）"
        },
        "disclaimers": {
          "type": "array",
          "items": { "type": "string" },
          "description": "必须附加的免责声明"
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "version": { "type": "string" },
        "author": { "type": "string" },
        "tags": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

## 触发词匹配规则

### 基础匹配：关键词

`trigger_keywords` 使用**任意匹配**（OR 逻辑）——用户输入中包含任意一个关键词即触发。

```json
{
  "trigger_keywords": ["盈亏平衡", "保本点", "break-even"]
}
```

匹配规则：
- **大小写不敏感**（中英文均适用）
- **子串匹配**（"盈亏平衡点" 会匹配 "盈亏平衡"）
- **分词后匹配**（英文按空格分词，中文按字符）

### 高级匹配：正则表达式

`trigger_patterns` 支持正则表达式，适合复杂场景：

```json
{
  "trigger_patterns": [
    "计算.*盈亏",
    "how to.*break.?even"
  ]
}
```

匹配规则：
- 使用 Python `re` 模块语法
- 默认大小写不敏感（`re.IGNORECASE`）
- 与 `trigger_keywords` 是 OR 关系

### 匹配优先级

当多个配方同时匹配时：

1. **独占模式优先**：`exclusive: true` 的配方直接胜出
2. **关键词数量**：匹配关键词越多的配方越优先
3. **显式优先级**：`metadata.priority` 字段（数字越大越优先）
4. **定义顺序**：先定义的配方优先

## 配方结构详解

### trigger_keywords：触发词

```json
{
  "trigger_keywords": ["合规", "监管", "法规", "compliance", "regulatory"]
}
```

**最佳实践**：
- 同时提供中英文关键词
- 包含常见别名和缩写
- 避免过于宽泛的词（如"帮助"、"问题"）

### skills：技能列表

```json
{
  "skills": [
    {
      "name": "compliance_check",
      "path": "skills/compliance_check.md",
      "priority": 10
    },
    {
      "name": "legal_disclaimer",
      "path": "skills/legal_disclaimer.md",
      "priority": 5
    }
  ]
}
```

**字段说明**：
- `name`：Skill 的可读名称（用于日志和调试）
- `path`：Skill 文件的路径（相对于仓库根目录）
- `priority`：当多个 Skill 冲突时的优先级（数字越大越优先）

### routing：路由规则

```json
{
  "routing": {
    "fallback_recipe": "general_finance",
    "exclusive": false
  }
}
```

**字段说明**：
- `fallback_recipe`：当此配方的 Skill 无法处理用户请求时，降级到哪个配方
- `exclusive`：是否为独占模式。独占模式下，匹配后不再尝试其他配方

### constraints：约束条件

```json
{
  "constraints": {
    "max_tokens": 2000,
    "required_output_format": "markdown",
    "disclaimers": [
      "本分析仅供参考，不构成法律建议。"
    ]
  }
}
```

**字段说明**：
- `max_tokens`：此配方组装的上下文总 token 上限（超出时按 priority 裁剪低优先级 Skill）
- `required_output_format`：强制输出格式
- `disclaimers`：必须附加在输出末尾的免责声明

## 示例配方

### 示例 1：盈亏平衡分析

```json
{
  "id": "break-even-analysis",
  "name": "盈亏平衡分析",
  "description": "帮助用户计算产品或服务的盈亏平衡点",
  "trigger_keywords": ["盈亏平衡", "保本点", "break-even", "盈亏分析"],
  "skills": [
    {
      "name": "break_even_formula",
      "path": "skills/financial/break_even.md",
      "priority": 10
    },
    {
      "name": "cost_categorization",
      "path": "skills/financial/cost_types.md",
      "priority": 5
    }
  ],
  "routing": {
    "fallback_recipe": "general_finance",
    "exclusive": false
  },
  "constraints": {
    "max_tokens": 1500,
    "required_output_format": "markdown",
    "disclaimers": [
      "本计算基于简化模型，实际情况可能因税费、市场波动等因素有所不同。"
    ]
  },
  "metadata": {
    "version": "1.0.0",
    "author": "context-engineering-kit",
    "tags": ["finance", "analysis"]
  }
}
```

### 示例 2：合规性检查

```json
{
  "id": "compliance-check",
  "name": "合规性检查",
  "description": "检查业务操作是否符合相关法规要求",
  "trigger_keywords": ["合规", "监管", "法规", "compliance", "regulatory", "法律风险"],
  "trigger_patterns": [
    "是否.*合规",
    "符合.*法规",
    "法律.*风险"
  ],
  "skills": [
    {
      "name": "compliance_checklist",
      "path": "skills/legal/compliance_checklist.md",
      "priority": 10
    },
    {
      "name": "industry_regulations",
      "path": "skills/legal/regulations.md",
      "priority": 8
    },
    {
      "name": "legal_disclaimer",
      "path": "skills/legal/disclaimer.md",
      "priority": 5
    }
  ],
  "routing": {
    "fallback_recipe": "general_legal",
    "exclusive": true
  },
  "constraints": {
    "max_tokens": 3000,
    "required_output_format": "markdown",
    "disclaimers": [
      "本检查仅供参考，不构成法律建议。具体合规要求请咨询专业律师。"
    ]
  },
  "metadata": {
    "version": "1.0.0",
    "author": "context-engineering-kit",
    "tags": ["legal", "compliance"]
  }
}
```

## 配方设计原则

### 原则 1：单一职责

一个配方应该只处理一类意图。如果 `trigger_keywords` 包含完全不相关的词（如同时包含"盈亏平衡"和"员工招聘"），说明配方职责过宽，应该拆分。

### 原则 2：最小注入

只注入当前任务真正需要的 Skill。宁可少注入（用户追问时再补充），不要多注入（浪费 token 且干扰模型）。

### 原则 3：明确边界

每个配方的 `constraints.max_tokens` 应该明确设定。没有上限的配方会导致上下文无限膨胀。

### 原则 4：可测试

每个配方都应该有对应的测试用例（放在 `examples/` 目录下），验证：
- 触发词能正确匹配
- 注入的 Skill 内容正确
- 输出符合约束条件

## 下一步

- 查看 `reference/mini-jit/` 了解配方的加载与组装逻辑
- 查看 `examples/` 下的完整示例
- 查看 `templates/` 获取可复用的配方模板

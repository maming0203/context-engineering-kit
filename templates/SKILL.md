---
name: example-skill
version: 1.0.0
description: "A brief description of what this skill does."
tags:
  - example
  - template
---

# Example Skill

## When to Use

Use this skill when the user's request involves:

- Condition 1: e.g., analyzing financial data
- Condition 2: e.g., calculating specific metrics
- Condition 3: e.g., generating structured reports

**Trigger keywords:** keyword1, keyword2, keyword3

## Steps

1. **Parse Input** — Extract relevant parameters from the user's request.
2. **Validate** — Ensure all required inputs are present and valid.
3. **Execute** — Perform the core computation or analysis.
4. **Format Output** — Structure the result according to the expected format.
5. **Verify** — Run validation checks on the output before returning.

## Pitfalls

- ⚠️ **Do not** assume missing values — ask the user for clarification.
- ⚠️ **Do not** skip validation steps even if input looks correct.
- ⚠️ **Beware** of edge cases: zero values, negative numbers, missing fields.
- ⚠️ **Never** return unverified results to the user.

## Verification

After completing the steps, verify:

- [ ] All required fields are present in the output
- [ ] Calculations are mathematically correct
- [ ] Output format matches the expected schema
- [ ] No sensitive data is leaked in the response

## Size Limit Reminder

> ⚠️ This SKILL.md file must remain under **4KB** in size.
> If this file exceeds 4KB, split it into multiple smaller skills or
> move detailed reference material to a separate document.
>
> Check size: `wc -c SKILL.md`

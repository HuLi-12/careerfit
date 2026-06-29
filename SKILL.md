---
name: CareerFit Evidence
description: 简历-JD证据链匹配与求职提升助手，支持简历解析、岗位能力建模、人岗匹配评分、风险诊断、简历优化、面试预测和技能补差路线生成。
version: 1.0.0
author: careerfit-team
tags:
  - resume
  - recruitment
  - career
  - job-matching
  - interview
  - skill-gap
---

# CareerFit Evidence

## Skill 能力

CareerFit Evidence 面向人才与机会双向匹配场景，通过“岗位胜任力证据链”方法，将岗位 JD 与候选人简历建立可解释匹配关系。

核心流程：

```text
输入简历/JD → 输入分类 → 简历解析 → JD建模 → 证据链匹配 → 匹配评分 → 报告生成
```

## 支持场景

1. 求职者：简历-JD匹配诊断、简历优化、面试预测、技能补差。
2. 招聘方：候选人初筛、优势风险分析、面试追问、评分表。
3. 仅简历：职业方向推荐与简历问题诊断。
4. 仅 JD：JD优化、候选人画像、筛选标准、面试题库。

## 推荐输入

```text
【简历】
姓名：张三
目标岗位：Java后端开发
项目经历：...
技能：Java、Spring Boot、MySQL

【岗位JD】
招聘 Java 后端开发工程师，要求熟悉 Java、Spring Boot、MySQL，有 Redis 经验优先。
```

## 输出内容

- 综合匹配度
- 岗位核心要求拆解
- 证据链匹配表
- 红黄绿风险诊断
- 简历优化建议
- 面试预测问题
- 技能补差路线

---

## Execution Instructions

### Trigger

Invoke this skill when the user:
- Provides a resume and a job description for matching analysis
- Asks for resume optimization, career direction, or skill gap diagnosis
- Asks for interview question prediction or candidate evaluation
- Provides only a resume or only a JD

### How to invoke (Claude Code built-in)

When the user's message matches any trigger condition:

1. Save the user's input text to a temp file
2. Run the Python pipeline:

```bash
cd /path/to/careerfit-evidence-skill
python src/main.py --input /path/to/temp_input.txt
```

If the user input is shorter than 10 characters, ask them to provide more details instead of running the pipeline.

### Return the output directly

The skill outputs a Markdown report (or JSON with `--format json`). Return it directly to the user without additional commentary.

### Task mode routing

| User intent | TaskMode | Output type |
|---|---|---|
| Resume + JD match scoring | resume_jd_match | 10-chapter match report |
| Recruiter evaluation | recruiter_eval | Candidate assessment report |
| Resume only (career direction) | resume_only | Career planning report |
| JD only (position analysis) | jd_only | JD optimization report |
| Interview preparation | interview_prepare | Interview question list |
| Resume optimization | resume_optimize | Optimization suggestions |
| Skill gap / learning path | skill_gap_plan | Learning roadmap |



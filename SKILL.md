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

## 执行说明（Claude 调用指令）

### 触发条件

当用户输入包含以下内容时，调用本 Skill：

| 触发关键词 | 示例 |
|---|---|
| 简历 + JD / 人岗匹配 / 岗位匹配度 | 简历+岗位描述，要求评分 |
| 仅简历 / 职业方向 / 简历诊断 | 只有简历文本，无 JD |
| 仅 JD / 岗位优化 / 候选人画像 | 只有 JD 文本，无简历 |
| 招聘方 / 候选人评估 / 初筛 | 要求从招聘方角度评估 |
| 面试准备 / 面试预测 / 面试追问 | 要求预测面试问题 |
| 简历优化 / 润色简历 | 要求修改简历 |
| 技能补差 / 学习路线 / 技能差距 | 要求补强计划 |

### 调用方式

将用户输入写入临时文件，调用 CLI：

```bash
cd /path/to/careerfit-evidence-skill
python src/main.py --input /tmp/careerfit_input.txt
```

若用户输入较短（< 10 字符），直接提示用户补充。

### 结果返回

Skill 输出 Markdown 报告。直接返回给用户，无需额外解释。

### 任务模式对应

| 用户意图 | 内部 TaskMode | 输出报告类型 |
|---|---|---|
| 简历+JD 匹配评分 | resume_jd_match | 10 章人岗匹配诊断报告 |
| 招聘方评估候选人 | recruiter_eval | 候选人岗位匹配评估报告 |
| 仅简历方向推荐 | resume_only | 职业方向与简历优化初步报告 |
| 仅 JD 分析 | jd_only | JD 优化与候选人画像报告 |
| 面试准备 | interview_prepare | 面试预测与追问列表 |
| 简历优化 | resume_optimize | 简历定向优化建议 |
| 技能补差 | skill_gap_plan | 技能补差路线



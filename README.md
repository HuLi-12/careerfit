# CareerFit Evidence：岗位胜任力证据链匹配助手

## 1. 项目简介

CareerFit Evidence 是一个面向“人才与机会双向匹配”赛题的可运行 Skill 工程。它不是简单的简历润色工具，而是围绕“岗位要求—简历证据—匹配等级—风险诊断—优化建议”构建完整分析链路。

## 2. 核心创新

### 2.1 岗位胜任力证据链

每条 JD 要求都要寻找简历中的对应证据：

```text
JD要求 → 简历证据 → 匹配等级 → 风险等级 → 优化建议
```

### 2.2 红黄绿风险分级

| 风险等级 | 含义 |
|---|---|
| green | 已满足岗位要求 |
| yellow | 部分满足，但证据不足 |
| red | 核心要求缺失或严重不匹配 |

### 2.3 双视角报告

- 求职者视角：投递建议、简历优化、面试准备、学习路线。
- 招聘方视角：候选人初筛、优势风险、面试追问、评分表。

## 3. 功能模块

| 模块 | 说明 |
|---|---|
| input_classifier | 输入识别与任务分流 |
| resume_parser | 简历结构化解析 |
| jd_parser | JD岗位能力建模 |
| evidence_matcher | 简历-JD证据链匹配 |
| score_engine | 匹配度评分与风险诊断 |
| report_generator | Markdown报告生成 |
| resume_optimizer | 简历定向优化建议 |
| interview_generator | 面试问题预测 |
| safety_checker | 敏感信息规避与合规说明 |

## 4. 工程结构

```text
careerfit-evidence-skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── examples/
├── src/
│   ├── main.py
│   ├── router.py
│   ├── config.py
│   ├── prompts/
│   ├── schemas/
│   ├── services/
│   └── data/
├── tests/
└── docs/
```

## 5. 快速运行

当前版本仅依赖 Python 标准库，推荐 Python 3.10+。

```bash
python src/main.py --input examples/input_match_analysis.txt --output examples/output_match_report.md
```

JSON 输出：

```bash
python src/main.py --input examples/input_match_analysis.txt --format json
```

标准输入：

```bash
cat examples/input_match_analysis.txt | python src/main.py
```

## 6. 测试

```bash
python -m unittest discover -s tests
```

## 7. 参赛价值

- 场景清晰：聚焦求职者与招聘方双向匹配。
- 落地性强：粘贴简历和 JD 即可运行。
- 创新明确：证据链匹配与风险分级。
- 工程可控：模块化结构，支持 Prompt 和规则双实现。
- 鲁棒性强：支持空输入、仅简历、仅 JD、格式混乱、中英文混合。
- 安全合规：敏感信息不参与评分。

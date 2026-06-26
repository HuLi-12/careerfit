# CareerFit Evidence：岗位胜任力证据链匹配助手

## 1. 项目简介

CareerFit Evidence 是一个面向"人才与机会双向匹配"赛题的可运行 Skill 工程。它不是简单的简历润色工具，而是围绕"岗位要求—简历证据—匹配等级—风险诊断—优化建议—学习路线"构建完整分析链路，支持求职者和招聘方双视角。

---

## 2. 核心创新

### 2.1 岗位胜任力证据链（Evidence Chain）

每条 JD 要求通过 `alias expansion → keyword matching → synonym mapping → evidence level → match level → risk level → confidence → suggestion` 完整链路分析：

```text
JD要求（如：熟悉 Redis）
  → 别名扩展（Redis = 缓存 = Cache）
  → 简历证据召回（技能栏 / 项目经历）
  → 证据等级判定（A/B/C/D/E）
  → 匹配等级判定（strong/medium/weak/none）
  → 风险等级判定（green/yellow/red）
  → 置信度计算
  → 优化建议生成
```

### 2.2 五级证据等级

| 等级 | 判断标准 | 匹配等级 |
|------|----------|----------|
| A | 技能栏出现 + 项目有明确实践且有结果指标 | strong |
| B | 技能栏出现 + 项目有相关描述但无结果 | medium |
| C | 技能栏出现但无项目支撑，或项目有相关但技能栏无 | medium |
| D | 只有相近经历或弱语义映射匹配 | weak |
| E | 未发现任何证据 | none |

### 2.3 动态加权评分

```text
总分 = must_have基础分 + nice_to_have加分 - 风险扣分（上限20）
```

- Must-Have 基础分：纯证据驱动，无默认补分
- Nice-to-Have 加分：封顶 +10
- 风险扣分：red × 8 + yellow × 3，上限 20
- 含置信度和信息完整度辅助指标

### 2.4 红黄绿风险分级

| 风险等级 | 含义 |
|----------|------|
| green | 已满足岗位要求 |
| yellow | 部分满足，但证据不足或为可选项 |
| red | 核心要求缺失或严重不匹配 |

### 2.5 双视角报告

- **求职者视角**：10 章节诊断报告，含投递建议、简历优化、面试预测、7天/14天/30天学习路线
- **招聘方视角**：候选人初筛、优势风险、面试追问、面试评分表

---

## 3. 专家榜评分项对应

| 专家榜评分项 | 项目对应设计 |
|-------------|-------------|
| 鲁棒性 | 60 项测试、异常输入兜底、空输入/仅简历/仅JD/混合语言/Markdown 全覆盖 |
| 创新性 | EvidenceBlock 五级证据等级、结构化证据链、动态加权评分、红黄绿风险 |
| 结果质量 | 10 章节诊断报告、证据附录、学习路线、面试预测、简历优化 |
| 技术设计 | 模块化 9 大服务、规则外置（skill_alias/semantic_match/skill_taxonomy）、CI |
| 工程规范 | README、SKILL.md（validate PASS）、pyproject.toml、Makefile、60 tests |
| 安全合规 | 敏感信息不参与评分、安全合规说明、SafetyChecker 检测 |

---

## 4. 测试与CI

```
Ran 60 tests in 0.109s
OK
```

- GitHub Actions 自动运行：push/PR 触发全量测试 + SKILL.md 校验
- 测试覆盖：评分完整性、证据等级结构、风险等级、输入鲁棒性、岗位族、同义映射

---

## 5. 功能模块

| 模块 | 说明 |
|------|------|
| input_classifier | 输入识别与任务分流（仅简历/仅JD/双输入） |
| resume_parser | 简历结构化解析（技能/项目/教育/证书） |
| jd_parser | JD 岗位能力建模（must-have/nice-to-have/hidden） |
| evidence_matcher | 简历-JD 证据链匹配（含同义映射+弱语义） |
| score_engine | 动态加权评分与风险诊断 |
| report_generator | 10 章节 Markdown/JSON 报告生成 |
| resume_optimizer | 简历定向优化建议 |
| interview_generator | 面试问题预测（技术/项目/HR/反问） |
| learning_path_generator | 7天/14天/30天技能补差路线 |
| safety_checker | 敏感信息规避与合规说明 |

## 6. 工程结构

```text
careerfit-evidence-skill/
├── SKILL.md                     # Skill 元数据（validated）
├── README.md
├── pyproject.toml               # Black + pytest 配置
├── Makefile                     # format/test/run/validate/package
├── requirements.txt
├── .github/workflows/test.yml   # GitHub Actions CI
├── examples/
│   ├── input_match_analysis.txt
│   └── output_match_report.md   # 完整10章节报告示例
├── src/
│   ├── main.py                  # CLI 入口
│   ├── router.py                # 路由调度
│   ├── config.py                # 全局配置
│   ├── schemas/models.py        # 数据模型（EvidenceBlock/ScoreResult）
│   ├── services/                # 9 大服务模块
│   ├── data/                    # 规则数据（skill_alias/semantic_match/taxonomy）
│   └── prompts/
├── tests/                       # 60 项测试
├── scripts/                     # validate/package
└── docs/
```

## 7. 快速运行

当前版本仅依赖 Python 标准库，推荐 Python 3.10+。

```bash
# Markdown 报告
python src/main.py --input examples/input_match_analysis.txt --output examples/output_match_report.md

# JSON 输出（含 score/evidence_matches/evidence_blocks）
python src/main.py --input examples/input_match_analysis.txt --format json

# 标准输入
cat examples/input_match_analysis.txt | python src/main.py
```

## 8. 典型输出片段

```text
# CareerFit 人岗匹配诊断报告

## 0. 一句话结论
候选人与岗位存在一定相关性，但证据链不够充分...

## 1. 综合评分
| 维度                    | 得分 |
|------------------------|-----:|
| 总分                    | 64/100 |
| Must-Have 基础分        | 82.0 |
| Nice-to-Have 加分       | +3.2 |
| 风险扣分                | -21.0 |
| 置信度                  | 70% |
| 信息完整度              | 53% |
```

## 9. 参赛价值

- **场景清晰**：聚焦求职者与招聘方双向匹配
- **落地性强**：粘贴简历和 JD 即可运行
- **创新明确**：EvidenceBlock 证据链与动态评分
- **工程可控**：模块化 9 大服务，规则外置可扩展
- **鲁棒性强**：60 测试覆盖空输入/仅简历/仅JD/格式混乱/中英文混合
- **安全合规**：敏感信息不参与评分

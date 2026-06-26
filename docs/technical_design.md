# 技术设计文档

## 核心架构

```text
main.py → router.py → input_classifier.py → resume_parser.py + jd_parser.py → evidence_matcher.py → score_engine.py → report_generator.py
```

## 设计原则

1. 可运行优先：当前版本不依赖外部 API。
2. 可解释优先：所有匹配结论都保留证据链。
3. 可扩展：prompts 目录保留 LLM 编排模板，后续可替换为模型结构化解析。
4. 合规安全：敏感信息不参与评分。

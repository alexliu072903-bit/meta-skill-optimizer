# Meta-Skill Optimizer

[English](README.md)

一个轻量的 Agent Skill 和本地工具集，用来把一组 Agent Skills 作为一个完整的行为系统进行审查和优化。

一个 Skill 单独看可能非常优秀，但整套系统却可能变得更慢、更僵化或更难做出明确判断。不使用 Meta-Skill Optimizer 时，我们通常依靠直觉修改指令；使用它之后，每次改动都会使用相同的行为 Cases，与不可变 Baseline 进行对照。

这套审查机制会：

- 把 Skills、Preference、Prompts 和 Context Rules 作为一个完整测试对象导入；
- 判断每个组件提供什么用户价值，以及它为什么必须单独存在；
- 把原始系统保存为不可变 Baseline；
- 把每次修改隔离到独立 Candidate；
- 使用相同 Cases 和执行配置对比 Baseline 与 Candidate；
- 保存判断证据、回归情况，以及 `accepted`、`rejected` 或 `inconclusive` 决策。

最终目标不是得到一组写得更漂亮的 Prompts，而是形成一套更简单、更有能力，并且每次取舍都有依据的 Agent 指令系统。

## 使用

克隆仓库，并声明所有会实质影响 Agent 行为的指令来源：

```bash
git clone https://github.com/alexliu072903-bit/meta-skill-optimizer.git
cd meta-skill-optimizer
cp subject.example.json subject.local.json
# 在 subject.local.json 中填写本地来源路径。
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
```

创建一个 Review Session 和一个隔离的 Candidate：

```bash
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
python3 scripts/review_session.py candidate my-review simpler-system
# 只修改 workspace/sessions/my-review/candidates/simpler-system。
python3 scripts/review_session.py seal-candidate my-review simpler-system
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

使用遵循 [`protocol/runner.md`](protocol/runner.md) 的 Agent 执行 Plan，然后注册 Results、完成比较并记录决策：

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-system
python3 scripts/review_session.py decide my-review --candidate simpler-system \
  --verdict accepted --reason "行为得到改善，并且没有重要回归。"
```

仓库不会自动修改正式来源。私人测试对象、Results 和 Review Sessions 都保存在 Git 默认忽略的本地 `workspace/` 中。

## 仓库结构

```text
meta-skill-optimizer/
├── SKILL.md
├── protocol/
│   ├── system-review.md
│   ├── evaluation.md
│   ├── runner.md
│   └── safety.md
├── schemas/
├── scripts/
├── benchmark/cases/
├── subject.example.json
└── workspace/              # 私人目录，Git 默认忽略
```

Agent 以 [`SKILL.md`](SKILL.md) 作为入口。`protocol/` 中保存完整的审查、评估、Runner 和安全规则。

## 当前边界

Meta-Skill Optimizer 目前处于实验阶段。导入、隔离、Review Session、校验、比较、决策记录和 Patch 生成已经可用。

Codex 和 Claude Code 的原生执行 Adapter 尚未实现。仓库未来只支持这两个 Runtime。系统会保存 Feedback，但不会自动把它转化成新 Case 或 Candidate；这项判断留给实际使用者和他的 Agent。

## License

MIT

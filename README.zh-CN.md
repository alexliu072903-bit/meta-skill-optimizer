# Meta-Skill Optimizer

[English](README.md)

**判断你的 Agent Skills 组合起来是否真的更好，并用证据而不是直觉优化整个系统。**

一个 Skill 单独看可能非常优秀，但整套系统却可能变得更慢、更僵化或更难做出明确判断。Meta-Skill Optimizer 把 Skills、Preference、Prompts 和 Context Rules 放在一起，作为一个完整的行为系统进行审查。

## 为什么使用它？

不使用这个仓库时，我们通常通过阅读和修改文字来优化 Skill：

```text
看到有价值的内容 → 继续增加规则 → 系统越来越复杂
→ Agent 表现变差时，不知道问题来自哪里
```

使用 Meta-Skill Optimizer 后，每次改动都会变成一次对照实验：

```text
完整系统 → 不可变 Baseline → 一次 Candidate 修改
→ 相同 Cases → 行为对比 → 保留或撤回
```

| 不使用 | 使用 |
| --- | --- |
| 判断每个 Skill 写得好不好 | 判断整个系统实际做得好不好 |
| 看到好内容就继续保留 | 要求组件产生可观察的用户价值 |
| 同时修改多处指令 | 每次只测试一个有边界的 Candidate |
| 依靠记忆和直觉判断 | 与不可变 Baseline 进行对照 |
| 不断累积规则 | 有证据地新增、增强、重路由、合并、拆分、降级或删除 |

最终得到的不是一组写得更漂亮的 Prompts，而是一套更简单、更有能力，并且每次取舍都有依据的 Agent 指令系统。

## 它会做什么？

1. 把完整指令系统导入私密、隔离的本地 Workspace。
2. 判断每个组件提供什么价值，以及它为什么必须单独存在。
3. 把原始系统保存为不可变 Baseline。
4. 用相同的行为 Cases 测试一个修改后的 Candidate。
5. 保存原始输出和判断证据，对比改善与回归。
6. 记录 `accepted`、`rejected` 或 `inconclusive`，但不修改正式来源。

## 快速开始

环境要求：Python 3，以及一套你有权审查的本地指令系统。

```bash
git clone https://github.com/alexliu072903-bit/meta-skill-optimizer.git
cd meta-skill-optimizer
cp subject.example.json subject.local.json
# 填入所有会影响 Agent 行为的 Skill、Preference、Prompt 和 Context 来源。
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
```

审查 Baseline 后，创建一个 Candidate：

```bash
python3 scripts/review_session.py candidate my-review simpler-system
# 只修改 workspace/sessions/my-review/candidates/simpler-system。
python3 scripts/review_session.py seal-candidate my-review simpler-system
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

生成的 Plan 需要由兼容的 Agent Runner 执行。Result 注册、比较、决策记录和 Patch 生成由仓库负责；Result Contract 见 [`protocol/runner.md`](protocol/runner.md)。

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-system
python3 scripts/review_session.py decide my-review --candidate simpler-system \
  --verdict accepted --reason "行为得到改善，并且没有重要回归。"
```

## 当前状态

Meta-Skill Optimizer 目前处于实验阶段。

已经具备：

- 组合式、原子化导入；
- Whole-System Review 协议；
- 不可变 Baseline 与封存 Candidate；
- 有版本的 Cases、Results、Comparisons 和 Decisions；
- 回归关口和可审查 Patch；
- Git 默认排除的私人本地 Workspace。

尚未具备：

- Codex 和 Claude Code 的原生执行 Adapter。

仓库未来只支持 Codex 和 Claude Code。它不会根据 Feedback 自动生成新 Case 或 Candidate；这项判断留给实际使用者和他的 Agent。

## 文档

- [`SKILL.md`](SKILL.md)：Agent 入口与操作路由
- [`protocol/system-review.md`](protocol/system-review.md)：完整系统审查方法
- [`protocol/evaluation.md`](protocol/evaluation.md)：行为评估规则
- [`protocol/runner.md`](protocol/runner.md)：Runner 与 Result Contract
- [`protocol/safety.md`](protocol/safety.md)：隔离、隐私和来源保护

## License

MIT

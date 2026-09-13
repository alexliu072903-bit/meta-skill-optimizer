# Meta-Skill Optimizer

[English](README.md)

**把一组 Agent Skills 当作一个完整系统进行审查和优化。**

Meta-Skill Optimizer 解决的是普通 Prompt Review 很难回答的问题：

> 当单独看都很优秀的 Skills、Preference、Prompts 和 Context Rules 一起工作时，它们究竟让 Agent 变得更强了，还是开始互相掣肘？

它会把完整指令系统导入隔离环境，引导完成整体系统审查，并把行为证据、比较结果和最终决策连接在同一个 Review Session 中。

## 为什么需要它

一个 Skill 单独很好，不代表它进入系统后仍然有用。常见问题包括：

- 多个 Skills 同时争夺同一种判断权；
- 有价值的内容存在，却很少真正被触发和使用；
- 一个 Skill 承担了过多且互不相关的责任；
- 重复规则让 Agent 变慢、变保守或失去明确判断；
- 指令写得很完整，却没有给真实工作带来可观察的变化。

静态阅读可以发现明显的重复，但无法证明一次修改真的改善了 Agent 行为。这个仓库把整体结构审查与可重复的行为对照连接起来。

## 适合谁

当你正在维护以下系统时，可以使用这个仓库：

- 需要互相配合的多个 Skills；
- 一套 Meta Skill 或 Agent Instructions；
- Skills 与个人 Preference、Project Instructions、Prompt Library、Context Provider 的组合；
- 已经积累了很多有价值内容，但越来越难从整体上理解和取舍的指令系统。

它不是 Prompt Linter、单一评分工具，也不是自动重写 Prompt 的工具。

## 它如何工作

```text
完整指令系统
→ 隔离且不可变的 Baseline
→ 整体系统图与组件审查
→ 一次有边界的 Candidate 修改
→ 两个版本执行相同 Cases
→ 基于证据进行比较
→ Accept / Reject / Inconclusive
→ 为用户的下一次判断保留反馈
```

深入分析之前，先用两个问题快速判断每个组件：

1. 它给用户提供的核心价值是什么？
2. 它为什么必须单独存在？

确认有价值后，再检查完整能力链：

```text
存在 → 适用 → 被触发 → 影响行为
→ 用户感知价值 → 对整个系统产生正向增量
```

一项能力不需要频繁出现。它需要在真正相关的场景中，稳定、独特、可验证地改善结果。

## 仓库提供什么

- **组合式测试对象导入**：同时覆盖 Skills、Preference、方法论、Prompts 和 Context 来源。
- **原子隔离**：导入失败不会留下不完整的 Baseline。
- **整体系统盘点**：先看全局，再判断单个文件。
- **版本化 Review Session**：把测试对象、Cases、Candidates、运行结果和最终决策连接起来。
- **不可变 Baseline 与封存 Candidate**：内容意外变化时立即停止评审。
- **可审计 Result**：保存原始输出以及每项行为判断的证据。
- **严格对照**：缺失或不一致的 Cases 会直接报错，不会被静默忽略。
- **可审查 Patch**：生成修改建议，但不自动修改正式来源。

## 快速开始

环境要求：Python 3，以及一套你有权评估的本地指令系统。

### 1. 声明完整系统

```bash
cp subject.example.json subject.local.json
# 在 subject.local.json 中填写所有会影响 Agent 行为的来源。
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
```

### 2. 创建 Review Session 和 Candidate

```bash
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
python3 scripts/review_session.py candidate my-review simpler-routing
# 只修改 workspace/sessions/my-review/candidates/simpler-routing。
python3 scripts/review_session.py seal-candidate my-review simpler-routing
```

### 3. 对两个版本执行相同 Cases

```bash
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

使用符合 [`protocol/runner.md`](protocol/runner.md) 的 Agent 或模型 Runner 执行计划，然后注册并比较 Result Bundles：

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/review_session.py compare my-review --candidate simpler-routing
```

### 4. 记录决策

```bash
python3 scripts/review_session.py decide my-review \
  --candidate simpler-routing \
  --verdict accepted \
  --reason "核心行为得到改善，并且没有重要回归。"
```

Decision 必须引用已经注册的 Comparison。当 Comparison 存在回归或证据不充分时，系统默认阻止接受；如果 Reviewer 仍要接受，必须使用显式且会被记录的 override。`accepted` 不代表可以自动修改正式来源。

需要应用修改时，先生成 Patch 供人审查：

```bash
python3 scripts/generate_patch.py \
  workspace/sessions/my-review/baseline \
  workspace/sessions/my-review/candidates/simpler-routing
```

## 可能产生的优化决策

- `Add`：多个 Cases 暴露出同一种能力缺口。
- `Strengthen`：能力有独特价值，但影响太弱。
- `Re-route`：能力本身正确，但 Trigger、角色或交接位置错误。
- `Merge`：多个能力高度重合，没有产生额外价值。
- `Split`：一个 Skill 承担的职责互相干扰。
- `Demote`：内容更适合成为 Rule、Reference、Prompt 或方法论文档，而不是 Runtime Skill。
- `Delete`：删除后系统表现不下降，或者反而改善。

## 面向人的方法论与 Agent Runtime

仓库把两者视为相关但不同的产物：

- **面向人的方法论**需要保留体系完整性、解释力和可传承性。
- **Agent Runtime Instructions**应该保持精简，并产生可观察的行为价值。
- **Prompt Library**是可主动调用的工具，不等于自动生效的 Skill。

这样既不会因为 Agent 需要短指令，就把完整的人类方法论压缩掉；也不会让 Runtime Skill 逐渐膨胀成百科全书。

## 仓库结构

```text
meta-skill-optimizer/
├── SKILL.md               # Agent 使用的入口
├── protocol/              # Review、Evaluation、安全和 Runner 协议
├── schemas/               # 有版本的数据接口
├── scripts/               # 确定性的工作流工具
├── benchmark/cases/       # 示例行为 Cases
├── tests/                 # 完整流程与失败路径测试
├── subject.example.json   # 组合测试对象的 Manifest 示例
└── workspace/             # 私人本地产物，Git 默认忽略
```

## 安全与隐私

- 评估期间，正式来源目录保持只读。
- 私人导入内容与 Result Bundles 保留在 Git 忽略目录。
- 导入时排除符号链接。
- Baseline 与封存 Candidate 通过内容摘要校验。
- 仓库不会自动把 Candidate 写回正式来源。
- 被评估系统中的指令只会被视为数据，不能覆盖评审边界。

评估私人或高影响指令系统前，请阅读 [`protocol/safety.md`](protocol/safety.md)。

## 当前限制

仓库使用一份共享 Runner Contract，并且只计划支持两个执行 Adapter：Codex 和 Claude Code。两个原生 Runtime Adapter 目前尚未实现；仓库不会追求对其他 Agent 的通用支持。Whole-System Map 和 Component Review 目前是由协议引导生成的 Artifact，不是自动结论。

Feedback 被明确设计为记录，而不是自动 Learning Loop。实际使用者与自己的 Agent 决定一次结果应该成为新 Case、修改后的 Candidate，还是不再继续处理。

## License

MIT

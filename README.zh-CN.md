# Meta-Skill Optimizer

[English](README.md)

一个轻量的 Agent Skill 和本地工具集，用来把一组 Agent Skills 作为一个完整的行为系统进行审查和优化。

一个 Skill 单独看可能非常优秀，但整套系统却可能变得更慢、更僵化或更难做出明确判断。不使用 Meta-Skill Optimizer 时，我们通常依靠直觉修改指令；使用它之后，每次改动都会与不可变 Baseline 隔离，并使用结构证据，以及在可比执行条件成立时使用相同的行为 Cases 进行评估。

这套审查机制会：

- 把 Skills、Preference、Prompts 和 Context Rules 作为一个完整测试对象导入；
- 判断每个组件提供什么用户价值，以及它为什么必须单独存在；
- 把原始系统保存为不可变 Baseline；
- 把每次修改隔离到独立 Candidate；
- 使用相同 Cases 和执行配置对比 Baseline 与 Candidate；
- 保存判断证据、回归情况，以及 `accepted`、`rejected` 或 `inconclusive` 决策。

最终目标不是得到一组写得更漂亮的 Prompts，而是形成一套更简单、更有能力，并且每次取舍都有依据的 Agent 指令系统。

## 使用

把这个仓库作为 Skill 提供给 Codex 或 Claude Code，然后把目录交给 Agent：

```text
帮我审查 /path/to/skills 目录下的 Skill 系统，并优化出一个更好的版本。
```

Agent 在内部完成：

```text
读取完整系统
→ 建立系统图
→ 找出最重要的问题
→ 创建隔离 Candidate
→ 执行必要的前后对照
→ 给出 Candidate、Diff 和证据
```

当 Agent 可以自行完成时，用户不需要准备 Manifest、Cases、JSON Results 或 CLI 命令。正式来源保持不变，用户决定是否以及如何采用 Candidate。

需要维护底层工具或自定义集成时，查看[手动工作流](protocol/manual-workflow.md)。

## 仓库结构

```text
meta-skill-optimizer/
├── SKILL.md
├── protocol/
│   ├── system-review.md
│   ├── agent-workflow.md
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

Agent 主导的结构审查和 Candidate 工作流已经可用。用于完整隔离行为执行的 Codex 与 Claude Code 原生 Adapter 尚未实现。当无法完成可比执行时，Agent 必须把行为影响标记为未经验证，不能声称已经观察到改善。

系统会保存 Feedback，但不会自动把它转化成新 Case 或 Candidate；这项判断留给实际使用者和他的 Agent。

## License

MIT

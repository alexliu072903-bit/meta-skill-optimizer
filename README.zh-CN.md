# Meta-Skill Optimizer

[English](README.md)

Meta-Skill Optimizer 把一组 Agent Skills 作为一个完整的行为系统进行评估和优化。

它解决的不是「每个 Skill 单独看起来是否优秀」，而是：一项能力进入完整系统后，是否仍然可以被触发、产生独特贡献并改善最终结果；以及通过新增、增强、重新路由、合并、拆分、降级或删除能力，能否让整组 Meta Skills 变得更强、更简单。

## v0 边界

v0 采用「证据优先、用户确认」的工作方式：

1. 将完整指令系统复制到 Git 忽略的本地隔离区；
2. 从整体系统角度明确每个文件的位置和作用；
3. 先验证每个组件在目标场景中是否具有净价值；
4. 只分析有效组件之间的冲突和组合关系；
5. 对比不可变 Baseline 与相互隔离的优化 Candidate；
6. 生成可以审查的 patch。

系统不会修改来源 Skill，也不会自动应用 patch、发布私人数据，或把静态文本检查误称为行为改善证据。

Optimizer 明确区分完整的人类方法论与精简的 Agent Runtime 指令。前者评估体系完整性、解释力和可传承性；后者评估能否产生可观察的行为增量。两者应该互相对应，但不应被迫写在同一个文件中。

可复用 Prompt Library 单独分类。Prompt 不会因为放在同一目录就被视为自动生效的 Skill，与 Runtime 内容重复也不构成删除理由。

## 仓库学习闭环

Optimizer 使用与评估测试对象相同的证据原则迭代自身：

```text
真实隔离测试对象
→ 暴露仓库自身限制
→ 对仓库做有边界的修改
→ 测试
→ 使用改进后的仓库继续评估
```

仓库能力不足时，应先修复仓库，而不是通过静默修改私人测试对象绕过问题。

## 核心判断

```text
Capability exists
→ Eligible
→ Activated
→ Influenced behavior
→ Produced observable value
→ Added positive marginal contribution
```

一项能力不需要频繁出现；它只需要在真正相关的场景中产生稳定、独特、可验证的行为增量。整组系统的表现优先于保留每一个 Skill。

评审顺序是：

```text
完整系统图
→ 对用户的核心价值
→ 必须独立存在的理由
→ 必要时再做详细单体审查
→ 有效组件之间的关系
→ 整体组合优化
→ 回归验证
```

## 仓库结构

```text
meta-skill-optimizer/
├── SKILL.md
├── agents/openai.yaml
├── protocol/
├── schemas/
├── subject.example.json
├── scripts/
├── benchmark/
│   ├── cases/
│   ├── expected/
│   └── results/        # ignored
├── tests/fixtures/
└── workspace/          # ignored
```

## 首次使用

当真实运行环境由 Skills、Preference、Project Instructions 或 Context Provider 共同组成时，复制 `subject.example.json`、声明所有相关来源，然后导入组合后的测试对象：

```bash
cp subject.example.json subject.local.json
# 在 subject.local.json 中填写本地来源路径。
python3 scripts/validate_data.py subject.local.json schemas/subject.schema.json
python3 scripts/import_manifest.py subject.local.json
python3 scripts/inventory.py workspace/baseline > workspace/inventory.json
```

需要完成可审计的端到端评审时，使用有版本的 Review Session，不要手动维护散落的 Workspace 文件：

```bash
python3 scripts/review_session.py init my-review \
  --manifest subject.local.json \
  --cases benchmark/cases
python3 scripts/review_session.py candidate my-review candidate-one
# 只修改 workspace/sessions/my-review/candidates/candidate-one。
python3 scripts/review_session.py seal-candidate my-review candidate-one
python3 scripts/review_session.py plan my-review > workspace/run-plan.json
```

按照 `protocol/runner.md` 执行计划，注册有版本的结果、严格比较并记录决定：

```bash
python3 scripts/review_session.py register-run my-review baseline-result.json
python3 scripts/review_session.py register-run my-review candidate-result.json
python3 scripts/compare_results.py baseline-result.json candidate-result.json
python3 scripts/review_session.py decide my-review \
  --candidate candidate-one \
  --verdict accepted \
  --reason "核心行为改善且没有重要回归。"
```

如果同一个 canonical 目录中的文件承担不同运行角色，可以为每个来源配置 `include` 和 `exclude` glob。

在 Manifest 声明的 `runtime-skills` 来源中，只要 Markdown 包含有效的 `name` 和 `description` Frontmatter，即使使用 `process.md` 这样的扁平化人类可读文件名，也会被正确识别为 Skill。

如果测试对象只有一个目录，可以使用简化导入方式：

```bash
python3 scripts/import_subject.py /path/to/source
python3 scripts/inventory.py workspace/baseline > workspace/inventory.json
python3 scripts/validate_data.py benchmark/cases schemas/case.schema.json
```

Baseline 导入完成后，为每次实验创建独立 Candidate：

```bash
python3 scripts/new_candidate.py routing-cleanup
```

按照 `protocol/evaluation.md` 生成 Baseline 和 Candidate 的结果文件后，执行对照比较并生成 patch：

```bash
python3 scripts/compare_results.py baseline.json candidate.json
python3 scripts/generate_patch.py workspace/baseline workspace/candidates/routing-cleanup
```

## 优化动作

- `Add`：多个 Case 暴露同一能力缺口；
- `Strengthen`：能力有独特价值，但影响过弱；
- `Re-route`：能力正确，但 Trigger、角色或交接位置错误；
- `Merge`：能力高度重叠，组合没有额外价值；
- `Split`：一个 Skill 承担了互相干扰的职责；
- `Demote`：内容更适合成为 Rule、Reference 或局部原则；
- `Delete`：删除后系统表现不下降，或反而改善。

## 安全边界

在导入私人内容或应用任何建议前，必须先阅读 `protocol/safety.md`。

- 正式 Skill 目录只作为来源，不在测试中修改；
- `workspace/baseline` 导入后保持不变；
- 所有实验发生在独立 Candidate 中；
- `workspace/` 和 `benchmark/results/` 默认不进入 Git；
- 系统只生成 patch，未经用户明确授权不回写正式版本。
- 导入时会排除符号链接，并在 Git 忽略的 `subject.lock.json` 中记录来源类型和文件哈希。

## 当前限制

v0 提供原子隔离导入、能力盘点、Review Session 状态、Candidate sealing、Runner Plan、可审计结果注册、严格比较、决定记录和 patch 生成。仓库定义了与模型供应商无关的 Runner Contract，但暂不提供统一的跨模型执行 Adapter，也不会自动修改正式 Skills。

## License

MIT

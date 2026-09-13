# Meta-Skill Optimizer

[English](README.md)

Meta-Skill Optimizer 把一组 Agent Skills 作为一个完整的行为系统进行评估和优化。

它解决的不是「每个 Skill 单独看起来是否优秀」，而是：一项能力进入完整系统后，是否仍然可以被触发、产生独特贡献并改善最终结果；以及通过新增、增强、重新路由、合并、拆分、降级或删除能力，能否让整组 Meta Skills 变得更强、更简单。

## v0 边界

v0 采用「证据优先、用户确认」的工作方式：

1. 将待评估的 Skill 系统复制到 Git 忽略的本地隔离区；
2. 盘点其中声明的能力、角色和依赖关系；
3. 定义能够代表真实工作的行为 Case；
4. 对比不可变 Baseline 与相互隔离的 Candidate；
5. 根据行为证据提出有边界的优化建议；
6. 生成可以审查的 patch。

系统不会修改来源 Skill，也不会自动应用 patch、发布私人数据，或把静态文本检查误称为行为改善证据。

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

## 仓库结构

```text
meta-skill-optimizer/
├── SKILL.md
├── agents/openai.yaml
├── protocol/
├── schemas/
├── scripts/
├── benchmark/
│   ├── cases/
│   ├── expected/
│   └── results/        # ignored
├── tests/fixtures/
└── workspace/          # ignored
```

## 首次使用

只将待评估系统的副本导入隔离区：

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

## 当前限制

v0 提供隔离导入、能力盘点、数据校验、Candidate 管理、结果比较和 patch 生成。真实模型行为评测由 `SKILL.md` 按 Evaluation Protocol 执行；仓库暂不假设存在统一的跨模型 Runtime，也不提供自动修改正式 Skills 的能力。

## License

MIT


# Design Advisor V2

5 阶段设计流程，帮助用户从需求到实现规划完成完整的 Claude Code 组件设计。

## 架构

```
/design-advisor
    ├──▶ Stage 1: requirement-core
    ├──▶ Stage 2: architect-core
    ├──▶ Stage 3: design-core
    ├──▶ Stage 4: validator-core
    └──▶ Stage 5: planner-core
```

## 文件结构

```
advisor/
├── README.md
├── requirement-core/SKILL.md
├── architect-core/SKILL.md
├── design-core/SKILL.md
├── validator-core/SKILL.md
├── planner-core/SKILL.md
├── knowledge/design-patterns/
│   ├── handbook-references.json
│   ├── stage-1-requirement.json
│   ├── stage-2-architecture.json
│   ├── stage-3-detailed-design.json
│   ├── stage-4-validation.json
│   └── stage-5-implementation.json
└── tests/
```

## 使用

```bash
/design-advisor 创建代码审查工具
/design-advisor 已有需求 --stage=2
```

## 阶段说明

| 阶段 | 名称 | Subagent | 输入 | 输出 |
|------|------|----------|------|------|
| 1 | 需求理解 | requirement-core | 用户描述 | 需求规格 |
| 2 | 架构选型 | architect-core | 需求规格 | 架构决策 |
| 3 | 详细设计 | design-core | 架构决策 | 设计规格 |
| 4 | 规范验证 | validator-core | 设计规格 | 合规报告 |
| 5 | 实现规划 | planner-core | 验证设计 | 实施计划 |

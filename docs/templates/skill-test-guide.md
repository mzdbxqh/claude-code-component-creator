# [技能名称] 测试指南

## 为什么要写测试？

1. **验证功能**：确保技能按预期工作
2. **回归保护**：修改后快速验证未破坏功能
3. **文档作用**：测试用例展示技能使用方法

## 快速开始

### 运行所有测试

```bash
/[技能命令]:test-sandbox
```

### 运行单个测试

```bash
/[技能命令]:test-sandbox --test-case=TC-001
```

### 干运行验证

```bash
/[技能命令]:test-sandbox --dry-run
```

## 测试类型

| 类型 | 用途 | 文件 |
|------|------|------|
| 功能测试 | 验证核心功能 | `tests/unit/test-xxx.md` |
| 边界测试 | 验证边界情况 | `tests/unit/test-boundary.md` |
| 集成测试 | 验证与其他技能配合 | `tests/integration/test-flow.md` |

## 测试结构

```
skills/[技能名称]/
├── SKILL.md
├── evals/
│   └── evals.json          # 测试用例定义
└── tests/
    ├── unit/               # 单元测试
    ├── integration/        # 集成测试
    └── fixtures/           # 测试夹具
```

## 编写测试用例

### 功能测试示例

```json
{
  "id": "TC-001",
  "name": "查找 TODO 注释",
  "prompt": "查找当前目录的 TODO 注释",
  "expectedOutput": "Markdown 列表，包含文件路径和行号"
}
```

### 边界测试示例

```json
{
  "id": "TC-002",
  "name": "空目录测试",
  "prompt": "查找空目录的 TODO 注释",
  "expectedOutput": "友好的提示信息"
}
```

## 测试覆盖率

当前覆盖率：X%

- 功能测试：X 个用例
- 边界测试：X 个用例
- 集成测试：X 个用例

## 常见问题

### Q: 测试失败了怎么办？

1. 查看失败详情
2. 检查是否是预期行为变更
3. 更新测试用例或修复代码

### Q: 如何添加新测试？

1. 复制现有测试用例结构
2. 修改 prompt 和 expectedOutput
3. 运行测试验证

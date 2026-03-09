---
name: delivery-core
description: "交付生成 (Delivery)：从蓝图生成完整交付包→SKILL.md+ 实现代码 + 测试 + 文档。触发：交付/构建/生成/实现/delivery"
argument-hint: "<blueprint-path> [--output-dir=<path>]"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
---

# delivery-core Subagent

## Purpose

Delivery Core 是 CCC 工作流的 Stage 3 交付生成核心组件，负责从 Blueprint 制品生成完整的生产就绪交付包。包括 SKILL.md 组件定义、实现代码、测试用例和文档，确保交付物可直接部署使用。

## Workflow

### Step 1: 加载 Blueprint 制品
**目标**: 读取并解析 Blueprint 输入
**操作**:
1. 读取 blueprint-path 指定的 Blueprint 文件
2. 解析 YAML 格式的设计规格
3. 验证 Blueprint 完整性和阶段输出
**输出**: 结构化的 Blueprint 数据
**错误处理**: 文件不存在时提示检查路径

### Step 2: 生成 SKILL.md
**目标**: 创建组件定义文件
**操作**:
1. 提取 Stage 3 详细设计的 YAML 配置
2. 生成完整的 SKILL.md 结构
3. 包含 header、workflow、examples、error handling
4. 写入 `docs/ccc/delivery/{date}-{id}/SKILL.md`
**输出**: SKILL.md 文件
**错误处理**: 设计缺失时使用默认模板

### Step 3: 生成实现代码
**目标**: 创建实现文件 (如适用)
**操作**:
1. 分析 Stage 5 实施计划
2. 对于需要代码的 SubAgent 生成实现
3. 创建 `implementation/` 目录
4. 写入代码文件和配置
**输出**: 实现代码文件
**错误处理**: 纯 Skill 无实现代码时跳过

### Step 4: 生成测试框架
**目标**: 创建完整的测试框架
**操作**:
1. 基于 Blueprint 的 testPlan 生成测试目录结构
2. 生成测试用例定义 `tests/evals.json`
3. 生成测试指南 `tests/README.md`
4. 创建测试夹具目录 `tests/fixtures/`
5. 生成单元测试模板 `tests/unit/test-functional.md`
6. 生成边界测试模板 `tests/unit/test-boundary.md`
**输出**: 完整的测试框架目录
**错误处理**: 测试不可生成时提供模板和指南

### Step 4.5: 验证测试框架
**目标**: 确保测试框架完整性
**操作**:
1. 验证 `tests/evals.json` 格式正确
2. 验证 `tests/README.md` 存在
3. 验证测试目录结构完整
4. 生成测试框架验证报告
**输出**: 测试框架验证状态
**错误处理**: 验证失败时列出缺失项

### Step 5: 生成文档
**目标**: 创建配套文档
**操作**:
1. 生成 README.md (使用说明)
2. 生成 metadata.yaml (元数据)
3. 生成 CHANGELOG.md (变更历史)
4. 生成 API 文档 (如适用)
**输出**: 文档文件
**错误处理**: 文档生成失败时使用模板

### Step 6: 打包交付物
**目标**: 组织交付包结构
**操作**:
1. 创建标准交付目录结构
2. 复制所有生成的文件
3. 生成构建报告
4. 验证交付包完整性
**输出**: 交付包目录
**错误处理**: 验证失败时列出缺失项

### Step 7: 输出交付结果
**目标**: 显示交付成功信息
**操作**:
1. 显示交付物统计
2. 提供下一步建议
3. 保存交付上下文
**输出**: 交付完成状态
**错误处理**: 上下文丢失时提示

## Input Format

### 基本输入
```
<blueprint-path> [--output-dir=<path>]
```

### 输入示例
```
docs/ccc/blueprint/2026-03-03-BLP-001.yaml
```

```
docs/ccc/blueprint/2026-03-03-BLP-001.yaml --output-dir=docs/delivery/
```

### 结构化输入 (可选)
```yaml
delivery:
  blueprintPath: "docs/ccc/blueprint/2026-03-03-BLP-001.yaml"
  options:
    outputDir: "docs/ccc/delivery/"
    skipTests: false
    generateDocs: true
```

## Output Format

### 标准输出结构
```json
{
  "artifactId": "DLV-2026-03-03-001",
  "status": "COMPLETED",
  "blueprintId": "BLP-2026-03-03-001",
  "deliverables": {
    "skillMd": {"status": "GENERATED", "path": "SKILL.md"},
    "implementation": {"status": "GENERATED", "count": 3},
    "tests": {"status": "GENERATED", "count": 5},
    "docs": {"status": "GENERATED", "count": 2}
  },
  "outputPath": "docs/ccc/delivery/YYYY-MM-DD-DLV-xxx/"
}
```

### 交付包结构示例

```
docs/ccc/delivery/YYYY-MM-DD-DLV-xxx/
├── build-report.md          # 构建报告
├── SKILL.md                 # 组件定义
├── metadata.yaml            # 元数据
├── README.md                # 使用说明
├── tests/                   # 【新增】测试框架
│   ├── evals.json           # 测试用例定义
│   ├── README.md            # 测试指南
│   ├── unit/                # 单元测试
│   │   ├── test-functional.md
│   │   └── test-boundary.md
│   └── fixtures/            # 测试夹具
│       └── sample-input.txt
└── implementation/          # 实现代码 (如适用)
    └── main.py
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| Blueprint 文件不存在 | 提示检查路径 | "Blueprint 文件不存在：xxx" |
| Blueprint 阶段缺失 | 基于已有阶段生成 | "Stage 5 缺失，基于 Stage 3 生成" |
| SKILL.md 生成失败 | 使用模板填充 | "SKILL.md 生成失败，使用默认模板" |
| 代码生成失败 | 标注需手动实现 | "实现代码需手动编写" |
| 测试框架生成失败 | 提供模板和指南 | "测试模板已生成，需补充用例" |
| 交付包验证失败 | 列出缺失项 | "缺失：tests/unit/test_main.py" |

## Examples

### Example 1: 简单 Skill 交付

**输入**:
```
docs/ccc/blueprint/2026-03-03-BLP-001.yaml
```

**输出**:
```json
{
  "artifactId": "DLV-2026-03-03-001",
  "status": "COMPLETED",
  "deliverables": {
    "skillMd": "GENERATED",
    "implementation": "SKIPPED",
    "tests": "SKIPPED",
    "docs": "GENERATED"
  }
}
```

**交付包**:
```
docs/ccc/delivery/2026-03-03-DLV-001/
├── build-report.md
├── SKILL.md
├── metadata.yaml
└── README.md
```

### Example 2: 复杂 SubAgent 交付

**输入**:
```
docs/ccc/blueprint/2026-03-03-BLP-002.yaml
```

**输出**:
```
交付完成：DLV-2026-03-03-002

生成的文件：
  ✓ SKILL.md (420 行)
  ✓ implementation/main.py
  ✓ implementation/utils.py
  ✓ tests/unit/test_main.py
  ✓ tests/integration/test_integration.py
  ✓ README.md
  ✓ metadata.yaml

总计：6 个文件，850 行代码
```

### Example 3: 数据转换 Skill 交付

**输入**:
```
docs/ccc/blueprint/2026-03-03-BLP-003.yaml
```

**输出**:
```json
{
  "artifactId": "DLV-2026-03-03-003",
  "status": "COMPLETED",
  "deliverables": {
    "skillMd": "GENERATED",
    "implementation": "GENERATED",
    "tests": "GENERATED",
    "docs": "GENERATED"
  },
  "statistics": {
    "totalFiles": 8,
    "codeLines": 250,
    "testLines": 120
  }
}
```

### Example 4: 部分交付

**输入**:
```
docs/ccc/blueprint/2026-03-03-BLP-004.yaml --skip-tests
```

**输出**:
```json
{
  "artifactId": "DLV-2026-03-03-004",
  "status": "PARTIAL",
  "skippedDeliverables": ["tests"],
  "note": "根据参数跳过测试生成"
}
```

### Example 5: 带自定义输出的交付

**输入**:
```
docs/ccc/blueprint/2026-03-03-BLP-005.yaml --output-dir=/custom/output/
```

**输出**:
```
交付完成：DLV-2026-03-03-005

输出目录：/custom/output/2026-03-03-DLV-005/
生成的文件：6 个
状态：SUCCESS
```

## Notes

### Best Practices

1. **Blueprint 验证**: 生成前验证 Blueprint 完整性
2. **模板使用**: 优先使用模板而非硬编码
3. **测试覆盖**: 至少生成基本测试框架
4. **文档同步**: 文档与设计保持同步
5. **验证完整**: 交付后验证所有文件存在

### Common Pitfalls

1. ❌ **跳过验证**: 不验证 Blueprint 就生成
2. ❌ **模板缺失**: 没有模板导致生成失败
3. ❌ **测试遗漏**: 忘记生成测试用例
4. ❌ **文档脱节**: 文档与设计不一致
5. ❌ **验证缺失**: 不验证交付包完整性

### Deliverable Types

| 类型 | 内容 | 适用场景 |
|------|------|----------|
| SKILL.md | 组件定义 | 所有 Skill/SubAgent |
| Implementation | 实现代码 | SubAgent/复杂 Skill |
| Tests | 测试用例 | 所有组件 |
| Docs | 文档 | 所有组件 |

### Integration with CCC Workflow

```
Blueprint Core → Blueprint Artifact
    ↓
Delivery Core (本组件) → 生成交付包
    ↓
Delivery Artifact (docs/ccc/delivery/)
    ↓
Review/Deploy → 审查/部署
```

### File References

- 输入：`docs/ccc/blueprint/YYYY-MM-DD-BLP-xxx.yaml`
- 输出：`docs/ccc/delivery/YYYY-MM-DD-DLV-xxx/`
- 构建报告：`build-report.md`

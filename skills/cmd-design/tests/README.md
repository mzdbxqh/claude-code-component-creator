# cmd-design 测试指南

本目录包含 cmd-design Skill 的测试用例和测试夹具。

## 测试结构

```
tests/
├── README.md                # 本文件
├── test-cases.yaml          # 测试用例定义
└── fixtures/                # 测试夹具（示例数据）
    ├── int-001-simple.yaml
    ├── int-002-complex.yaml
    └── expected-outputs/
```

## 运行测试

### 方式1: 使用CCC Eval机制

```bash
# 进入skill目录
cd skills/cmd-design

# 运行所有测试
/ccc:test-sandbox --target=. --with-eval

# 运行特定测试
/ccc:test-sandbox --target=. --eval-name=basic_design_generation
```

### 方式2: 手动测试

```bash
# 测试基础设计生成
/ccc:design --artifact-id=INT-001

# 验证输出
ls docs/designs/
ls docs/ccc/blueprint/
```

## 测试用例

| 测试名称 | 描述 | 优先级 | 预期结果 |
|---------|------|--------|----------|
| basic_design_generation | 基础设计流程 | critical | 生成完整Blueprint |
| complex_design_handling | 复杂多组件设计 | high | 生成多Agent架构 |
| design_with_constraints | 约束条件设计 | high | 满足安全/性能要求 |
| iterative_design | 迭代优化设计 | medium | 生成改进方案 |

## 测试夹具

### INT-001: 简单工具

```yaml
# evals/test-fixtures/int-001-simple-tool.yaml
version: "3.0"
id: "INT-001"
type: "intent"

metadata:
  name: "code-formatter"
  description: "代码格式化工具"
  component_type: "skill"
  complexity: "simple"

requirements:
  functional:
    - "读取代码文件"
    - "应用格式化规则"
    - "输出格式化结果"

constraints:
  hard:
    - "不修改原文件"
    - "支持多种语言"
```

### 预期输出验证

测试执行后，应生成以下文件：
- `docs/designs/YYYY-MM-DD-code-formatter-design.md`
- `docs/ccc/blueprint/YYYY-MM-DD-BLP-XXX.yaml`

文件应包含：
- [x] 工作流设计章节
- [x] 组件结构说明
- [x] 能力表定义
- [x] 实施计划

## 测试通过标准

### 必要条件
- [x] 所有critical测试通过
- [x] 生成的文件格式正确
- [x] YAML可以解析
- [x] 包含所有必需字段

### 质量标准
- [x] 设计文档清晰易懂
- [x] Blueprint结构完整
- [x] Token预算合理（<4000）
- [x] 工作流逻辑连贯

## 故障排除

### 问题1: 测试夹具未找到

**症状**: `Error: Intent file not found: test-fixtures/int-001-simple-tool.yaml`

**解决**:
```bash
# 检查文件是否存在
ls evals/test-fixtures/

# 创建缺失的夹具文件
cp examples/intent-template.yaml evals/test-fixtures/int-001-simple-tool.yaml
```

### 问题2: Blueprint生成失败

**症状**: `Error: Failed to generate blueprint`

**解决**:
1. 检查Intent制品格式是否正确
2. 验证所有必需字段是否存在
3. 查看日志: `~/.claude/logs/`

### 问题3: 测试超时

**症状**: `Timeout after 120 seconds`

**解决**:
- 调整timeout配置: `evals/evals.json` → `timeout: 180`
- 检查网络连接
- 确认API配额充足

## 贡献测试用例

添加新测试用例的步骤：

1. **定义测试**: 在 `evals/evals.json` 中添加新测试条目
2. **创建夹具**: 在 `evals/test-fixtures/` 中添加测试数据
3. **验证测试**: 运行测试确保通过
4. **更新文档**: 在本README中记录测试

## 参考资料

- [CCC测试框架文档](../../docs/testing-guide.md)
- [Eval机制说明](../../docs/eval-mechanism.md)
- [测试最佳实践](../../docs/testing-best-practices.md)

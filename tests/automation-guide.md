# CCC 插件测试自动化指南

> **Test Automation Guide for Component Creator Creator (CCC) Plugin**

**版本**: 1.0.0
**最后更新**: 2026-03-07
**维护者**: CCC Team

---

## 目录

1. [CI/CD 集成建议](#cicd-集成建议)
2. [自动化测试触发条件](#自动化测试触发条件)
3. [测试报告自动生成](#测试报告自动生成)
4. [回归测试策略](#回归测试策略)
5. [本地测试开发](#本地测试开发)

---

## CI/CD 集成建议

### GitHub Actions 配置

创建 `.github/workflows/test.yml`:

```yaml
name: CCC Plugin Test

on:
  push:
    paths:
      - 'agents/**/*.md'
      - 'commands/**/*.md'
      - 'tests/**/*.md'
      - 'evals/**/*.json'
  pull_request:
    paths:
      - 'agents/**/*.md'
      - 'commands/**/*.md'
      - 'tests/**/*.md'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Validate JSON
        run: |
          python3 -c "import json; json.load(open('evals/evals.json'))"
          echo "✅ evals.json 格式正确"

      - name: Run Unit Tests
        run: |
          echo "运行单元测试..."
          # 添加具体的测试执行命令

      - name: Run Integration Tests
        run: |
          echo "运行集成测试..."
          # 添加具体的测试执行命令

      - name: Generate Coverage Report
        run: |
          echo "生成覆盖率报告..."
          # 添加覆盖率生成命令

      - name: Upload Test Report
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: docs/tests/
```

### GitLab CI 配置

创建 `.gitlab-ci.yml`:

```yaml
stages:
  - validate
  - test
  - report

validate:
  stage: validate
  script:
    - python3 -c "import json; json.load(open('evals/evals.json'))"
    - echo "✅ JSON 验证通过"

test:
  stage: test
  script:
    - echo "运行测试..."
    # 添加测试命令

report:
  stage: report
  script:
    - echo "生成报告..."
  artifacts:
    reports:
      - docs/tests/*.md
```

---

## 自动化测试触发条件

### 文件变更触发

| 变更文件 | 触发的测试 |
|----------|------------|
| `agents/intent-core/**` | intent-core 测试 |
| `agents/blueprint-core/**` | blueprint-core 测试 |
| `agents/delivery-core/**` | delivery-core 测试 |
| `agents/test-sandbox-core/**` | test-sandbox-core 测试 |
| `tests/integration/**` | 集成测试 |
| `evals/evals.json` | 全量测试 |
| `commands/**` | 命令测试 |

### 事件触发

| 事件 | 触发的测试 |
|------|------------|
| Push 到 main | 全量测试 |
| Pull Request | 变更相关测试 |
| 每日定时 | 全量测试 + 性能测试 |
| 发布前 | 全量测试 + 回归测试 |

### 手动触发

```bash
# 运行所有测试
/cmd-test-sandbox

# 运行特定组件测试
/cmd-test-sandbox --target=agents/intent-core

# 运行特定测试用例
/cmd-test-sandbox --test-case=TC-E2E-001

# 干运行（不实际执行）
/cmd-test-sandbox --dry-run
```

---

## 测试报告自动生成

### 报告生成命令

```bash
# 生成完整测试报告
/cmd-test-sandbox --report --output=docs/tests/test-report.md

# 生成覆盖率报告
/cmd-test-sandbox --coverage --output=docs/tests/coverage-report.md

# 生成 JUnit 格式报告
/cmd-test-sandbox --junit --output=docs/tests/junit-report.xml
```

### 报告模板

**控制台输出**:
```
🧪 CCC 插件测试报告
═══════════════════════════════════════════════════

测试环境：docs/ccc/sandbox-test-20260307-143022/
测试用例：75
开始时间：2026-03-07 14:30:22
结束时间：2026-03-07 14:45:18
总耗时：14 分 56 秒

执行摘要:
┌───────────────────────────────────────────────────┐
│ Total: 75  |  Passed: 72  |  Warn: 3  |  Failed: 0│
│ Pass Rate: 100% (warning 不计入失败)               │
│ Coverage: 88%                                     │
└───────────────────────────────────────────────────┘

详细报告：docs/tests/test-report.md
覆盖率报告：docs/tests/coverage-report.md
```

**Markdown 报告**:
```markdown
# CCC 插件测试报告

**测试时间**: 2026-03-07 14:30:22
**测试环境**: docs/ccc/sandbox-test-20260307-143022/

## 执行摘要

| 总计 | 通过 | 警告 | 失败 | 通过率 |
|------|------|------|------|--------|
| 75   | 72   | 3    | 0    | 100%   |

## 按组件统计

| 组件 | 通过 | 失败 | 跳过 |
|------|------|------|------|
| ccc:intent-core | 10 | 0 | 0 |
| ccc:blueprint-core | 14 | 0 | 0 |
| ccc:delivery-core | 14 | 0 | 0 |
| ccc:test-sandbox-core | 14 | 0 | 0 |
| integration | 21 | 0 | 0 |
| commands | 2 | 0 | 0 |

## 失败详情

无失败用例。

## 警告详情

| 用例 ID | 名称 | 警告原因 |
|---------|------|----------|
| TC-XXX | XXX | 输出格式略有差异 |
```

---

## 回归测试策略

### 回归测试范围

| 变更类型 | 回归测试范围 |
|----------|--------------|
| 核心 Agent 修改 | 全量测试 |
| 命令修改 | 命令测试 + 集成测试 |
| 测试框架修改 | 全量测试 |
| 文档修改 | 无（跳过测试） |

### 回归测试触发

```bash
# 检测变更文件
CHANGED_FILES=$(git diff --name-only HEAD~1)

# 根据变更决定测试范围
if echo "$CHANGED_FILES" | grep -q "agents/.*-core/"; then
  echo "核心 Agent 变更，运行全量测试"
  /cmd-test-sandbox --full
elif echo "$CHANGED_FILES" | grep -q "commands/"; then
  echo "命令变更，运行命令测试 + 集成测试"
  /cmd-test-sandbox --target=commands --integration
else
  echo "其他变更，运行相关测试"
  /cmd-test-sandbox --changed
fi
```

### 回归测试阈值

| 指标 | 阈值 | 动作 |
|------|------|------|
| 通过率 | < 100% | 阻塞合并 |
| 覆盖率 | < 85% | 警告 |
| 执行时间 | > 15 分钟 | 优化建议 |

---

## 本地测试开发

### 开发环境设置

```bash
# 1. 克隆仓库
git clone <repository>
cd claude-code-component-creator

# 2. 安装依赖（如需要）
pip install -r requirements.txt

# 3. 验证环境
python3 -c "import json; json.load(open('evals/evals.json'))" && echo "✅ 环境正常"
```

### 运行本地测试

```bash
# 运行单个测试文件
/cmd-test-sandbox --test-case=TC-INTENT-001

# 运行组件所有测试
/cmd-test-sandbox --target=agents/intent-core

# 运行集成测试
/cmd-test-sandbox --integration

# 快速验证（干运行）
/cmd-test-sandbox --dry-run
```

### 调试测试

```bash
# 详细模式
/cmd-test-sandbox --test-case=TC-XXX --verbose

# 调试特定阶段
/cmd-test-sandbox --debug --stage=intent

# 查看测试日志
cat docs/ccc/sandbox-test-*/logs/test.log
```

### 添加新测试

1. **选择测试文件位置**:
   - Agent 测试：`agents/{agent}/tests/`
   - 集成测试：`tests/integration/`

2. **复制测试模板**:
   ```bash
   cp docs/templates/test-case-template.md agents/intent-core/tests/test-xxx.md
   ```

3. **编辑测试用例**:
   - 定义测试目的
   - 编写测试步骤
   - 定义预期结果
   - 添加验证命令

4. **运行测试验证**:
   ```bash
   /cmd-test-sandbox --test-case=TC-XXX
   ```

5. **提交测试**:
   ```bash
   git add agents/intent-core/tests/test-xxx.md
   git commit -m "test(intent-core): 添加 XXX 测试"
   ```

---

## 附录：测试命令速查

```bash
# 全量测试
/cmd-test-sandbox

# 组件测试
/cmd-test-sandbox --target=agents/intent-core

# 集成测试
/cmd-test-sandbox --integration

# 特定测试
/cmd-test-sandbox --test-case=TC-XXX

# 干运行
/cmd-test-sandbox --dry-run

# 详细模式
/cmd-test-sandbox --verbose

# 生成报告
/cmd-test-sandbox --report --output=docs/tests/report.md

# 生成覆盖率
/cmd-test-sandbox --coverage

# 生成 JUnit 报告
/cmd-test-sandbox --junit --output=report.xml
```

---

## 相关文件

- [测试指南](tests/README.md) - 总体测试指南
- [覆盖率报告](tests/coverage-report.md) - 测试覆盖率统计
- [evals.json](evals/evals.json) - 测试用例定义

---

**维护者**: CCC Team
**最后更新**: 2026-03-07

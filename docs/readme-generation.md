# README 自动生成机制

## 概述

为了避免手动更新 README 时的遗漏和中英文不同步问题，CCC 提供了基于模板和实际数据源的自动生成机制。

## 问题

手动更新 README 存在以下问题：
1. ❌ **版本号不一致**：容易忘记更新徽章、配置文件等处的版本号
2. ❌ **中英文不同步**：README.md 和 README_zh.md 容易内容不一致
3. ❌ **命令列表遗漏**：新增命令后容易忘记更新命令表格
4. ❌ **质量评分过时**：忘记更新最新的质量评分
5. ❌ **人工错误**：格式不一致、拼写错误等

## 解决方案

### 架构

```
数据来源（Single Source of Truth）
├── .claude-plugin/plugin.json       → 版本号、元数据
├── .claude-plugin/marketplace.json  → 插件描述
├── CHANGELOG.md                     → 质量评分、特性列表
└── skills/cmd-*/SKILL.md            → 命令列表、描述

              ↓

生成脚本（scripts/generate-readme.py）
├── 提取版本信息
├── 提取质量评分
├── 扫描命令列表
└── 提取特性列表

              ↓

模板（docs/templates/）
├── README-template.md       → 英文模板
└── README-template-zh.md    → 中文模板

              ↓

生成输出
├── README.md       ← 自动生成（英文）
└── README_zh.md    ← 自动生成（中文，自动同步）
```

## 使用方法

### 基本使用

```bash
# 在插件根目录运行
python3 scripts/generate-readme.py

# 输出示例：
# 开始生成 README 文件...
#   [1/5] 提取版本信息...
#   [2/5] 提取质量评分...
#   [3/5] 扫描命令列表...
#   [4/5] 提取特性列表...
#   [5/5] 渲染模板...
#   ✓ 已生成: /path/to/README.md
#   ✓ 已生成: /path/to/README_zh.md
#
# 生成完成！
#   版本号: 3.1.3
#   质量评分: 96/100
#   命令数量: 18
#   特性数量: 5
```

### 验证生成结果

```bash
# 查看变更
git diff README.md README_zh.md

# 检查版本号是否正确
grep "badge/version" README.md README_zh.md

# 检查命令列表是否完整
grep "/cmd-" README.md | wc -l
```

### 集成到发布流程

在 `docs/github-release-workflow.md` 的"步骤 2.2"中运行：

```bash
# 1. 更新 CHANGELOG.md（手动）

# 2. 更新 plugin.json 和 marketplace.json 版本号（手动）

# 3. 运行 README 生成脚本（自动）
python3 scripts/generate-readme.py

# 4. 验证生成结果
git diff README.md README_zh.md

# 5. 提交
git add README.md README_zh.md
git commit -m "[doc]自动生成README到vX.Y.Z"
```

## 数据来源详解

### 1. 版本号（plugin.json）

```json
{
  "version": "3.1.3",  ← 提取此字段
  "description": "...",
  "author": {...}
}
```

生成到模板中的 `{version}` 变量。

### 2. 质量评分（CHANGELOG.md）

从最新版本条目中提取：

```markdown
## [3.1.3] - 2026-03-13

### 🎉 Quality Review Completion - A+ Grade (96/100)

**Overall Score**: 96/100

| Dimension | Score |
|-----------|-------|
| Security  | 98/100|
| ...       | ...   |
```

提取：
- `{quality_score}` = 96
- `{score_security}` = 98
- 其他维度评分

### 3. 命令列表（skills/cmd-*/）

扫描 `skills/cmd-*/SKILL.md`，提取：

```yaml
---
description: "主工作流第1步。4问框架分析需求..."
---
```

生成命令表格：

```markdown
| Command | Description |
|---------|-------------|
| `/cmd-init` | 主工作流第1步。4问框架... |
| `/cmd-design` | 主工作流第2步。5阶段... |
```

### 4. 特性列表（CHANGELOG.md）

从最新版本的 "Added" 部分提取：

```markdown
### Added
- 循环依赖防护 (LOOP-001)
- Token预算透明化 (SCALE-001)
- 并行处理支持 (SCALE-002)
```

生成特性列表。

## 模板自定义

### 编辑模板

```bash
# 编辑英文模板
vim docs/templates/README-template.md

# 编辑中文模板
vim docs/templates/README-template-zh.md
```

### 模板变量

可用变量：

| 变量 | 数据来源 | 示例值 |
|------|---------|--------|
| `{version}` | plugin.json | 3.1.3 |
| `{quality_score}` | CHANGELOG.md | 96 |
| `{author}` | plugin.json | mzdbxqh |
| `{repository}` | plugin.json | https://github.com/... |
| `{homepage}` | plugin.json | https://github.com/... |
| `{license}` | plugin.json | MIT |
| `{current_year}` | 系统时间 | 2026 |
| `{commands_table_en}` | skills/ 扫描 | 命令表格（英文） |
| `{commands_table_zh}` | skills/ 扫描 | 命令表格（中文） |
| `{features_list_en}` | CHANGELOG.md | 特性列表（英文） |
| `{features_list_zh}` | CHANGELOG.md | 特性列表（中文） |

### 添加新变量

在 `scripts/generate-readme.py` 中：

```python
# 添加数据提取
data['new_variable'] = extract_new_data()

# 在模板中使用
{new_variable}
```

## 脚本实现

### 核心类

```python
class READMEGenerator:
    def extract_version_info(self) -> Dict
    def extract_quality_score(self) -> Dict
    def scan_commands(self) -> List[Dict]
    def extract_features(self) -> List[Dict]
    def render_template(self, template: str, data: Dict) -> str
    def generate(self)
```

### 数据流

```
1. 收集数据
   ├── extract_version_info()    → version, author, license...
   ├── extract_quality_score()   → overall, dimensions
   ├── scan_commands()           → command list with descriptions
   └── extract_features()        → feature list from CHANGELOG

2. 准备数据字典
   └── 合并所有提取的数据到统一字典

3. 加载模板
   ├── README-template.md
   └── README-template-zh.md

4. 渲染模板
   └── 变量替换 {variable} → value

5. 写入文件
   ├── README.md
   └── README_zh.md
```

## 优势

### 1. 版本号一致性

✅ **单一数据源**: 所有版本号从 plugin.json 读取
- README 徽章
- 配置示例
- 页脚版本信息

### 2. 中英文自动同步

✅ **基于同一数据**: 两个模板使用相同的数据字典
- 版本号自动一致
- 命令列表自动一致
- 质量评分自动一致

### 3. 命令列表完整性

✅ **自动扫描**: 从 skills/cmd-*/ 目录扫描
- 新增命令自动出现在列表中
- 描述自动从 SKILL.md 提取
- 支持中英文描述

### 4. 质量评分准确性

✅ **从 CHANGELOG 提取**: 始终使用最新版本的评分
- 总体评分
- 各维度评分
- 自动更新徽章

### 5. 减少人工错误

✅ **模板化生成**:
- 格式一致
- 无拼写错误
- 无遗漏

## 最佳实践

### 1. 每次发布都使用生成脚本

```bash
# ❌ 不要手动编辑 README
vim README.md

# ✅ 使用生成脚本
python3 scripts/generate-readme.py
```

### 2. 先更新数据源，再生成

```bash
# 1. 更新 CHANGELOG.md（添加新版本条目）
# 2. 更新 plugin.json（版本号）
# 3. 更新 marketplace.json（版本号）
# 4. 运行生成脚本
python3 scripts/generate-readme.py
```

### 3. 验证生成结果

```bash
# 查看变更
git diff README.md README_zh.md

# 确保：
# - 版本号正确
# - 命令列表完整
# - 质量评分最新
# - 中英文一致
```

### 4. 自定义内容编辑模板

```bash
# ❌ 不要直接编辑生成的 README
# ✅ 编辑模板文件
vim docs/templates/README-template.md
vim docs/templates/README-template-zh.md

# 然后重新生成
python3 scripts/generate-readme.py
```

## 故障排除

### 问题：模板文件不存在

```
错误: 模板文件不存在: docs/templates/README-template.md
```

**解决**:
```bash
# 确保模板文件存在
ls -la docs/templates/
```

### 问题：提取不到数据

```
KeyError: 'version'
```

**解决**:
```bash
# 检查 plugin.json 格式
cat .claude-plugin/plugin.json | jq .

# 确保包含必需字段
{
  "version": "X.Y.Z",
  "author": {...},
  ...
}
```

### 问题：命令列表为空

```
命令数量: 0
```

**解决**:
```bash
# 检查 skills 目录
ls -la skills/cmd-*/

# 确保每个命令都有 SKILL.md
ls skills/cmd-*/SKILL.md
```

### 问题：质量评分提取失败

```
质量评分: 96  # 使用默认值
```

**解决**:
```bash
# 检查 CHANGELOG.md 格式
# 确保包含：Overall Score: XX/100
grep "Overall Score" CHANGELOG.md
```

## 未来改进

### 计划功能

1. **命令行参数支持**
   ```bash
   python3 scripts/generate-readme.py --version 3.2.0
   python3 scripts/generate-readme.py --dry-run
   ```

2. **自定义模板变量**
   ```bash
   python3 scripts/generate-readme.py --var KEY=VALUE
   ```

3. **CI/CD 集成**
   ```yaml
   # .github/workflows/release.yml
   - name: Generate README
     run: python3 scripts/generate-readme.py
   ```

4. **验证模式**
   ```bash
   python3 scripts/generate-readme.py --validate
   # 验证：
   # - 版本号一致性
   # - 中英文同步
   # - 链接有效性
   ```

5. **多语言支持**
   - 支持更多语言模板
   - 自动翻译（可选）

## 相关文档

- [发布流程](github-release-workflow.md) - 标准发布流程
- [模板说明](templates/) - 模板文件目录
- [CHANGELOG](../CHANGELOG.md) - 版本历史

---

**创建日期**: 2026-03-13
**作者**: mzdbxqh
**最后更新**: 2026-03-13

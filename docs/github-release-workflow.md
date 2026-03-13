# CCC GitHub 标准发布流程

本文档定义了 CCC 插件的标准 GitHub 发布流程，遵循语义化版本控制和 GitHub 最佳实践。

## 版本号规则（语义化版本控制）

遵循 [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)：

- **Major 版本** (X.0.0): 不兼容的 API 变更、重大架构调整、破坏性变更
- **Minor 版本** (3.X.0): 新功能添加、向后兼容的改进
- **Patch 版本** (3.1.X): Bug 修复、向后兼容的小修改

**版本号格式**: `MAJOR.MINOR.PATCH`

**示例**:
- 3.0.0 → 3.1.0: 添加新功能（向后兼容）
- 3.1.0 → 3.1.1: 修复 Bug（向后兼容）
- 3.1.0 → 4.0.0: 移除命名空间（破坏性变更）

---

## 发布前检查清单

在开始发布之前，确保以下条件满足：

### 代码质量
- [ ] 所有计划的功能已完成并测试通过
- [ ] 代码审查完成，质量评分 ≥95/100
- [ ] 所有 ERROR 级别问题已解决
- [ ] WARNING 级别问题已评估并记录

### 测试
- [ ] 核心功能测试通过（evals.json 测试套件）
- [ ] 回归测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过（如适用）

### 文档
- [ ] README.md 已更新
- [ ] README_zh.md 已更新（保持与英文版同步）
- [ ] CHANGELOG.md 已更新
- [ ] API 文档已更新（如有变更）
- [ ] 迁移指南已创建（如有破坏性变更）

### 兼容性
- [ ] 向后兼容性已验证
- [ ] 依赖版本已检查
- [ ] 平台兼容性已测试（macOS/Linux/Windows）

### 安全
- [ ] 安全审查通过
- [ ] 依赖包漏洞扫描通过
- [ ] 敏感信息已清除

---

## 标准发布流程

### 步骤 1: 确定版本号

根据变更类型确定新版本号：

```bash
# 当前版本: 3.1.2
#
# 场景 1: Bug 修复 → 3.1.3 (PATCH)
# 场景 2: 新功能添加 → 3.2.0 (MINOR)
# 场景 3: 破坏性变更 → 4.0.0 (MAJOR)
```

### 步骤 2: 更新版本号和文档

**必须更新的文件（按顺序）**:

#### 2.1 更新 CHANGELOG.md

在文件顶部添加新版本条目：

```markdown
## [X.Y.Z] - YYYY-MM-DD - 版本标题

### Added (新增功能)
- 功能描述

### Changed (变更)
- 变更描述

### Fixed (修复)
- Bug 修复描述

### Removed (移除)
- 移除的功能

### Security (安全)
- 安全相关更新

### Deprecated (废弃)
- 计划废弃的功能

---
```

**破坏性变更示例**:
```markdown
## [3.1.3] - 2026-03-13 - 🔴 Breaking Change: Namespace Removal

### 💥 BREAKING CHANGES

**命名空间已完全移除，所有命令格式更新**

#### 命令格式变更

**旧格式** (已废弃):
```bash
/ccc:init
```

**新格式** (正确):
```bash
/cmd-init
```

### Migration Guide

详细迁移步骤...
```

#### 2.2 自动生成 README（推荐）

**使用自动生成脚本**（避免手动遗漏和中英文不同步）:

```bash
# 运行 README 生成脚本
python3 scripts/generate-readme.py

# 脚本会自动：
# 1. 从 plugin.json 提取版本号
# 2. 从 CHANGELOG.md 提取质量评分
# 3. 从 skills/cmd-* 扫描命令列表
# 4. 从 CHANGELOG.md 提取最新特性
# 5. 生成 README.md（英文）
# 6. 生成 README_zh.md（中文，自动同步）

# 验证生成结果
git diff README.md README_zh.md
```

**生成脚本的优势**:
- ✅ 版本号一致性：自动从 plugin.json 提取，避免手动错误
- ✅ 中英文同步：基于同一数据源，确保两个版本完全一致
- ✅ 命令列表完整：自动扫描 skills/ 目录，不会遗漏新命令
- ✅ 质量评分准确：从 CHANGELOG 最新版本提取，避免过时数据
- ✅ 减少人工错误：模板化生成，避免格式不一致

**数据来源**:
- 版本号：`.claude-plugin/plugin.json`
- 质量评分：`CHANGELOG.md` 最新版本
- 命令列表：扫描 `skills/cmd-*/SKILL.md`
- 功能特性：`CHANGELOG.md` 最新版本的 Added 部分
- 其他元数据：`plugin.json` 和 `marketplace.json`

**如果需要自定义内容**:
1. 编辑模板文件：
   - `docs/templates/README-template.md`（英文模板）
   - `docs/templates/README-template-zh.md`（中文模板）
2. 重新运行生成脚本

#### 2.3 或手动更新 README（不推荐）

**仅当自动生成脚本不可用时使用**

手动更新 README.md (英文):
1. 版本徽章
   ```markdown
   [![Version](https://img.shields.io/badge/version-X.Y.Z-blue.svg)]
   ```

2. Features 部分（如有新功能）
   ```markdown
   ## Features

   - **New Feature Name**: Description (NEW in vX.Y.Z)
   ```

3. Quality Score 徽章（如有变化）
   ```markdown
   [![Quality Score](https://img.shields.io/badge/quality-96%2F100-brightgreen.svg)]
   ```

4. Quality Dimensions 表格（如有变化）
   ```markdown
   | Dimension | Score | Change |
   |-----------|-------|--------|
   | Security  | 98/100| +26    |
   ```

5. Commands 表格（如有新命令）

手动更新 README_zh.md (中文):
**重要**: 必须保持与英文版本完全同步
- 同步更新所有版本号
- 同步更新所有功能描述
- 同步更新所有徽章
- 同步更新命令列表

**⚠️ 手动更新风险**:
- 容易遗漏版本号更新
- 中英文容易不同步
- 命令列表可能过时
- 质量评分可能不准确

#### 2.4 更新 .claude-plugin/plugin.json

**关键配置文件** - Claude Code 读取此文件获取插件版本信息

```json
{
  "name": "ccc",
  "description": "Claude Code Component Creator vX.Y.Z - 简短描述变更",
  "version": "X.Y.Z",  // ← 更新此处
  "author": {
    "name": "mzdbxqh",
    "email": "mzdbxqh@github.com"
  },
  ...
}
```

**破坏性变更时的 description 示例**:
```json
{
  "description": "Claude Code Component Creator v3.1.3 - Breaking Change: Namespace removed, use /cmd-* commands",
  "version": "3.1.3"
}
```

#### 2.5 更新 .claude-plugin/marketplace.json

**插件市场配置文件** - 用于插件分发和市场展示

```json
{
  "name": "ccc-marketplace",
  "owner": {
    "name": "showme.cc"
  },
  "plugins": [
    {
      "name": "ccc",
      "source": "./",
      "description": "Claude Code Component Creator vX.Y.Z - 简短描述",
      "version": "X.Y.Z",  // ← 更新此处
      "author": {
        "name": "mzdbxqh"
      },
      "homepage": "https://github.com/mzdbxqh/claude-code-component-creator",
      "repository": "https://github.com/mzdbxqh/claude-code-component-creator",
      "license": "MIT",
      "keywords": ["component", "design", "workflow", ...]
    }
  ]
}
```

**注意**:
- marketplace.json 中的版本号必须与 plugin.json 保持一致
- description 应该简洁明了，突出主要变更

#### 2.6 其他配置文件（如存在）

- package.json（如存在）
- pyproject.toml（如存在）
- 其他包管理配置文件

### 步骤 3: 提交变更

**推荐提交顺序**（便于回滚）:

```bash
# 确保在插件目录
cd /Users/mzdbxqh/source/component-creator-parent/claude-code-component-creator

# 检查工作区状态
git status

# 第一次提交：文档更新
git add CHANGELOG.md README.md README_zh.md
git commit -m "[doc]更新文档到vX.Y.Z

- CHANGELOG.md: 添加vX.Y.Z版本条目
- README.md: 更新版本徽章和功能描述
- README_zh.md: 同步英文版本更新"

# 第二次提交：配置文件更新
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "[config]更新插件版本到vX.Y.Z

- plugin.json: X.Y.Z-1 → X.Y.Z
- marketplace.json: X.Y.Z-1 → X.Y.Z
- description: 添加版本变更说明"

# 如果有代码变更（通常在之前已提交）
git add <changed-files>
git commit -m "[feat/fix/refactor]简短描述

详细说明..."
```

**提交消息规范**:
```
[type]简短描述（不超过50字符）

详细说明（如需要）:
- 变更点1
- 变更点2
- 变更点3

影响范围:
Breaking Change: 是/否
Migration Required: 是/否
```

**Type 类型**:
- `[feat]`: 新功能
- `[fix]`: Bug 修复
- `[doc]`: 文档更新
- `[config]`: 配置文件更新
- `[refactor]`: 代码重构
- `[test]`: 测试相关
- `[chore]`: 构建/工具相关
- `[release]`: 发布版本

### 步骤 4: 创建 Git 标签

**带注释的标签**（推荐 - 包含完整版本信息）:

```bash
# 创建标签
git tag -a vX.Y.Z -m "Release vX.Y.Z - 版本标题

核心变更:
- 变更1
- 变更2
- 变更3

质量评分: XX/100

关键特性:
- 特性1
- 特性2

Release Risk: 低/中/高
Recommended for Production: 是/否"

# 验证标签创建成功
git tag -l -n9 vX.Y.Z
```

**破坏性变更标签示例**:

```bash
git tag -a v3.1.3 -m "Release v3.1.3 - Breaking Change: Namespace Removal

💥 BREAKING CHANGES: 命名空间完全移除

所有命令格式更新:
- 旧格式: /ccc:* (已废弃)
- 新格式: /cmd-* (必须使用)

文档更新范围:
- README.md: 43 处命令引用 + 版本徽章
- README_zh.md: 16 处命令引用 + 版本徽章
- CHANGELOG.md: 完整变更记录
- 所有 Skill 定义: 200+ 处引用
- 总计: 60+ 文件，500+ 处引用

配置文件更新:
- plugin.json: 3.1.0 → 3.1.3
- marketplace.json: 3.0.0 → 3.1.3

向后兼容性: ❌ 无
Migration Required: 是
Release Risk: 高 - Breaking Change"
```

### 步骤 5: 推送到远程仓库

```bash
# 推送提交
git push origin main

# 推送标签
git push origin vX.Y.Z

# 或者一次性推送所有内容
git push origin main --tags
```

**验证推送成功**:
```bash
# 验证标签已推送
git ls-remote --tags origin | grep vX.Y.Z

# 验证提交已推送
git log origin/main --oneline -5
```

### 步骤 6: 创建 GitHub Release

#### 方法 1: 使用 gh CLI（推荐 - 如果已安装）

```bash
# 检查 gh CLI 是否可用
gh --version

# 从文件创建 release
gh release create vX.Y.Z \
  --title "vX.Y.Z - 版本标题" \
  --notes-file docs/release-notes-vX.Y.Z.md \
  --latest

# 或使用内联说明
gh release create vX.Y.Z \
  --title "vX.Y.Z - 版本标题" \
  --notes "简短说明

主要变更:
- 变更1
- 变更2

详见 CHANGELOG.md" \
  --latest
```

#### 方法 2: 使用 GitHub Web 界面

1. **访问仓库页面**
   ```
   https://github.com/mzdbxqh/claude-code-component-creator
   ```

2. **创建 Release**
   - 点击 "Releases" 标签
   - 点击 "Draft a new release" 按钮

3. **选择标签**
   - 在 "Choose a tag" 下拉框中选择 `vX.Y.Z`
   - 或者输入新标签名（如果还未创建）

4. **填写 Release 信息**

   **标题**:
   ```
   vX.Y.Z - 版本标题
   ```

   **描述**（Markdown 格式）:
   ```markdown
   ## 主要变更

   ### Added (新增)
   - 新功能1
   - 新功能2

   ### Changed (变更)
   - 变更1
   - 变更2

   ### Fixed (修复)
   - Bug 修复1
   - Bug 修复2

   ## 质量评分

   - Overall Score: XX/100
   - Security: XX/100
   - Performance: XX/100

   ## 迁移指南

   详见 [CHANGELOG.md](链接)

   ## 发布风险

   - Risk Level: 低/中/高
   - Breaking Changes: 是/否
   - Migration Required: 是/否

   ---

   **完整详情**: [CHANGELOG.md](https://github.com/mzdbxqh/claude-code-component-creator/blob/main/CHANGELOG.md#xyz)
   ```

   **破坏性变更 Release 描述模板**:
   ```markdown
   ## 💥 重大变更：简短说明

   **此版本包含破坏性变更，不向后兼容。**

   ### 命令/API 变更

   **旧格式** (已废弃，不再工作):
   ```bash
   旧的使用方式
   ```

   **新格式** (正确):
   ```bash
   新的使用方式
   ```

   ### 完整映射表

   | 旧 | 新 | 状态 |
   |---|---|------|
   | old1 | new1 | ✅ 已更新 |
   | old2 | new2 | ✅ 已更新 |

   ### 迁移指南

   **立即行动**:
   1. 步骤1
   2. 步骤2
   3. 步骤3

   **向后兼容性**: ❌ **无**

   ### 影响评估

   - **用户影响**: 高/中/低
   - **迁移要求**: 是/否
   - **质量影响**: 说明

   ---

   详见 [CHANGELOG.md](链接)
   ```

5. **设置 Release 选项**
   - ✅ 勾选 "Set as the latest release"
   - ⚠️ 如果是预发布版本，勾选 "Set as a pre-release"
   - ⚠️ 如果文档未完成，勾选 "Save as draft"

6. **发布**
   - 点击 "Publish release" 按钮

### 步骤 7: 发布后验证

**在 GitHub 上验证**:
- [ ] Release 页面显示新版本
- [ ] README 徽章显示正确版本号
- [ ] CHANGELOG 内容正确显示
- [ ] 标签指向正确的 commit

**本地验证**:
```bash
# 验证标签
git show vX.Y.Z --quiet

# 验证提交历史
git log --oneline -5

# 验证远程同步
git fetch origin
git log origin/main --oneline -5
```

**功能验证**:
```bash
# 重新加载插件
# 在 Claude Code 中执行

# 验证版本号
/cmd-status  # 检查显示的版本号

# 验证核心功能
/cmd-quick   # 测试主要工作流
```

### 步骤 8: 发布通知（可选）

- [ ] 更新项目文档站点（如有）
- [ ] 发送发布公告（邮件/Slack/Discord）
- [ ] 更新依赖该插件的项目
- [ ] 在社区/论坛发布更新通知

---

## 热修复发布流程（Patch 版本）

对于紧急 bug 修复（patch 版本），流程简化：

```bash
# 1. 创建热修复分支（可选，适合团队协作）
git checkout -b hotfix/vX.Y.Z

# 2. 修复问题
# ... 修复代码 ...

# 3. 测试修复
# ... 运行测试 ...

# 4. 更新版本号（仅 PATCH 号）
# - README.md: X.Y.Z-1 → X.Y.Z
# - README_zh.md: X.Y.Z-1 → X.Y.Z
# - CHANGELOG.md: 添加 [X.Y.Z] 条目
# - plugin.json: X.Y.Z-1 → X.Y.Z
# - marketplace.json: X.Y.Z-1 → X.Y.Z

# 5. 提交
git commit -m "[fix]紧急修复: 问题描述

修复内容:
- 修复点1
- 修复点2

影响: 修复XX问题，提升稳定性"

# 6. 合并到主分支（如果使用了分支）
git checkout main
git merge hotfix/vX.Y.Z

# 7. 创建标签
git tag -a vX.Y.Z -m "Hotfix vX.Y.Z - 修复问题描述

紧急修复:
- 问题1
- 问题2

Release Risk: 低（仅 Bug 修复）"

# 8. 推送
git push origin main --tags

# 9. 创建 GitHub Release（同上）

# 10. 清理分支（可选）
git branch -d hotfix/vX.Y.Z
```

---

## 版本回滚流程

如果发现发布有严重问题，可以选择以下方案：

### 方案 1: 撤销标签（仅限发布后 24 小时内）

```bash
# 删除远程标签
git push origin :refs/tags/vX.Y.Z

# 删除本地标签
git tag -d vX.Y.Z

# 在 GitHub Release 页面删除 Release
```

**注意**: 如果用户已下载该版本，不推荐此方案。

### 方案 2: 发布修复版本（推荐）

```bash
# 立即发布 vX.Y.Z+1 修复问题
# 在 CHANGELOG.md 中说明：
## [X.Y.Z+1] - YYYY-MM-DD - Hotfix

### Fixed
- 修复 vX.Y.Z 中的严重问题
```

### 方案 3: 标记为废弃（deprecated）

```bash
# 在 CHANGELOG.md 中标记
## [X.Y.Z] - YYYY-MM-DD - ⚠️ DEPRECATED

**此版本已废弃，请升级到 vX.Y.Z+1**

# 在 GitHub Release 中添加警告
```

---

## 发布检查清单模板

复制此清单用于每次发布：

```markdown
## vX.Y.Z 发布检查清单

**版本类型**: [ ] Major [ ] Minor [ ] Patch
**是否为破坏性变更**: [ ] 是 [ ] 否

### 发布前检查
- [ ] 质量评分 ≥95/100 (当前: ___)
- [ ] ERROR 问题 = 0 (当前: ___)
- [ ] WARNING 问题已评估
- [ ] 核心功能测试通过
- [ ] 回归测试通过
- [ ] 安全审查通过
- [ ] 性能基准建立（如适用）
- [ ] 文档完整性 ≥95%
- [ ] 向后兼容性验证
- [ ] 迁移指南创建（如有破坏性变更）

### 文档更新
- [ ] CHANGELOG.md 新版本条目添加
- [ ] **运行 README 生成脚本** (`python3 scripts/generate-readme.py`)
- [ ] README.md 版本号正确
- [ ] README.md 新功能说明（如有）
- [ ] README_zh.md 与英文版同步
- [ ] README.md 和 README_zh.md 命令列表完整
- [ ] API 文档更新（如有变更）

### 配置文件更新
- [ ] .claude-plugin/plugin.json 版本号更新
- [ ] .claude-plugin/marketplace.json 版本号更新
- [ ] plugin.json 和 marketplace.json 版本号一致
- [ ] description 描述准确

### Git 操作
- [ ] 文档已提交 (commit)
- [ ] 配置已提交 (commit)
- [ ] 标签已创建 (tag vX.Y.Z)
- [ ] 已推送到远程 (push)
- [ ] GitHub Release 已创建

### 发布后验证
- [ ] GitHub Release 页面正确
- [ ] README 徽章显示正确版本
- [ ] 插件可正常加载
- [ ] 核心命令可正常执行
- [ ] 版本号在 /cmd-status 中正确显示
- [ ] 测试套件全部通过

### 发布通知（可选）
- [ ] 文档站点已更新
- [ ] 发布公告已发送
- [ ] 依赖项目已通知
```

---

## 最佳实践

### 版本管理
1. **规律的发布节奏**: 建立固定的发布周期（如每月一次 minor 版本）
2. **版本号提前规划**: 在开发周期初期就规划好版本号
3. **语义化严格遵守**: 严格按照 SemVer 规范确定版本号
4. **避免跳跃版本**: 不要跳过版本号（如 3.1.0 → 3.3.0）

### 文档管理
1. **CHANGELOG 先行**: 开发过程中持续更新 CHANGELOG
2. **双语文档同步**: 中英文文档必须保持同步
3. **迁移指南完整**: 破坏性变更必须提供详细迁移指南
4. **示例代码充足**: 提供足够的示例帮助用户理解变更

### Git 管理
1. **标签注释详细**: 标签注释应包含关键变更和影响
2. **提交消息规范**: 使用约定式提交消息格式
3. **分支策略清晰**: main 分支保持稳定，使用 feature/hotfix 分支
4. **标签不可变**: 已推送的标签不应修改或删除

### 配置文件管理
1. **版本号一致性**: 所有配置文件的版本号必须保持一致
   - plugin.json
   - marketplace.json
   - README.md 徽章
   - CHANGELOG.md
2. **配置文件优先级**:
   - plugin.json: Claude Code 读取的主配置
   - marketplace.json: 市场分发配置
   - 两者必须同步更新
3. **描述信息准确**: description 字段应准确反映版本变更，特别是破坏性变更

### 发布管理
1. **自动化流程**: 考虑使用 GitHub Actions 自动化发布流程
2. **版本锁定**: 重要项目依赖应锁定具体版本号
3. **回滚预案**: 准备好版本回滚方案
4. **发布验证**: 每次发布后进行完整的功能验证

---

## 常见问题

### Q: 什么时候应该升级 major 版本？

**A**: 当满足以下任一条件时：
- 有不兼容的 API 变更
- 重大架构调整
- 移除已废弃功能
- 命令/接口格式发生破坏性变更
- 需要用户手动迁移

**示例**:
- v3.1.3 移除命名空间 → 应该是 v4.0.0（因为是破坏性变更）
- 但如果已经在 3.x 系列，可以用 3.1.3 + Breaking Change 标注

### Q: plugin.json 和 marketplace.json 有什么区别？

**A**:
- **plugin.json**: Claude Code 本地加载时读取的配置文件
  - 控制插件在本地的版本显示
  - 包含插件的基本元数据

- **marketplace.json**: 插件市场分发配置
  - 用于插件市场展示
  - 可能包含多个插件的配置
  - 用户从市场安装时使用此文件

**两者必须保持版本号一致！**

### Q: 忘记更新 plugin.json/marketplace.json 怎么办？

**A**:
1. 立即创建新的提交更新版本号
2. 不要修改已推送的标签
3. 如果已经创建 Release，可以编辑 Release 说明添加勘误
4. 考虑发布一个 patch 版本修正

### Q: 标签推送失败怎么办？

**A**:
```bash
# 检查标签是否已存在
git tag -l | grep vX.Y.Z

# 删除本地标签
git tag -d vX.Y.Z

# 重新创建
git tag -a vX.Y.Z -m "..."

# 如果远程已存在，先删除远程标签
git push origin :refs/tags/vX.Y.Z

# 重新推送
git push origin vX.Y.Z
```

### Q: 如何撤销已发布的版本？

**A**: 不推荐撤销，应该：
1. 发布新版本修复问题
2. 在文档中标注问题版本
3. 如必须撤销（发布后 24 小时内）：
   - 删除标签：`git push origin :refs/tags/vX.Y.Z`
   - 删除 GitHub Release
   - 在文档中说明

### Q: Release notes 应该包含什么内容？

**A**:
- **必需**:
  - 主要变更说明
  - 新功能列表
  - 修复的问题
  - 破坏性变更（如有）
  - 迁移指南（如有）

- **推荐**:
  - 质量评分
  - 性能改进
  - 致谢贡献者
  - 完整 CHANGELOG 链接

### Q: 版本号中间可以跳号吗？

**A**:
- **不推荐**跳过版本号
- 每个版本号都应该对应一个实际的发布
- 如果某个版本被废弃，应该标记为 deprecated 而不是跳过

### Q: 如何处理多个 breaking changes？

**A**:
1. 合并到一个 major 版本中
2. 在 CHANGELOG 中详细列出所有破坏性变更
3. 为每个变更提供迁移指南
4. 考虑提供迁移工具或脚本

---

## 自动化建议

### GitHub Actions 工作流示例

创建 `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Verify version consistency
        run: |
          PLUGIN_VERSION=$(jq -r '.version' .claude-plugin/plugin.json)
          MARKET_VERSION=$(jq -r '.plugins[0].version' .claude-plugin/marketplace.json)
          TAG_VERSION=${GITHUB_REF#refs/tags/v}

          if [ "$PLUGIN_VERSION" != "$TAG_VERSION" ] || [ "$MARKET_VERSION" != "$TAG_VERSION" ]; then
            echo "Version mismatch!"
            echo "Tag: $TAG_VERSION"
            echo "plugin.json: $PLUGIN_VERSION"
            echo "marketplace.json: $MARKET_VERSION"
            exit 1
          fi

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

---

## 附录

### 版本号示例

```
1.0.0 - 初始发布
1.0.1 - Bug 修复
1.1.0 - 新功能（向后兼容）
1.2.0 - 新功能（向后兼容）
2.0.0 - 破坏性变更
2.0.1 - Bug 修复
2.1.0 - 新功能（向后兼容）
3.0.0 - 重大重构
```

### 提交消息示例

```
[feat]添加并行处理支持

新增功能:
- --parallel 标志
- --max-workers 参数
- 3层并行处理架构

性能提升: 3.75x-6.8x

Breaking Change: 否
```

### 标签注释示例

```
Release v3.1.0 - Production Ready

Quality Score: 96/100 (A+)

Major Improvements:
- Security: +26 points
- Scalability: +21 points
- Testability: +17 points

Key Features:
- Circular dependency prevention
- Token budget transparency
- Parallel processing support

Release Risk: Very Low
Recommended for Production
```

---

## 更新历史

- 2026-03-13: 初始版本，添加 plugin.json 和 marketplace.json 更新步骤
- 未来更新将记录在此处

---

**相关文档**:
- [CHANGELOG.md](../CHANGELOG.md) - 完整版本历史
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 贡献指南
- [CLAUDE.md](../../CLAUDE.md) - 项目指南

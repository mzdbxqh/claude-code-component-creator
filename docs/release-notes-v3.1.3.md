# Release v3.1.3 - 🔴 Breaking Change: Namespace Removal

**发布日期**: 2026-03-13
**质量评分**: 96/100 (A+ 级) - 保持不变
**变更类型**: 🔴 **破坏性变更**
**升级要求**: **必须**

---

## 🔴 重大变更警告

### 命名空间功能已完全移除

根据 **Claude Code 官方标准**，命名空间（namespace）功能已被废弃。所有插件命令必须使用直接的 skill 名称调用。

**这是一个破坏性变更，所有用户必须更新其命令调用方式。**

---

## 📋 命令格式变更

### 旧格式 ❌ (已废弃，不再工作)

```bash
/ccc:init
/ccc:design
/ccc:review
/ccc:quick
# ... 等18个命令
```

### 新格式 ✅ (正确，必须使用)

```bash
/cmd-init
/cmd-design
/cmd-review
/cmd-quick
# ... 等18个命令
```

---

## 🔄 完整命令映射表

| 旧命令 (废弃) | 新命令 (正确) | 用途 |
|--------------|--------------|------|
| `/ccc:quick` | `/cmd-quick` | 一键执行完整工作流 |
| `/ccc:init` | `/cmd-init` | 创建意图工件 |
| `/ccc:design` | `/cmd-design` | 生成蓝图 |
| `/ccc:design-new` | `/cmd-design-new` | 新组件设计 |
| `/ccc:design-iterate` | `/cmd-design-iterate` | 迭代设计 |
| `/ccc:build` | `/cmd-build` | 构建交付物 |
| `/ccc:implement` | `/cmd-implement` | 实施迭代计划 |
| `/ccc:iterate` | `/cmd-iterate` | 蓝图迭代 |
| `/ccc:review` | `/cmd-review` | 质量审查 |
| `/ccc:review-workflow` | `/cmd-review-workflow` | 工作流审查 |
| `/ccc:review-migration-plan` | `/cmd-review-migration-plan` | 迁移计划审查 |
| `/ccc:fix` | `/cmd-fix` | 问题修复 |
| `/ccc:validate` | `/cmd-validate` | 工件验证 |
| `/ccc:status` | `/cmd-status` | 状态查看 |
| `/ccc:status-graph` | `/cmd-status-graph` | 状态图 |
| `/ccc:status-trace` | `/cmd-status-trace` | 状态追踪 |
| `/ccc:trace` | `/cmd-trace` | 追溯矩阵 |
| `/ccc:diff` | `/cmd-diff` | 工件对比 |
| `/ccc:test-sandbox` | `/cmd-test-sandbox` | 测试沙箱 |

---

## 📊 修复范围

本次发布更新了整个代码库中的所有命令引用：

### 核心文档
- ✅ **README.md** - 43 处引用已更新
- ✅ **README_zh.md** - 16 处引用已更新
- ✅ **CONTRIBUTING.md** - 已更新
- ✅ **TROUBLESHOOTING.md** - 25 处引用已更新
- ✅ **CONFIGURATION.md** - 已更新
- ✅ **SECURITY.md** - 4 处引用已更新

### Skills 定义
- ✅ **19 个 Skill 文件** - 200+ 处引用已更新
- ✅ **所有测试文档** - 50+ 处引用已更新

### 用户指南和文档
- ✅ **docs/** 目录 - 100+ 处引用已更新
- ✅ **agents/** 文档 - 所有引用已更新

### 统计总计
- **修改文件**: 60+ 个 Markdown 文件
- **替换总数**: 500+ 处命令引用
- **验证结果**: ✅ 0 个错误引用残留

---

## 🗑️ 已移除：不存在的命令

以下命令引用已被删除或标注为"计划中"（这些命令从未实现）：

| 旧引用 | 处理方式 |
|--------|----------|
| `/ccc:eval-executor` | 标注为 SubAgent（通过 `/cmd-test-sandbox` 调用） |
| `/ccc:checkpoint` | 标注为计划中功能 |
| `/ccc:benchmark` | 标注为计划中功能 |
| `/ccc:clean` | 替换为 `/cmd-status --clean` (计划中) |
| `/ccc:projects` | 替换为 `/cmd-status` |
| `/ccc:link` | 标注为手动操作或计划中功能 |
| `/ccc:list` | 替换为 `/cmd-status` |
| `/ccc:show` | 替换为 `/cmd-status --show-details` |
| `/ccc:import` | 替换为 `/cmd-init --from-template` (计划中) |

---

## 🚀 迁移指南

### 立即行动清单

#### 1. 更新脚本和自动化

**查找所有 `/ccc:` 调用**:
```bash
grep -r '/ccc:' your-scripts/
```

**批量替换** (示例):
```bash
# macOS/Linux
sed -i 's|/ccc:review|/cmd-review|g' your-script.sh

# 或使用查找替换工具
```

#### 2. 更新 CI/CD 配置

检查以下文件中的命令调用：
- `.github/workflows/*.yml`
- `.gitlab-ci.yml`
- `Jenkinsfile`
- 其他 CI 配置文件

#### 3. 通知团队成员

发送通知模板：
```
【重要】CCC v3.1.3 破坏性变更

命名空间已移除，所有 /ccc: 命令必须更新为 /cmd- 格式。

旧格式: /ccc:review ❌
新格式: /cmd-review ✅

请立即更新您的脚本和工作流。

详见: https://github.com/mzdbxqh/claude-code-component-creator/releases/tag/v3.1.3
```

#### 4. 验证更新

运行测试确保所有命令正常工作：
```bash
/cmd-status  # 应该正常工作
/ccc:status  # 将不再工作
```

---

## ⚠️ 向后兼容性

**兼容性状态**: ❌ **无向后兼容性**

- ❌ 旧的 `/ccc:` 格式将**不再工作**
- ✅ 必须更新所有调用为 `/cmd-` 格式
- ✅ Skill 内部实现未变更，仅调用方式变更

---

## 📖 官方参考

- **Claude Code 插件文档**: https://docs.claude.ai/plugins
- **命名空间废弃公告**: 官方文档已移除命名空间相关内容
- **最佳实践**: 使用直接的 skill 名称调用

---

## 🎯 质量保证

**质量评分**: 96/100 (A+ 级) - **保持不变**

尽管进行了大规模的文档更新，CCC 的质量评分和功能完全保持不变：
- ✅ ERROR 问题: 0
- ✅ 循环依赖: 0
- ✅ 工作流完整性: 100%
- ✅ 测试覆盖率: 95%
- ✅ 文档完整性: 94%

本次变更**仅影响文档和示例**，不影响任何功能实现。

---

## 📞 需要帮助?

### 常见问题

**Q: 为什么要移除命名空间？**
A: Claude Code 官方已废弃命名空间功能，所有插件必须遵循新标准。

**Q: 我的旧脚本还能用吗？**
A: ❌ 不能。您必须更新所有 `/ccc:` 调用为 `/cmd-` 格式。

**Q: 如何批量更新？**
A: 使用 `sed` 或您喜欢的文本编辑器的查找替换功能。

**Q: 功能有变化吗？**
A: ✅ 没有。仅命令调用方式变更，所有功能保持不变。

### 反馈渠道

- **Issues**: https://github.com/mzdbxqh/claude-code-component-creator/issues
- **Discussions**: https://github.com/mzdbxqh/claude-code-component-creator/discussions

---

## 📦 其他变更

无其他功能变更。完整变更历史请参考 [CHANGELOG.md](CHANGELOG.md)。

---

**发布负责人**: mzdbxqh
**发布日期**: 2026-03-13
**下次审查**: 预计 2026-05-13 (v3.2.0)

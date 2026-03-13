# /cmd-fix 用户指南

**文档版本**: v1.0
**最后更新**: 2026-03-06
**适用版本**: CCC Plugin v3.1+

---

## 快速入门

### 什么是 /cmd-fix？

`/cmd-fix` 是 CCC 插件的交互式修复命令，基于审查报告自动修复组件质量问题。它支持三种修复模式：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 全自动修复 | 批量修复所有 P0/P1 问题 | 信任自动修复，快速迭代 |
| 交互式修复 | 逐类确认修复范围和方案 | 首次使用，谨慎修复 |
| 手动修复 | 仅生成修复建议 | 复杂场景，需要人工判断 |

### 基本用法

```bash
# 启动交互式修复（推荐首次使用）
/cmd-fix --artifact-id=DLV-001

# 自动修复所有 P0 问题（Error 级别）
/cmd-fix --artifact-id=DLV-001 --auto

# 预览修复内容（不实际修改文件）
/cmd-fix --artifact-id=DLV-001 --dry-run
```

---

## 参数详解

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--artifact-id` | 指定要修复的交付物 ID | `--artifact-id=DLV-001` |

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--auto` | false | 自动修复所有 P0 问题，无需确认 |
| `--dry-run` | false | 预览模式，不实际修改文件 |

---

## 使用示例

### 示例 1: 标准交互式修复

```bash
# 步骤 1: 先执行审查
/cmd-review --artifact-id=DLV-001

# 步骤 2: 执行修复
/cmd-fix --artifact-id=DLV-001
```

**交互流程**:
1. 系统加载审查报告，显示问题摘要
2. 选择修复策略（全自动/交互式/手动）
3. 选择修复范围（仅 P0/P0+P1/全部）
4. 确认执行
5. 查看修复结果

---

### 示例 2: 自动修复模式

```bash
/cmd-fix --artifact-id=DLV-001 --auto
```

**适用场景**:
- 已信任自动修复质量
- 需要快速修复大量 P0 问题
- CI/CD 流水线集成

**输出示例**:
```
修复完成！

修复摘要:
  - 修复文件数：3 个
  - 修复问题数：12 个
  - 修复耗时：2 分 35 秒

修复报告：docs/fixes/2026-03-06-DLV-001-fix.md
```

---

### 示例 3: 预览模式

```bash
/cmd-fix --artifact-id=DLV-001 --dry-run
```

**输出示例**:
```
预览模式 - 不会修改任何文件

将要修复的问题:
  - command/deploy.md: 添加 argument-hint 字段
  - skills/reviewer/SKILL.md: 添加 model 声明
  - agents/builder/SKILL.md: 添加使用示例章节

预计修复文件数：3
预计修复问题数：12
```

---

### 示例 4: 与审查命令连用

```bash
# 完整工作流
/cmd-review --artifact-id=DLV-001   # 审查
/cmd-fix --artifact-id=DLV-001      # 修复
/cmd-review --artifact-id=DLV-002   # 再审查验证修复效果
```

---

## 修复范围说明

### 问题级别定义

| 级别 | 代号 | 说明 | 修复优先级 |
|------|------|------|------------|
| Error | P0 | 阻塞性问题，必须修复 | 最高 |
| Warning | P1 | 建议修复的问题 | 中等 |
| Info | P2 | 可选优化项 | 低 |

### 修复策略选择

#### 全自动修复
- 修复范围：所有 P0 + P1 问题
- 用户确认：无需
- 适用场景：信任自动修复

#### 交互式修复
- 修复范围：用户选择
- 用户确认：需要
- 适用场景：首次使用或复杂场景

#### 手动修复
- 修复范围：仅生成建议
- 用户确认：N/A
- 适用场景：需要人工判断的复杂问题

---

## 可修复的问题类型

### 1. 元数据问题 (Metadata Fix Agent)

| 问题 | 修复内容 |
|------|----------|
| 缺少 argument-hint | 添加参数提示字段 |
| 缺少 model 声明 | 添加模型推荐 |
| 缺少 context 声明 | 添加上下文模式 |
| description 过短 | 增强描述内容 |

### 2. 工具权限问题 (Tool Declare Agent)

| 问题 | 修复内容 |
|------|----------|
| 缺少 allowed-tools | 分析实际使用，添加声明 |
| 工具权限过宽 | 建议最小权限集 |

### 3. 文档完整性问题 (Doc Complete Agent)

| 问题 | 修复内容 |
|------|----------|
| 缺少使用示例 | 生成 5 个多样化示例 |
| 缺少错误处理 | 添加错误处理表格 |
| 缺少注意事项 | 补充最佳实践和陷阱 |

---

## 修复报告

### 报告位置

修复报告保存在：
```
docs/fixes/YYYY-MM-DD-<artifact-id>-fix.md
```

### 报告内容

```markdown
# 修复报告：DLV-001

## 修复摘要
| 指标 | 值 |
|------|-----|
| 修复文件数 | 3 |
| 修复问题数 | 12 |
| 修复耗时 | 155 秒 |

## 变更详情
### command/deploy.md
- 添加 argument-hint 字段
- 补充错误处理文档

### skills/reviewer/SKILL.md
- 添加 model: sonnet 声明
- 添加 allowed-tools 声明

## Git Commits 建议
chore: fix metadata issues in deploy.md
chore: add tool declarations in reviewer skill

## 修复前后对比
| 指标 | 修复前 | 修复后 | 变化 |
|------|--------|--------|------|
| 总体评分 | 72/100 | 94/100 | +22 |
```

---

## 常见问题

### Q1: 修复失败了怎么办？

**A**: 系统会自动回滚失败的文件修改，并生成部分成功报告。检查修复报告中的错误详情，手动修复剩余问题。

### Q2: 可以取消正在执行的修复吗？

**A**: 可以。在交互过程中选择"暂停"选项，系统会保存进度供以后继续。

### Q3: 修复后需要重新审查吗？

**A**: 强烈建议。执行 `/cmd-review --artifact-id=<新 ID>` 验证修复效果。

### Q4: 自动修复的准确率如何？

**A**: 元数据修复准确率约 95%，工具声明约 90%，文档补充约 85%。复杂场景建议使用交互式模式。

### Q5: 修复会创建 Git 提交吗？

**A**: 不会。修复完成后会提供建议的 commit 消息，需要用户手动执行 git add 和 git commit。

---

## 最佳实践

### 1. 审查后立即修复

```bash
/cmd-review --artifact-id=DLV-001
/cmd-fix --artifact-id=DLV-001    # 立即修复
```

### 2. 首次使用选择交互式模式

```bash
# 首次使用，了解修复内容
/cmd-fix --artifact-id=DLV-001

# 熟悉后使用自动模式
/cmd-fix --artifact-id=DLV-002 --auto
```

### 3. 定期运行 dry-run 检查

```bash
# 每周检查新增问题
/cmd-fix --artifact-id=latest --dry-run
```

### 4. 保留修复报告

```bash
# 修复报告是重要的质量记录
cat docs/fixes/YYYY-MM-DD-<artifact-id>-fix.md
```

---

## 故障排除

### 问题：找不到审查报告

**错误信息**: "Review report not found for DLV-001"

**解决方案**:
```bash
# 先执行审查
/cmd-review --artifact-id=DLV-001
# 再执行修复
/cmd-fix --artifact-id=DLV-001
```

### 问题：文件已被修改

**错误信息**: "File has been modified since review"

**解决方案**:
1. 选择"重新审查"选项
2. 或手动确认是否继续修复

### 问题：修复后评分未提升

**可能原因**:
- 修复的内容被其他问题抵消
- 新增问题在修复过程中产生

**解决方案**:
```bash
# 执行完整审查查看新问题
/cmd-review --artifact-id=<新 ID>
```

---

## 相关命令

| 命令 | 说明 |
|------|------|
| `/cmd-review` | 执行质量审查 |
| `/cmd-review-workflow` | 工作流串联审查 |
| `/cmd-status` | 查看项目状态 |
| `/cmd-build` | 构建交付物 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-03-06 | 初始版本 |

---

*文档生成于 2026-03-06 | CCC Plugin User Guide*

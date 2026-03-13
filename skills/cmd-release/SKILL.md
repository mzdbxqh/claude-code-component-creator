---
name: cmd-release
description: "GitHub发布工作流。自动化执行版本发布：更新版本号、生成README、创建标签、推送代码。遵循语义化版本控制。"
version: 1.0.0
author: mzdbxqh
trigger-keywords: ["发布", "release", "版本发布", "publish", "新版本"]
argument-hint: "[版本号] [--major|--minor|--patch] [--dry-run]"
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
permissionMode: prompt
disable-model-invocation: false
---

# GitHub 发布技能

## 概述

自动化执行 GitHub 发布流程，包括：

1. **版本号管理**：确定新版本号（支持 major/minor/patch）
2. **配置更新**：更新 plugin.json 和 marketplace.json
3. **文档生成**：自动生成 README.md 和 README_zh.md
4. **Git 操作**：提交、创建标签、推送到远程
5. **发布准备**：生成 GitHub Release 所需内容

遵循语义化版本控制（SemVer 2.0.0）和 CCC 发布标准。

## 工作流定位

**独立工具**。执行完整的版本发布流程，无前后依赖。

## 使用场景

- 发布新的 major/minor/patch 版本
- 执行破坏性变更发布
- 发布热修复版本
- 预发布版本（--dry-run 模式）

## 参数

### 位置参数

- **版本号**（可选）：指定版本号，如 `3.2.0`
  - 如果不提供，根据 `--major|--minor|--patch` 自动计算

### 选项参数

- **--major**：升级主版本号（X.0.0）
  - 用于：不兼容的 API 变更、重大架构调整

- **--minor**：升级次版本号（3.X.0）
  - 用于：新功能添加、向后兼容的改进

- **--patch**：升级补丁版本号（3.1.X）
  - 用于：Bug 修复、向后兼容的小修改
  - 默认选项（如果未指定）

- **--dry-run**：演练模式，不实际执行 Git 操作
  - 显示将要执行的操作
  - 不修改文件、不提交、不推送

- **--skip-readme**：跳过 README 生成
  - 仅当手动维护 README 时使用

- **--skip-tests**：跳过发布前测试
  - 不推荐，仅在紧急情况使用

## 工作流步骤

### Step 1: 发布前检查

**目的**：确保满足发布条件

**操作**：

```python
def pre_release_checks():
    """
    执行发布前检查

    检查项：
    1. Git 工作区干净（无未提交变更）
    2. 当前在 main 分支
    3. 与远程同步
    4. plugin.json 和 marketplace.json 存在
    5. CHANGELOG.md 存在
    6. README 生成脚本存在

    返回：
    - True: 所有检查通过
    - False: 有检查失败（显示详细错误）
    """

    # 1. 检查 Git 状态
    result = run_bash("git status --porcelain")
    if result.strip():
        error("Git 工作区不干净，请先提交或暂存变更")
        return False

    # 2. 检查当前分支
    branch = run_bash("git branch --show-current").strip()
    if branch != "main":
        error(f"当前在分支 {branch}，请切换到 main 分支")
        return False

    # 3. 检查与远程同步
    run_bash("git fetch origin")
    local = run_bash("git rev-parse @").strip()
    remote = run_bash("git rev-parse @{u}").strip()
    if local != remote:
        error("本地与远程不同步，请先 pull 或 push")
        return False

    # 4. 检查必需文件
    required_files = [
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        "CHANGELOG.md",
        "scripts/generate-readme.py"
    ]

    for file in required_files:
        if not file_exists(file):
            error(f"必需文件不存在: {file}")
            return False

    return True
```

**输出**：检查结果（通过/失败）

---

### Step 2: 确定版本号

**目的**：根据参数或当前版本计算新版本号

**操作**：

```python
def determine_version(args):
    """
    确定新版本号

    优先级：
    1. 显式指定版本号（args.version）
    2. 根据 --major/--minor/--patch 计算
    3. 默认：patch 版本升级

    验证：
    - 版本号格式符合 SemVer
    - 新版本号大于当前版本
    - 如果是破坏性变更，建议使用 major 版本
    """

    # 读取当前版本
    plugin_json = read_json(".claude-plugin/plugin.json")
    current_version = plugin_json['version']

    # 解析版本号
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', current_version)
    major, minor, patch = map(int, match.groups())

    # 计算新版本号
    if args.version:
        # 验证版本号格式
        if not is_valid_semver(args.version):
            error(f"无效的版本号格式: {args.version}")
            return None
        new_version = args.version
    elif args.major:
        new_version = f"{major + 1}.0.0"
    elif args.minor:
        new_version = f"{major}.{minor + 1}.0"
    else:  # patch (默认)
        new_version = f"{major}.{minor}.{patch + 1}"

    # 验证新版本大于当前版本
    if not version_greater_than(new_version, current_version):
        error(f"新版本 {new_version} 不大于当前版本 {current_version}")
        return None

    # 显示版本信息
    print(f"当前版本: {current_version}")
    print(f"新版本: {new_version}")

    # 如果是 major 版本，提醒破坏性变更
    if new_version.startswith(str(major + 1) + ".0.0"):
        warning("这是一个 MAJOR 版本升级，请确保：")
        warning("  1. CHANGELOG.md 中标注了破坏性变更")
        warning("  2. 提供了完整的迁移指南")
        warning("  3. 已通知用户即将发生的变更")

    return new_version
```

**输出**：新版本号

---

### Step 3: 更新 CHANGELOG.md

**目的**：为新版本添加 CHANGELOG 条目

**操作**：

```python
def update_changelog(version, dry_run=False):
    """
    更新 CHANGELOG.md

    操作：
    1. 检查是否已有新版本条目
    2. 如果没有，在顶部添加模板条目
    3. 提示用户编辑 CHANGELOG

    注意：
    - 不自动生成变更内容（需要人工编写）
    - 仅提供模板结构
    - 验证格式正确性
    """

    changelog_path = "CHANGELOG.md"
    content = read_file(changelog_path)

    # 检查是否已有版本条目
    version_pattern = f"## [{version}]"
    if version_pattern in content:
        info(f"CHANGELOG.md 中已存在 [{version}] 条目")
        return True

    # 准备新版本条目模板
    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""## [{version}] - {today}

### Added (新增功能)
- 功能描述

### Changed (变更)
- 变更描述

### Fixed (修复)
- Bug 修复描述

### Removed (移除)
- 移除的功能

---

"""

    # 找到第一个 ## [ 位置，插入新条目
    first_version_match = re.search(r'## \[', content)
    if first_version_match:
        insert_pos = first_version_match.start()
        new_content = content[:insert_pos] + template + content[insert_pos:]
    else:
        # 如果没有找到，添加到 ## [Unreleased] 之后
        unreleased_match = re.search(r'## \[Unreleased\].*?\n\n', content, re.DOTALL)
        if unreleased_match:
            insert_pos = unreleased_match.end()
            new_content = content[:insert_pos] + template + content[insert_pos:]
        else:
            error("无法确定 CHANGELOG.md 的插入位置")
            return False

    if not dry_run:
        write_file(changelog_path, new_content)
        info(f"已在 CHANGELOG.md 中添加 [{version}] 条目")
    else:
        info("[DRY-RUN] 将在 CHANGELOG.md 中添加版本条目")

    # 提示用户编辑
    warning("请编辑 CHANGELOG.md，填写版本变更内容：")
    warning(f"  1. 打开 CHANGELOG.md")
    warning(f"  2. 找到 ## [{version}] 章节")
    warning(f"  3. 在各个小节下填写具体变更")
    warning(f"  4. 删除不需要的小节")

    # 等待用户确认
    if not dry_run:
        confirm = ask_user("CHANGELOG.md 是否已编辑完成？", default="no")
        if not confirm:
            error("已取消发布流程")
            return False

    return True
```

**输出**：更新后的 CHANGELOG.md

---

### Step 4: 更新配置文件

**目的**：更新 plugin.json 和 marketplace.json 中的版本号

**操作**：

```python
def update_config_files(version, dry_run=False):
    """
    更新配置文件版本号

    文件：
    1. .claude-plugin/plugin.json
    2. .claude-plugin/marketplace.json

    操作：
    - 更新 version 字段
    - 更新 description（如果需要）
    - 保持其他字段不变
    - 验证 JSON 格式
    """

    # 1. 更新 plugin.json
    plugin_json_path = ".claude-plugin/plugin.json"
    plugin_json = read_json(plugin_json_path)

    old_version = plugin_json['version']
    plugin_json['version'] = version

    # 如果 description 包含版本号，也更新
    if old_version in plugin_json['description']:
        plugin_json['description'] = plugin_json['description'].replace(
            old_version, version
        )

    if not dry_run:
        write_json(plugin_json_path, plugin_json)
        info(f"已更新 plugin.json: {old_version} → {version}")
    else:
        info(f"[DRY-RUN] 将更新 plugin.json: {old_version} → {version}")

    # 2. 更新 marketplace.json
    marketplace_json_path = ".claude-plugin/marketplace.json"
    marketplace_json = read_json(marketplace_json_path)

    # marketplace.json 中 plugins 数组的第一个元素
    if 'plugins' in marketplace_json and len(marketplace_json['plugins']) > 0:
        plugin = marketplace_json['plugins'][0]
        old_market_version = plugin['version']
        plugin['version'] = version

        # 更新 description
        if old_market_version in plugin['description']:
            plugin['description'] = plugin['description'].replace(
                old_market_version, version
            )

        if not dry_run:
            write_json(marketplace_json_path, marketplace_json)
            info(f"已更新 marketplace.json: {old_market_version} → {version}")
        else:
            info(f"[DRY-RUN] 将更新 marketplace.json: {old_market_version} → {version}")
    else:
        error("marketplace.json 格式异常")
        return False

    return True
```

**输出**：更新后的配置文件

---

### Step 5: 生成 README

**目的**：运行 README 生成脚本，确保文档同步

**操作**：

```python
def generate_readme(skip_readme=False, dry_run=False):
    """
    运行 README 生成脚本

    命令：python3 scripts/generate-readme.py

    验证：
    - 脚本执行成功
    - README.md 和 README_zh.md 已生成
    - 版本号正确
    - 中英文同步
    """

    if skip_readme:
        warning("已跳过 README 生成（--skip-readme）")
        return True

    if not dry_run:
        info("正在生成 README.md 和 README_zh.md...")
        result = run_bash("python3 scripts/generate-readme.py")

        if result.returncode != 0:
            error("README 生成失败")
            print(result.stderr)
            return False

        print(result.stdout)
        info("README 生成成功")

        # 验证生成结果
        if not file_exists("README.md") or not file_exists("README_zh.md"):
            error("README 文件未生成")
            return False

    else:
        info("[DRY-RUN] 将运行: python3 scripts/generate-readme.py")

    return True
```

**输出**：生成的 README.md 和 README_zh.md

---

### Step 6: 运行发布前测试（可选）

**目的**：验证核心功能正常工作

**操作**：

```python
def run_pre_release_tests(skip_tests=False, dry_run=False):
    """
    运行发布前测试

    测试项：
    1. 插件可以正常加载
    2. 核心命令可以执行
    3. 测试套件通过

    注意：
    - 可以通过 --skip-tests 跳过
    - 如果测试失败，终止发布流程
    """

    if skip_tests:
        warning("已跳过发布前测试（--skip-tests）")
        return True

    if not dry_run:
        info("正在运行发布前测试...")

        # 1. 运行测试套件（如果存在）
        if file_exists("scripts/run-tests.sh"):
            result = run_bash("bash scripts/run-tests.sh")
            if result.returncode != 0:
                error("测试失败，已终止发布流程")
                return False
            info("测试通过")
        else:
            warning("未找到测试脚本，跳过测试")
    else:
        info("[DRY-RUN] 将运行发布前测试")

    return True
```

**输出**：测试结果

---

### Step 7: 提交变更

**目的**：提交所有版本相关的变更

**操作**：

```python
def commit_changes(version, dry_run=False):
    """
    提交版本变更

    提交顺序：
    1. 文档提交（CHANGELOG + README）
    2. 配置提交（plugin.json + marketplace.json）

    提交消息格式：
    [release]vX.Y.Z - 简短描述

    详细内容从 CHANGELOG 提取
    """

    if not dry_run:
        # 1. 文档提交
        run_bash("git add CHANGELOG.md README.md README_zh.md")

        commit_msg_doc = f"""[doc]更新文档到v{version}

- CHANGELOG.md: 添加v{version}版本条目
- README.md: 更新版本徽章（自动生成）
- README_zh.md: 同步英文版本（自动生成）"""

        result = run_bash(f"git commit -m '{commit_msg_doc}'")
        if result.returncode != 0:
            error("文档提交失败")
            return False

        info("文档已提交")

        # 2. 配置提交
        run_bash("git add .claude-plugin/plugin.json .claude-plugin/marketplace.json")

        commit_msg_config = f"""[config]更新插件版本到v{version}

- plugin.json: 版本更新
- marketplace.json: 版本更新"""

        result = run_bash(f"git commit -m '{commit_msg_config}'")
        if result.returncode != 0:
            error("配置提交失败")
            return False

        info("配置已提交")

    else:
        info(f"[DRY-RUN] 将提交文档变更")
        info(f"[DRY-RUN] 将提交配置变更")

    return True
```

**输出**：Git 提交记录

---

### Step 8: 创建 Git 标签

**目的**：为新版本创建带注释的 Git 标签

**操作**：

```python
def create_git_tag(version, dry_run=False):
    """
    创建 Git 标签

    标签名：vX.Y.Z
    标签注释：从 CHANGELOG.md 提取版本内容

    格式：
    Release vX.Y.Z - 版本标题

    主要变更：
    - 变更1
    - 变更2

    详见 CHANGELOG.md
    """

    tag_name = f"v{version}"

    # 从 CHANGELOG 提取版本内容
    changelog_content = read_file("CHANGELOG.md")

    # 提取版本标题
    version_section_match = re.search(
        rf'## \[{version}\] - \d{{4}}-\d{{2}}-\d{{2}}(.*?)\n\n(.*?)(?=\n## \[|$)',
        changelog_content,
        re.DOTALL
    )

    if version_section_match:
        version_title = version_section_match.group(1).strip()
        version_content = version_section_match.group(2).strip()

        # 简化内容（只保留前3个变更点）
        changes = []
        for line in version_content.split('\n'):
            if line.strip().startswith('- '):
                changes.append(line.strip())
                if len(changes) >= 3:
                    break

        tag_message = f"""Release v{version}{' - ' + version_title if version_title else ''}

主要变更:
{chr(10).join(changes[:3])}

详见 CHANGELOG.md"""
    else:
        # 如果提取失败，使用简单消息
        tag_message = f"Release v{version}\n\n详见 CHANGELOG.md"

    if not dry_run:
        # 创建标签
        result = run_bash(f"git tag -a {tag_name} -m '{tag_message}'")

        if result.returncode != 0:
            # 检查是否标签已存在
            if "already exists" in result.stderr:
                error(f"标签 {tag_name} 已存在")
                confirm = ask_user("是否删除旧标签并重新创建？", default="no")
                if confirm:
                    run_bash(f"git tag -d {tag_name}")
                    result = run_bash(f"git tag -a {tag_name} -m '{tag_message}'")
                    if result.returncode != 0:
                        error("标签创建失败")
                        return False
                else:
                    return False
            else:
                error("标签创建失败")
                return False

        info(f"已创建标签: {tag_name}")

        # 显示标签内容
        run_bash(f"git show {tag_name} --quiet")
    else:
        info(f"[DRY-RUN] 将创建标签: {tag_name}")
        print(f"\n标签消息:\n{tag_message}\n")

    return True
```

**输出**：Git 标签

---

### Step 9: 推送到远程

**目的**：推送提交和标签到远程仓库

**操作**：

```python
def push_to_remote(version, dry_run=False):
    """
    推送到远程仓库

    操作：
    1. 推送提交：git push origin main
    2. 推送标签：git push origin vX.Y.Z

    验证：
    - 推送成功
    - 远程已有新提交和标签
    """

    tag_name = f"v{version}"

    if not dry_run:
        # 1. 推送提交
        info("正在推送提交到远程...")
        result = run_bash("git push origin main")

        if result.returncode != 0:
            error("推送提交失败")
            print(result.stderr)
            return False

        info("提交已推送")

        # 2. 推送标签
        info(f"正在推送标签 {tag_name} 到远程...")
        result = run_bash(f"git push origin {tag_name}")

        if result.returncode != 0:
            error("推送标签失败")
            print(result.stderr)
            return False

        info(f"标签 {tag_name} 已推送")

        # 验证
        result = run_bash(f"git ls-remote --tags origin | grep {tag_name}")
        if tag_name in result.stdout:
            success(f"验证成功：远程已有标签 {tag_name}")
        else:
            warning(f"警告：无法验证远程标签 {tag_name}")
    else:
        info(f"[DRY-RUN] 将推送提交到 origin/main")
        info(f"[DRY-RUN] 将推送标签 {tag_name} 到 origin")

    return True
```

**输出**：推送结果

---

### Step 10: 生成 GitHub Release 内容

**目的**：生成 GitHub Release 所需的内容，供用户手动创建 Release

**操作**：

```python
def generate_release_content(version):
    """
    生成 GitHub Release 内容

    输出：
    1. Release 标题
    2. Release 描述（Markdown）
    3. 创建 Release 的步骤

    注意：
    - 不自动创建 Release（需要用户在 GitHub 网页操作）
    - 提供完整的 Release 描述模板
    """

    # 从 CHANGELOG 提取版本内容
    changelog_content = read_file("CHANGELOG.md")

    version_section_match = re.search(
        rf'## \[{version}\] - \d{{4}}-\d{{2}}-\d{{2}}(.*?)\n\n(.*?)(?=\n---\n|$)',
        changelog_content,
        re.DOTALL
    )

    if version_section_match:
        version_title = version_section_match.group(1).strip()
        version_content = version_section_match.group(2).strip()
    else:
        version_title = ""
        version_content = "详见 CHANGELOG.md"

    # 检查是否为破坏性变更
    is_breaking = "BREAKING" in version_content or "破坏性" in version_content

    release_title = f"v{version}{' - ' + version_title if version_title else ''}"

    if is_breaking:
        release_title = f"💥 {release_title}"

    release_description = f"""## {version_title if version_title else '版本更新'}

{version_content}

---

**完整详情**: [CHANGELOG.md](https://github.com/mzdbxqh/claude-code-component-creator/blob/main/CHANGELOG.md#{version.replace('.', '')})
"""

    # 显示 Release 内容
    print("\n" + "="*60)
    print("GitHub Release 内容已生成")
    print("="*60)
    print(f"\n标题: {release_title}\n")
    print("描述:\n")
    print(release_description)
    print("\n" + "="*60)

    # 保存到文件
    release_file = f"docs/release-notes-v{version}.md"
    write_file(release_file, release_description)
    info(f"Release 内容已保存到: {release_file}")

    # 显示创建 Release 的步骤
    print("\n请在 GitHub 网页创建 Release：\n")
    print("1. 访问: https://github.com/mzdbxqh/claude-code-component-creator/releases/new")
    print(f"2. 选择标签: v{version}")
    print(f"3. 标题: {release_title}")
    print(f"4. 描述: 复制上面的内容或使用 {release_file}")
    print("5. 勾选 'Set as the latest release'")
    print("6. 点击 'Publish release'\n")

    return True
```

**输出**：GitHub Release 内容和创建步骤

---

### Step 11: 发布后验证

**目的**：验证发布是否成功

**操作**：

```python
def post_release_verification(version, dry_run=False):
    """
    发布后验证

    验证项：
    1. 远程标签存在
    2. 最新提交已推送
    3. plugin.json 和 marketplace.json 版本正确
    4. README.md 版本徽章正确
    """

    if dry_run:
        info("[DRY-RUN] 跳过发布后验证")
        return True

    info("正在执行发布后验证...")

    tag_name = f"v{version}"

    # 1. 验证远程标签
    result = run_bash(f"git ls-remote --tags origin | grep {tag_name}")
    if tag_name in result.stdout:
        success(f"✓ 远程标签存在: {tag_name}")
    else:
        error(f"✗ 远程标签不存在: {tag_name}")
        return False

    # 2. 验证提交已推送
    result = run_bash("git log origin/main --oneline -1")
    local_commit = run_bash("git log --oneline -1").stdout.strip()
    remote_commit = result.stdout.strip()

    if local_commit == remote_commit:
        success("✓ 最新提交已推送")
    else:
        error("✗ 本地和远程提交不一致")
        return False

    # 3. 验证配置文件版本
    plugin_json = read_json(".claude-plugin/plugin.json")
    if plugin_json['version'] == version:
        success(f"✓ plugin.json 版本正确: {version}")
    else:
        error(f"✗ plugin.json 版本错误: {plugin_json['version']} != {version}")
        return False

    marketplace_json = read_json(".claude-plugin/marketplace.json")
    if marketplace_json['plugins'][0]['version'] == version:
        success(f"✓ marketplace.json 版本正确: {version}")
    else:
        error(f"✗ marketplace.json 版本错误")
        return False

    # 4. 验证 README 徽章
    readme_content = read_file("README.md")
    if f"version-{version}" in readme_content:
        success(f"✓ README.md 版本徽章正确: {version}")
    else:
        warning(f"⚠ README.md 版本徽章可能不正确")

    print("\n" + "="*60)
    success(f"发布验证通过！版本 {version} 已成功发布。")
    print("="*60)

    return True
```

**输出**：验证结果摘要

---

## 完整示例

### 示例 1: 发布 patch 版本（默认）

```bash
# 当前版本: 3.1.3
# 目标: 发布 3.1.4 (Bug 修复)

/cmd-release

# 或明确指定 patch
/cmd-release --patch

# 脚本会：
# 1. 检查发布前条件
# 2. 确定版本号: 3.1.3 → 3.1.4
# 3. 在 CHANGELOG.md 添加 [3.1.4] 条目（需要手动编辑）
# 4. 更新 plugin.json 和 marketplace.json
# 5. 生成 README.md 和 README_zh.md
# 6. 提交变更
# 7. 创建标签 v3.1.4
# 8. 推送到远程
# 9. 生成 GitHub Release 内容
# 10. 验证发布成功
```

### 示例 2: 发布 minor 版本（新功能）

```bash
# 当前版本: 3.1.4
# 目标: 发布 3.2.0 (新功能)

/cmd-release --minor

# 版本号: 3.1.4 → 3.2.0
```

### 示例 3: 发布 major 版本（破坏性变更）

```bash
# 当前版本: 3.2.0
# 目标: 发布 4.0.0 (破坏性变更)

/cmd-release --major

# 版本号: 3.2.0 → 4.0.0
# 会提示确认破坏性变更说明
```

### 示例 4: 指定版本号

```bash
# 直接指定版本号
/cmd-release 3.1.5

# 版本号: 3.1.4 → 3.1.5
```

### 示例 5: 演练模式

```bash
# 不实际执行，仅显示将要执行的操作
/cmd-release --dry-run

# 输出示例：
# [DRY-RUN] 当前版本: 3.1.4
# [DRY-RUN] 新版本: 3.1.5
# [DRY-RUN] 将在 CHANGELOG.md 中添加版本条目
# [DRY-RUN] 将更新 plugin.json
# [DRY-RUN] 将更新 marketplace.json
# [DRY-RUN] 将运行: python3 scripts/generate-readme.py
# [DRY-RUN] 将提交文档变更
# [DRY-RUN] 将提交配置变更
# [DRY-RUN] 将创建标签: v3.1.5
# [DRY-RUN] 将推送到 origin/main
# [DRY-RUN] 将推送标签 v3.1.5
```

### 示例 6: 跳过 README 生成

```bash
# 手动维护 README 时使用
/cmd-release --skip-readme

# 会跳过 Step 5
```

## 错误处理

### 错误 1: Git 工作区不干净

```
错误: Git 工作区不干净，请先提交或暂存变更

解决:
git status
git add .
git commit -m "提交信息"
```

### 错误 2: 不在 main 分支

```
错误: 当前在分支 feature/xxx，请切换到 main 分支

解决:
git checkout main
```

### 错误 3: 与远程不同步

```
错误: 本地与远程不同步，请先 pull 或 push

解决:
git fetch origin
git pull origin main
```

### 错误 4: 版本号格式无效

```
错误: 无效的版本号格式: 3.1.a

解决:
使用正确的语义化版本号，如: 3.1.5
```

### 错误 5: 新版本不大于当前版本

```
错误: 新版本 3.1.3 不大于当前版本 3.1.4

解决:
指定更大的版本号，如: 3.1.5 或 3.2.0
```

### 错误 6: CHANGELOG.md 未编辑

```
CHANGELOG.md 是否已编辑完成？[no]: no
已取消发布流程

解决:
1. 编辑 CHANGELOG.md
2. 填写版本变更内容
3. 重新运行 /cmd-release
```

### 错误 7: README 生成失败

```
错误: README 生成失败

解决:
1. 检查 scripts/generate-readme.py 是否存在
2. 手动运行: python3 scripts/generate-readme.py
3. 查看错误信息
4. 或使用 --skip-readme 跳过
```

### 错误 8: 标签已存在

```
错误: 标签 v3.1.5 已存在
是否删除旧标签并重新创建？[no]:

解决:
输入 yes 删除旧标签并重新创建
或手动删除: git tag -d v3.1.5
```

### 错误 9: 推送失败

```
错误: 推送提交失败

可能原因:
1. 网络问题
2. 权限不足
3. 远程仓库保护

解决:
1. 检查网络连接
2. 验证 Git 凭据
3. 检查分支保护规则
```

## 输出

### 成功输出示例

```
开始 GitHub 发布流程...

[Step 1] 发布前检查
✓ Git 工作区干净
✓ 当前在 main 分支
✓ 与远程同步
✓ 必需文件存在

[Step 2] 确定版本号
当前版本: 3.1.4
新版本: 3.1.5

[Step 3] 更新 CHANGELOG.md
已在 CHANGELOG.md 中添加 [3.1.5] 条目
请编辑 CHANGELOG.md，填写版本变更内容
CHANGELOG.md 是否已编辑完成？[no]: yes

[Step 4] 更新配置文件
已更新 plugin.json: 3.1.4 → 3.1.5
已更新 marketplace.json: 3.1.4 → 3.1.5

[Step 5] 生成 README
正在生成 README.md 和 README_zh.md...
  [1/5] 提取版本信息...
  [2/5] 提取质量评分...
  [3/5] 扫描命令列表...
  [4/5] 提取特性列表...
  [5/5] 渲染模板...
  ✓ 已生成: README.md
  ✓ 已生成: README_zh.md
README 生成成功

[Step 6] 运行发布前测试
已跳过发布前测试（--skip-tests）

[Step 7] 提交变更
文档已提交
配置已提交

[Step 8] 创建 Git 标签
已创建标签: v3.1.5

[Step 9] 推送到远程
正在推送提交到远程...
提交已推送
正在推送标签 v3.1.5 到远程...
标签 v3.1.5 已推送
验证成功：远程已有标签 v3.1.5

[Step 10] 生成 GitHub Release 内容
============================================================
GitHub Release 内容已生成
============================================================

标题: v3.1.5 - Bug 修复版本

描述:

## Bug 修复版本

### Fixed
- 修复 README 生成脚本的编码问题
- 修复命令列表提取逻辑
- 修复版本号验证正则表达式

---

**完整详情**: [CHANGELOG.md](https://github.com/mzdbxqh/claude-code-component-creator/blob/main/CHANGELOG.md#315)

============================================================

Release 内容已保存到: docs/release-notes-v3.1.5.md

请在 GitHub 网页创建 Release：

1. 访问: https://github.com/mzdbxqh/claude-code-component-creator/releases/new
2. 选择标签: v3.1.5
3. 标题: v3.1.5 - Bug 修复版本
4. 描述: 复制上面的内容或使用 docs/release-notes-v3.1.5.md
5. 勾选 'Set as the latest release'
6. 点击 'Publish release'

[Step 11] 发布后验证
正在执行发布后验证...
✓ 远程标签存在: v3.1.5
✓ 最新提交已推送
✓ plugin.json 版本正确: 3.1.5
✓ marketplace.json 版本正确: 3.1.5
✓ README.md 版本徽章正确: 3.1.5

============================================================
发布验证通过！版本 3.1.5 已成功发布。
============================================================
```

## 依赖

### 工具依赖

- **Git**: 版本控制
- **Python 3**: README 生成脚本
- **Bash**: 命令执行

### 文件依赖

- `.claude-plugin/plugin.json`: 插件配置
- `.claude-plugin/marketplace.json`: 市场配置
- `CHANGELOG.md`: 版本历史
- `scripts/generate-readme.py`: README 生成脚本
- `docs/templates/README-template.md`: README 英文模板
- `docs/templates/README-template-zh.md`: README 中文模板

## 最佳实践

1. **每次发布前运行 --dry-run**
   ```bash
   /cmd-release --dry-run
   ```
   检查将要执行的操作，避免错误。

2. **认真编辑 CHANGELOG.md**
   - 详细描述变更内容
   - 如果是破坏性变更，必须标注
   - 提供迁移指南

3. **验证 README 生成结果**
   ```bash
   git diff README.md README_zh.md
   ```
   确保版本号、命令列表、质量评分正确。

4. **发布后立即创建 GitHub Release**
   - 不要延迟创建 Release
   - Release 是用户获取版本信息的主要途径

5. **遵循语义化版本控制**
   - Bug 修复 → patch (3.1.X)
   - 新功能 → minor (3.X.0)
   - 破坏性变更 → major (X.0.0)

## 相关文档

- [GitHub 发布流程](../../docs/github-release-workflow.md)
- [README 生成机制](../../docs/readme-generation.md)
- [语义化版本控制](https://semver.org/spec/v2.0.0.html)
- [CHANGELOG 格式](https://keepachangelog.com/)

## 作者

- **mzdbxqh** - [GitHub](https://github.com/mzdbxqh)

## 版本历史

- **1.0.0** (2026-03-13): 初始版本
  - 完整的发布流程自动化
  - 支持 major/minor/patch 版本升级
  - 集成 README 自动生成
  - 完善的错误处理和验证

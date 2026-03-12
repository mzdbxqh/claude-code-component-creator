# CCC 工作流中断和恢复机制

## 概述

为长时间运行的 CCC 工作流提供检查点保存和恢复功能，确保任务可以在中断后从上次停止的位置继续执行。

## 设计原则

### 1. 透明性
- 自动保存检查点，无需用户干预
- 清晰的恢复状态提示
- 完整的进度跟踪

### 2. 安全性
- 原子性写入检查点
- 检查点加密（可选）
- 自动清理过期检查点

### 3. 效率性
- 增量保存状态
- 压缩大型状态数据
- 异步写入检查点

## 架构设计

### 检查点结构

```json
{
  "checkpoint_id": "CHP-2026-03-12-001",
  "workflow": "design",
  "artifact_id": "DLV-001",
  "timestamp": "2026-03-12T10:30:00Z",
  "version": "1.0.0",
  "state": {
    "current_phase": "blueprint-generation",
    "completed_steps": [
      "intent-creation",
      "requirement-analysis",
      "architecture-design"
    ],
    "pending_steps": [
      "blueprint-generation",
      "validation"
    ],
    "phase_data": {
      "intent_id": "INT-001",
      "architecture_recommendation": {...},
      "requirements": {...}
    }
  },
  "context": {
    "user_inputs": [...],
    "llm_responses": [...],
    "artifacts_created": [...]
  },
  "metadata": {
    "tokens_used": 25000,
    "elapsed_time": 180,
    "retry_count": 0
  }
}
```

### 存储位置

```
.ccc/
├── checkpoints/
│   ├── design/
│   │   ├── CHP-2026-03-12-001.json
│   │   └── CHP-2026-03-12-002.json
│   ├── review/
│   │   └── CHP-2026-03-12-003.json
│   └── fix/
│       └── CHP-2026-03-12-004.json
├── recovery/
│   └── recovery.log
└── locks/
    └── design.lock
```

## 实现方案

### 1. 检查点管理器

```python
class CheckpointManager:
    """检查点管理器"""

    def __init__(self, workflow_name, artifact_id):
        self.workflow_name = workflow_name
        self.artifact_id = artifact_id
        self.checkpoint_dir = f".ccc/checkpoints/{workflow_name}"
        self.lock_file = f".ccc/locks/{workflow_name}.lock"
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, state, phase_name):
        """保存检查点"""
        checkpoint_id = self._generate_checkpoint_id()
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "workflow": self.workflow_name,
            "artifact_id": self.artifact_id,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "state": state,
            "metadata": {
                "phase": phase_name,
                "tokens_used": self._get_tokens_used(),
                "elapsed_time": self._get_elapsed_time()
            }
        }

        # 原子性写入
        temp_file = f"{self.checkpoint_dir}/{checkpoint_id}.tmp"
        final_file = f"{self.checkpoint_dir}/{checkpoint_id}.json"

        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)

            # 原子重命名
            os.rename(temp_file, final_file)

            logging.info(f"Checkpoint saved: {checkpoint_id}")
            return checkpoint_id

        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise CheckpointError(f"Failed to save checkpoint: {e}")

    def load_latest_checkpoint(self):
        """加载最新检查点"""
        checkpoints = self._list_checkpoints()
        if not checkpoints:
            return None

        latest = max(checkpoints, key=lambda c: c['timestamp'])
        return self._load_checkpoint(latest['checkpoint_id'])

    def resume_from_checkpoint(self, checkpoint_id=None):
        """从检查点恢复"""
        if checkpoint_id:
            checkpoint = self._load_checkpoint(checkpoint_id)
        else:
            checkpoint = self.load_latest_checkpoint()

        if not checkpoint:
            raise ValueError("No checkpoint found to resume")

        # 验证检查点完整性
        self._validate_checkpoint(checkpoint)

        # 恢复状态
        state = checkpoint['state']
        phase = checkpoint['metadata']['phase']

        logging.info(f"Resuming from checkpoint: {checkpoint['checkpoint_id']}")
        logging.info(f"Phase: {phase}")
        logging.info(f"Completed steps: {state['completed_steps']}")

        return state, phase

    def cleanup_old_checkpoints(self, keep_count=5):
        """清理旧检查点"""
        checkpoints = self._list_checkpoints()
        if len(checkpoints) <= keep_count:
            return

        # 按时间排序，删除旧的
        sorted_checkpoints = sorted(
            checkpoints,
            key=lambda c: c['timestamp'],
            reverse=True
        )

        for checkpoint in sorted_checkpoints[keep_count:]:
            file_path = f"{self.checkpoint_dir}/{checkpoint['checkpoint_id']}.json"
            os.remove(file_path)
            logging.info(f"Removed old checkpoint: {checkpoint['checkpoint_id']}")
```

### 2. 工作流集成

```python
class ResumableWorkflow:
    """可恢复的工作流"""

    def __init__(self, workflow_name, artifact_id):
        self.workflow_name = workflow_name
        self.artifact_id = artifact_id
        self.checkpoint_mgr = CheckpointManager(workflow_name, artifact_id)
        self.state = {}

    def execute(self, resume=False):
        """执行工作流"""
        if resume:
            # 从检查点恢复
            self.state, current_phase = self.checkpoint_mgr.resume_from_checkpoint()
            self._resume_from_phase(current_phase)
        else:
            # 全新执行
            self._execute_from_start()

    def _execute_from_start(self):
        """从头开始执行"""
        phases = self._get_workflow_phases()

        for phase in phases:
            try:
                # 执行阶段
                result = self._execute_phase(phase)

                # 更新状态
                self.state['completed_steps'].append(phase['name'])
                self.state['phase_data'][phase['name']] = result

                # 保存检查点
                self.checkpoint_mgr.save_checkpoint(self.state, phase['name'])

            except KeyboardInterrupt:
                # 用户中断，保存当前状态
                logging.warning("Workflow interrupted by user")
                self.checkpoint_mgr.save_checkpoint(self.state, phase['name'])
                raise

            except Exception as e:
                # 错误，保存检查点并退出
                logging.error(f"Phase {phase['name']} failed: {e}")
                self.checkpoint_mgr.save_checkpoint(self.state, phase['name'])
                raise

    def _resume_from_phase(self, resume_phase):
        """从指定阶段恢复"""
        phases = self._get_workflow_phases()

        # 找到恢复点
        resume_index = next(
            i for i, p in enumerate(phases)
            if p['name'] == resume_phase
        )

        # 从恢复点继续执行
        for phase in phases[resume_index:]:
            self._execute_phase(phase)
            self.state['completed_steps'].append(phase['name'])
            self.checkpoint_mgr.save_checkpoint(self.state, phase['name'])

        # 清理旧检查点
        self.checkpoint_mgr.cleanup_old_checkpoints()
```

### 3. 命令行集成

```yaml
# SKILL.md 参数扩展

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--artifact-id` | 制品ID | 必需 |
| `--resume` | 从上次中断处恢复 | false |
| `--checkpoint-id` | 指定检查点ID恢复 | latest |
| `--no-checkpoint` | 禁用检查点保存 | false |
| `--checkpoint-interval` | 检查点保存间隔（秒） | 60 |

## 使用示例

```bash
# 正常执行
/ccc:design --name=my-skill

# 执行被中断（Ctrl+C）...

# 从上次中断处恢复
/ccc:design --name=my-skill --resume

# 从特定检查点恢复
/ccc:design --name=my-skill --checkpoint-id=CHP-2026-03-12-001

# 查看可用检查点
/ccc:checkpoint --list --workflow=design

# 清理旧检查点
/ccc:checkpoint --cleanup --workflow=design --keep=5
```
```

### 4. 进度显示

```python
class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.completed_steps = 0

    def update(self, step_name):
        """更新进度"""
        self.completed_steps += 1
        progress = (self.completed_steps / self.total_steps) * 100

        print(f"\n[{self.completed_steps}/{self.total_steps}] {step_name}")
        print(self._render_progress_bar(progress))

    def _render_progress_bar(self, progress):
        """渲染进度条"""
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        return f"[{bar}] {progress:.1f}%"
```

## 错误处理

### 中断类型

| 中断类型 | 处理方式 | 恢复策略 |
|---------|---------|----------|
| 用户中断（Ctrl+C） | 保存检查点，优雅退出 | 完全恢复 |
| 进程崩溃 | 最后一个检查点 | 部分恢复 |
| 网络超时 | 自动重试 + 检查点 | 自动恢复 |
| LLM 超时 | 保存检查点，提示重试 | 手动恢复 |
| 磁盘空间不足 | 清理旧检查点，提示 | 手动处理 |

### 恢复验证

```python
def validate_checkpoint(checkpoint):
    """验证检查点完整性"""
    required_fields = ['checkpoint_id', 'workflow', 'state', 'metadata']

    for field in required_fields:
        if field not in checkpoint:
            raise ValueError(f"Missing required field: {field}")

    # 验证状态一致性
    state = checkpoint['state']
    if 'completed_steps' not in state or 'pending_steps' not in state:
        raise ValueError("Invalid state structure")

    # 验证工件存在
    for artifact in checkpoint['context'].get('artifacts_created', []):
        if not os.path.exists(artifact):
            raise ValueError(f"Artifact missing: {artifact}")

    return True
```

## 最佳实践

### 1. 检查点保存时机

- **阶段完成后**: 每个主要阶段完成后保存
- **长操作前**: 执行耗时操作前保存
- **用户交互后**: AskUserQuestion 后保存
- **定时保存**: 每隔一定时间自动保存

### 2. 状态管理

- **最小化状态**: 仅保存必要数据
- **序列化优化**: 使用高效的序列化格式
- **增量保存**: 仅保存变更部分
- **压缩大数据**: 对大型状态数据压缩

### 3. 安全考虑

- **敏感数据**: 不保存敏感信息到检查点
- **权限控制**: 检查点文件仅用户可读
- **加密存储**: 可选的检查点加密
- **完整性校验**: 使用哈希校验检查点

### 4. 性能优化

- **异步写入**: 不阻塞主流程
- **批量清理**: 定期批量清理旧检查点
- **缓存优化**: 缓存最近的检查点
- **延迟写入**: 聚合多个小更新

## 监控和日志

### 检查点日志

```
2026-03-12 10:30:00 [INFO] Checkpoint saved: CHP-2026-03-12-001
2026-03-12 10:35:00 [INFO] Checkpoint saved: CHP-2026-03-12-002
2026-03-12 10:35:30 [WARNING] Workflow interrupted by user
2026-03-12 10:36:00 [INFO] Resuming from checkpoint: CHP-2026-03-12-002
2026-03-12 10:40:00 [INFO] Workflow completed successfully
2026-03-12 10:40:05 [INFO] Removed old checkpoint: CHP-2026-03-12-001
```

### 恢复报告

```markdown
# Workflow Recovery Report

## Recovery Details
- **Checkpoint ID**: CHP-2026-03-12-002
- **Workflow**: design
- **Artifact ID**: DLV-001
- **Resume Time**: 2026-03-12 10:36:00

## Progress at Interruption
- **Completed Steps**: 3/5
  1. ✅ Intent Creation
  2. ✅ Requirement Analysis
  3. ✅ Architecture Design
  4. ⏸️ Blueprint Generation (interrupted)
  5. ⏹️ Validation (pending)

## Remaining Work
- Blueprint Generation (continue from 60%)
- Validation

## Estimated Time to Completion
- **Remaining**: ~5 minutes
- **Total Saved**: ~10 minutes (60% completed)
```

## 工具命令

### checkpoint 命令

```bash
# 列出检查点
/ccc:checkpoint --list --workflow=design

# 查看检查点详情
/ccc:checkpoint --show --id=CHP-2026-03-12-001

# 删除检查点
/ccc:checkpoint --delete --id=CHP-2026-03-12-001

# 清理旧检查点
/ccc:checkpoint --cleanup --workflow=design --keep=5

# 导出检查点
/ccc:checkpoint --export --id=CHP-2026-03-12-001 --output=/tmp/checkpoint.json

# 导入检查点
/ccc:checkpoint --import --file=/tmp/checkpoint.json
```

## 未来扩展

1. **分布式检查点**: 支持多机恢复
2. **云端备份**: 自动备份到云存储
3. **智能恢复**: AI 辅助决定最佳恢复点
4. **并行检查点**: 支持并行工作流的检查点
5. **增量快照**: 类似 Git 的增量存储

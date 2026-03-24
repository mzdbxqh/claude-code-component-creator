---
name: long-task-template
model: sonnet
context: fork
disable-model-invocation: true
description: "长任务模板：展示如何使用 ccc-core 持久化基础设施实现断点续传的长任务 Agent/Skill"
argument-hint: "[--task-name=<name>] [--resume=<trace_id>] [--base-dir=<path>]"
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# /long-task-template

**用途**: 长任务持久化模板，展示如何使用 ccc-core 持久化基础设施实现断点续传功能。

**适用场景**:
- 执行时间超过 10 分钟的长任务
- 需要多阶段执行的工作流
- 不能因中断而丢失进度的关键任务
- 需要支持断点续传的 Agent/Skill

## 何时使用此模板

当满足以下条件时，使用此模板作为开发基础：

| 条件 | 说明 |
|------|------|
| 多阶段执行 | 任务包含 3+ 个独立阶段 |
| 长时间运行 | 预计执行时间 > 10 分钟 |
| 状态敏感 | 中断后需要恢复而非重启 |
| 数据量大 | 需要持久化中间结果 |
| 可靠性要求高 | 不允许因意外中断而失败 |

## 持久化基础设施

本模板基于 ccc-core/persistence/ 模块：

```
ccc-core/persistence/
├── __init__.py           # 导出所有组件
├── state.py              # State 状态管理
├── checkpoint.py         # CheckpointManager 检查点管理
├── data_manager.py       # DataManager 数据持久化
└── resume_manager.py     # ResumeManager 断点续传
```

### 核心组件

| 组件 | 职责 | 关键方法 |
|------|------|----------|
| **State** | 追踪执行阶段、步骤、状态 | set_phase(), set_step(), add_result(), mark_completed() |
| **CheckpointManager** | 保存/恢复状态快照 | save(), restore(), list_checkpoints() |
| **DataManager** | 持久化中间结果 | save_result(), load_result(), has_result() |
| **ResumeManager** | 提供断点续传能力 | can_resume(), get_last_checkpoint(), resume_from_checkpoint() |

## Workflow

### Step 0: 检查 Checkpoint 并提供恢复选项

**目标**: 检测是否存在可恢复的 checkpoint，提示用户选择。

```python
from ccc_core.persistence import ResumeManager, generate_trace_id

# 检查是否有可恢复的 trace
base_dir = "."
resume_trace_id = args.get("--resume")

if resume_trace_id:
    # 用户指定了要恢复的 trace_id
    resume_mgr = ResumeManager(resume_trace_id, base_dir)

    if resume_mgr.can_resume():
        context = resume_mgr.get_resume_context()
        print(f"发现可恢复的 checkpoint: {context['last_checkpoint']}")
        print(f"当前阶段: {context['current_phase']}")
        print(f"当前步骤: {context['current_step']}")
        # 进入恢复流程
    else:
        print(f"警告: trace {resume_trace_id} 没有可恢复的 checkpoint")
        # 创建新的 trace_id
        trace_id = generate_trace_id()
else:
    # 检查最近执行的 traces
    reports_dir = os.path.join(base_dir, "reports")
    if os.path.exists(reports_dir):
        traces = sorted(os.listdir(reports_dir), reverse=True)
        for trace in traces[:3]:  # 检查最近 3 个
            resume_mgr = ResumeManager(trace, base_dir)
            if resume_mgr.can_resume():
                print(f"发现未完成的 trace: {trace}")
                # 提示用户是否恢复
                break
        else:
            trace_id = generate_trace_id()
    else:
        trace_id = generate_trace_id()
```

### Step 1: 初始化持久化组件

**目标**: 创建 trace_id 并初始化所有持久化管理器。

```python
from ccc_core.persistence import (
    State,
    CheckpointManager,
    DataManager,
    ResumeManager,
    generate_trace_id
)

# 生成 trace_id (格式: YYYYMMDD_HHMMSS_Random6)
trace_id = generate_trace_id()
print(f"[INIT] Trace ID: {trace_id}")

# 初始化所有管理器
base_dir = args.get("--base-dir", ".")
state = State(trace_id)
checkpoint_mgr = CheckpointManager(trace_id, base_dir)
data_mgr = DataManager(trace_id, base_dir)
resume_mgr = ResumeManager(trace_id, base_dir)

# 标记开始执行
state.mark_running()
state.set_phase("initialization")
state.set_step("setup")

# 保存初始 checkpoint
checkpoint_mgr.save("init", {
    "state": state.to_dict(),
    "config": task_config,
    "metadata": {"start_time": datetime.now().isoformat()}
})
```

### Step 2: 每个主要步骤前后保存 Checkpoint

**目标**: 确保每个关键步骤都可以恢复。

```python
def execute_step_with_checkpoint(step_name, step_func, state, checkpoint_mgr):
    """
    执行步骤并自动管理 checkpoint

    模式: 前置 checkpoint -> 执行 -> 后置 checkpoint
    """
    print(f"[STEP] 开始执行: {step_name}")

    # 1. 保存前置 checkpoint（记录进入步骤）
    state.set_step(f"{step_name}_started")
    checkpoint_mgr.save(f"step_{step_name}_started", {
        "state": state.to_dict(),
        "step": step_name,
        "status": "in_progress"
    })

    try:
        # 2. 执行实际步骤
        result = step_func()

        # 3. 保存后置 checkpoint（记录完成）
        state.add_result(f"{step_name}_result", result)
        state.set_step(f"{step_name}_completed")
        checkpoint_mgr.save(f"step_{step_name}_completed", {
            "state": state.to_dict(),
            "step": step_name,
            "result": result,
            "status": "completed"
        })

        print(f"[STEP] 完成: {step_name}")
        return result

    except Exception as e:
        # 4. 失败时保存错误状态
        state.mark_failed(str(e))
        checkpoint_mgr.save(f"step_{step_name}_failed", {
            "state": state.to_dict(),
            "step": step_name,
            "error": str(e),
            "status": "failed"
        })
        raise
```

### Step 3: 保存中间结果到 DataManager

**目标**: 持久化重要的中间数据，支持跨步骤访问。

```python
# 示例: 数据收集阶段
def data_collection_phase(task_name, state, data_mgr, checkpoint_mgr):
    """数据收集阶段 - 保存收集结果"""
    state.set_phase("data_collection")

    # 收集数据（可能耗时很长）
    collected_data = collect_data_from_sources()

    # 保存到 DataManager（原子写入）
    filepath = data_mgr.save_result(
        task_name=task_name,
        step_name="data_collection",
        data={
            "items": collected_data,
            "count": len(collected_data),
            "timestamp": datetime.now().isoformat()
        }
    )
    print(f"[DATA] 数据已保存: {filepath}")

    # 同时保存 checkpoint
    checkpoint_mgr.save("data_collection_completed", {
        "state": state.to_dict(),
        "data_file": filepath
    })

    return collected_data

# 示例: 分析阶段读取之前的数据
def analysis_phase(task_name, state, data_mgr):
    """分析阶段 - 读取之前收集的数据"""
    state.set_phase("analysis")

    # 检查是否存在之前的数据
    if data_mgr.has_result(task_name, "data_collection"):
        # 加载之前保存的数据
        data = data_mgr.load_result(task_name, "data_collection")
        print(f"[DATA] 加载已收集数据: {data['count']} 条")
    else:
        # 数据不存在，需要重新收集
        raise ValueError("数据收集结果不存在，请先执行数据收集阶段")

    # 执行分析
    analysis_result = analyze_data(data)

    # 保存分析结果
    data_mgr.save_result(
        task_name=task_name,
        step_name="analysis",
        data=analysis_result
    )

    return analysis_result
```

### Step 4: 标记完成并清理

**目标**: 任务完成后标记状态，可选清理临时数据。

```python
def finalize_task(state, checkpoint_mgr, data_mgr):
    """完成任务并保存最终状态"""

    # 标记完成
    state.mark_completed()
    state.set_phase("completed")
    state.set_step("final")

    # 保存最终 checkpoint
    final_checkpoint = checkpoint_mgr.save("completed", {
        "state": state.to_dict(),
        "summary": {
            "phases_completed": list(state.results.keys()),
            "total_results": len(state.results),
            "completion_time": datetime.now().isoformat()
        }
    })

    print(f"[DONE] 任务完成")
    print(f"[DONE] Trace ID: {state.trace_id}")
    print(f"[DONE] Checkpoint: {final_checkpoint}")

    # 输出报告路径
    reports_dir = os.path.join("reports", state.trace_id)
    print(f"[DONE] 报告目录: {reports_dir}")

    return state.to_dict()
```

## 完整示例代码

```python
#!/usr/bin/env python3
"""
长任务执行示例 - 使用 ccc-core 持久化基础设施

Author: mzdbxqh
"""

import os
import sys
from datetime import datetime

# 添加 ccc-core 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ccc-core"))

from persistence import (
    State,
    CheckpointManager,
    DataManager,
    ResumeManager,
    generate_trace_id
)


class LongRunningTask:
    """长任务执行器 - 支持断点续传"""

    def __init__(self, task_name: str, base_dir: str = ".", resume_trace_id: str = None):
        self.task_name = task_name
        self.base_dir = base_dir

        # 恢复模式或新建
        if resume_trace_id:
            self.trace_id = resume_trace_id
            self.resume_mode = True
        else:
            self.trace_id = generate_trace_id()
            self.resume_mode = False

        print(f"[INIT] Task: {task_name}")
        print(f"[INIT] Trace ID: {self.trace_id}")
        print(f"[INIT] Mode: {'RESUME' if self.resume_mode else 'NEW'}")

        # 初始化管理器
        self.state = State(self.trace_id)
        self.checkpoint_mgr = CheckpointManager(self.trace_id, base_dir)
        self.data_mgr = DataManager(self.trace_id, base_dir)
        self.resume_mgr = ResumeManager(self.trace_id, base_dir)

    def run(self):
        """执行主流程"""
        try:
            if self.resume_mode:
                self._resume_from_checkpoint()
            else:
                self._initialize()

            # 执行各阶段
            self._phase_planning()
            self._phase_data_collection()
            self._phase_analysis()
            self._phase_reporting()

            # 完成
            return self._finalize()

        except Exception as e:
            self._handle_error(e)
            raise

    def _initialize(self):
        """初始化阶段"""
        print("\n" + "="*50)
        print("PHASE: Initialization")
        print("="*50)

        self.state.mark_running()
        self.state.set_phase("initialization")
        self.state.set_step("setup")

        # 保存初始 checkpoint
        self.checkpoint_mgr.save("init", {
            "state": self.state.to_dict(),
            "task_name": self.task_name,
            "config": {"base_dir": self.base_dir}
        })

        print("[OK] 初始化完成")

    def _resume_from_checkpoint(self):
        """从 checkpoint 恢复"""
        print("\n" + "="*50)
        print("PHASE: Resume from Checkpoint")
        print("="*50)

        context = self.resume_mgr.get_resume_context()

        if not context["can_resume"]:
            raise ValueError(f"无法恢复 trace {self.trace_id}: {context['message']}")

        print(f"[RESUME] 从 checkpoint 恢复: {context['last_checkpoint']}")
        print(f"[RESUME] 当前阶段: {context['current_phase']}")
        print(f"[RESUME] 当前步骤: {context['current_step']}")
        print(f"[RESUME] 已完成步骤: {context['completed_steps']}")

        # 恢复状态
        checkpoint_data = self.resume_mgr.resume_from_checkpoint(context["last_checkpoint"])
        self.state = State.from_dict(checkpoint_data["state"])

        # 根据已完成的步骤跳过
        completed = context["completed_steps"]

        if "planning" in completed:
            print("[SKIP] planning 已完成")
        if "data_collection" in completed:
            print("[SKIP] data_collection 已完成")
        if "analysis" in completed:
            print("[SKIP] analysis 已完成")

        print("[OK] 恢复完成")

    def _phase_planning(self):
        """规划阶段"""
        if self.state.results.get("planning_completed"):
            print("\n[SKIP] planning 已跳过（已完成）")
            return

        print("\n" + "="*50)
        print("PHASE: Planning")
        print("="*50)

        self.state.set_phase("planning")
        self._save_step_checkpoint("planning", "started")

        # 执行规划逻辑
        plan = {"steps": ["step1", "step2", "step3"], "estimated_time": "30min"}

        # 保存结果
        self.state.add_result("planning_result", plan)
        self.data_mgr.save_result(self.task_name, "planning", plan)
        self._save_step_checkpoint("planning", "completed", plan)

        print("[OK] 规划完成")

    def _phase_data_collection(self):
        """数据收集阶段"""
        if self.state.results.get("data_collection_completed"):
            print("\n[SKIP] data_collection 已跳过（已完成）")
            return

        print("\n" + "="*50)
        print("PHASE: Data Collection")
        print("="*50)

        self.state.set_phase("data_collection")
        self._save_step_checkpoint("data_collection", "started")

        # 模拟长时间数据收集
        collected_items = []
        for i in range(5):
            print(f"[PROGRESS] 收集数据 {i+1}/5...")
            collected_items.append(f"item_{i}")
            # 每收集一部分保存一次 checkpoint
            if (i + 1) % 2 == 0:
                self._save_step_checkpoint(f"data_collection_partial_{i+1}", "in_progress", {
                    "items_so_far": collected_items.copy()
                })

        # 保存最终结果
        data = {"items": collected_items, "total": len(collected_items)}
        self.state.add_result("data_collection_result", data)
        self.data_mgr.save_result(self.task_name, "data_collection", data)
        self._save_step_checkpoint("data_collection", "completed", data)

        print("[OK] 数据收集完成")

    def _phase_analysis(self):
        """分析阶段"""
        if self.state.results.get("analysis_completed"):
            print("\n[SKIP] analysis 已跳过（已完成）")
            return

        print("\n" + "="*50)
        print("PHASE: Analysis")
        print("="*50)

        self.state.set_phase("analysis")
        self._save_step_checkpoint("analysis", "started")

        # 加载之前收集的数据
        data = self.data_mgr.load_result(self.task_name, "data_collection")
        if not data:
            raise ValueError("数据收集结果不存在")

        print(f"[DATA] 加载数据: {data['total']} 条")

        # 执行分析
        analysis = {"findings": ["finding1", "finding2"], "data_ref": data}

        self.state.add_result("analysis_result", analysis)
        self.data_mgr.save_result(self.task_name, "analysis", analysis)
        self._save_step_checkpoint("analysis", "completed", analysis)

        print("[OK] 分析完成")

    def _phase_reporting(self):
        """报告阶段"""
        print("\n" + "="*50)
        print("PHASE: Reporting")
        print("="*50)

        self.state.set_phase("reporting")
        self._save_step_checkpoint("reporting", "started")

        # 生成报告
        report = {
            "task": self.task_name,
            "trace_id": self.trace_id,
            "summary": self.state.results
        }

        self.data_mgr.save_result(self.task_name, "report", report)
        self._save_step_checkpoint("reporting", "completed", report)

        print("[OK] 报告生成完成")

    def _finalize(self):
        """完成任务"""
        print("\n" + "="*50)
        print("PHASE: Finalization")
        print("="*50)

        self.state.mark_completed()
        self.state.set_phase("completed")

        self.checkpoint_mgr.save("completed", {
            "state": self.state.to_dict(),
            "final_report": self.data_mgr.load_result(self.task_name, "report")
        })

        print("[DONE] 任务完成")
        print(f"[DONE] Trace ID: {self.trace_id}")
        print(f"[DONE] 报告: reports/{self.trace_id}/")

        return self.state.to_dict()

    def _handle_error(self, error):
        """处理错误"""
        print(f"\n[ERROR] {error}")
        self.state.mark_failed(str(error))
        self.checkpoint_mgr.save("failed", {
            "state": self.state.to_dict(),
            "error": str(error)
        })

    def _save_step_checkpoint(self, step: str, status: str, data: dict = None):
        """保存步骤 checkpoint"""
        checkpoint_name = f"step_{step}_{status}"
        checkpoint_data = {
            "state": self.state.to_dict(),
            "step": step,
            "status": status
        }
        if data:
            checkpoint_data["data"] = data

        filepath = self.checkpoint_mgr.save(checkpoint_name, checkpoint_data)
        print(f"[CHECKPOINT] 保存: {checkpoint_name}")


# 使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="长任务执行示例")
    parser.add_argument("--task-name", default="demo_task", help="任务名称")
    parser.add_argument("--resume", help="要恢复的 trace_id")
    parser.add_argument("--base-dir", default=".", help="基础目录")

    args = parser.parse_args()

    # 创建并执行任务
    task = LongRunningTask(
        task_name=args.task_name,
        base_dir=args.base_dir,
        resume_trace_id=args.resume
    )

    result = task.run()
    print(f"\n最终状态: {result['status']}")
```

## Checkpoint 策略

### 何时保存 Checkpoint

| 时机 | 建议 | 原因 |
|------|------|------|
| 阶段开始前 | 必须 | 记录进入状态，便于恢复定位 |
| 阶段完成后 | 必须 | 记录完成状态，避免重复执行 |
| 长时间操作中间 | 建议 | 防止操作中断导致全部丢失 |
| 重要数据生成后 | 必须 | 保护关键中间结果 |
| 错误发生时 | 必须 | 记录错误状态便于调试 |

### Checkpoint 命名规范

```
{step_name}_{status}  # 例如: step_planning_completed
{step_name}_partial_{n}  # 例如: step_data_collection_partial_10
{phase}_failed  # 例如: analysis_failed
init  # 初始化
completed  # 完成
failed  # 失败
```

### Checkpoint 数据内容

```python
{
    "state": state.to_dict(),  # 必须：完整状态
    "step": "step_name",       # 建议：步骤名称
    "status": "completed",     # 建议：状态标记
    "data": {...},             # 可选：相关数据
    "metadata": {...}          # 可选：元信息
}
```

## 错误处理

### 失败恢复模式

```python
def handle_failure_and_resume(trace_id, base_dir="."):
    """处理失败并准备恢复"""
    resume_mgr = ResumeManager(trace_id, base_dir)

    if not resume_mgr.can_resume():
        print("没有可恢复的 checkpoint")
        return None

    context = resume_mgr.get_resume_context()
    last_checkpoint = context["last_checkpoint"]

    # 分析失败原因
    checkpoint_data = resume_mgr.resume_from_checkpoint(last_checkpoint)
    state_data = checkpoint_data.get("state", {})

    if state_data.get("status") == "failed":
        error = state_data.get("metadata", {}).get("error", "未知错误")
        print(f"上次失败原因: {error}")

        # 决定恢复策略
        if "step_" in last_checkpoint and "_failed" in last_checkpoint:
            # 步骤失败，从该步骤重新开始
            step_name = last_checkpoint.replace("step_", "").replace("_failed", "")
            print(f"建议: 重新执行步骤 '{step_name}'")
            return {"strategy": "retry_step", "step": step_name}

    return {"strategy": "continue", "from_checkpoint": last_checkpoint}
```

### 优雅降级

```python
def execute_with_fallback(step_func, fallback_func, state, checkpoint_mgr):
    """执行步骤，失败时降级"""
    try:
        return step_func()
    except Exception as e:
        print(f"主流程失败: {e}")
        print("尝试降级方案...")

        # 保存失败状态
        checkpoint_mgr.save("step_failed", {
            "state": state.to_dict(),
            "error": str(e),
            "fallback": True
        })

        # 执行降级
        return fallback_func()
```

## Resume Flow

### 手动恢复流程

```bash
# 1. 查看可用的 traces
ls -la reports/

# 2. 检查特定 trace 的 checkpoints
python -c "
from ccc_core.persistence import ResumeManager
rm = ResumeManager('20260324_143052_a1b2c3')
print('Can resume:', rm.can_resume())
print('Last checkpoint:', rm.get_last_checkpoint())
print('Context:', rm.get_resume_context())
"

# 3. 恢复执行
python long_task.py --resume=20260324_143052_a1b2c3 --task-name=demo_task
```

### 自动恢复流程

```python
def auto_resume_latest(base_dir="."):
    """自动恢复最近的可恢复任务"""
    reports_dir = os.path.join(base_dir, "reports")

    if not os.path.exists(reports_dir):
        return None

    # 按时间排序查找
    for trace_id in sorted(os.listdir(reports_dir), reverse=True):
        resume_mgr = ResumeManager(trace_id, base_dir)
        if resume_mgr.can_resume():
            context = resume_mgr.get_resume_context()
            if context.get("current_state", {}).get("status") != "completed":
                return trace_id

    return None

# 使用
latest_trace = auto_resume_latest()
if latest_trace:
    print(f"自动恢复: {latest_trace}")
    task = LongRunningTask(task_name="demo", resume_trace_id=latest_trace)
    task.run()
```

## 输出结构

执行后生成的目录结构：

```
reports/
└── 20260324_143052_a1b2c3/           # trace_id 目录
    ├── checkpoints/                   # checkpoint 文件
    │   ├── init_143052.json
    │   ├── step_planning_started_143053.json
    │   ├── step_planning_completed_143055.json
    │   ├── step_data_collection_started_143056.json
    │   ├── step_data_collection_partial_2_143100.json
    │   ├── step_data_collection_partial_4_143145.json
    │   ├── step_data_collection_completed_143200.json
    │   ├── step_analysis_started_143201.json
    │   ├── step_analysis_completed_143305.json
    │   └── completed_143310.json
    └── data/                          # 数据文件
        ├── demo_task_planning.json
        ├── demo_task_data_collection.json
        ├── demo_task_analysis.json
        └── demo_task_report.json
```

## 最佳实践

### 1. Checkpoint 粒度

- **粗粒度**: 每个阶段保存一次（适合简单任务）
- **细粒度**: 每个子步骤保存（适合复杂任务）
- **混合粒度**: 阶段 + 关键中间点（推荐）

### 2. 数据管理

- 大数据量使用 DataManager 单独存储
- 状态元数据使用 CheckpointManager 存储
- 避免在 checkpoint 中存储重复数据

### 3. 恢复策略

- 幂等设计：同一 checkpoint 恢复多次结果一致
- 跳过已完成：检查状态避免重复执行
- 部分恢复：支持从中间步骤恢复

### 4. 监控和日志

```python
# 记录关键事件
print(f"[CHECKPOINT] Saved: {checkpoint_name}")
print(f"[PHASE] Entering: {phase_name}")
print(f"[PROGRESS] {completed}/{total} ({percent}%)")

# 定期输出状态
if step_count % 10 == 0:
    print(f"[STATUS] Current: {state.current_phase}/{state.current_step}")
```

### 5. 测试建议

```python
def test_checkpoint_resume():
    """测试 checkpoint 恢复功能"""
    # 1. 创建任务并执行部分步骤
    task = LongRunningTask("test_task")
    task._initialize()
    task._phase_planning()

    # 2. 模拟中断，创建新实例恢复
    trace_id = task.trace_id
    task2 = LongRunningTask("test_task", resume_trace_id=trace_id)

    # 3. 验证恢复成功
    assert task2.state.current_phase == "planning"
    assert "planning_completed" in task2.state.results

    # 4. 继续执行剩余步骤
    task2._phase_data_collection()
    task2._finalize()
```

## 参考

- **State 类**: ccc-core/persistence/state.py
- **CheckpointManager**: ccc-core/persistence/checkpoint.py
- **DataManager**: ccc-core/persistence/data_manager.py
- **ResumeManager**: ccc-core/persistence/resume_manager.py

# Integration Test: Full Workflow

## Test 1: Happy Path

```bash
# Step 1: Init
/cmd-init "做一个简单的文件读取Skill"
# Expected: Intent created with quality score > 80

# Step 2: Design
/cmd-design
# Expected: Blueprint created with checkpoint passed

# Step 3: Build
/cmd-build
# Expected: Delivery created with compliance score > 80
```

## Test 2: Quick Workflow

```bash
/cmd-quick "做一个简单的文件读取Skill"
# Expected: Full workflow completes, Delivery ready
```

## Test 3: Iteration

```bash
/cmd-init "做一个部署工具"
/cmd-design
/cmd-iterate "增加回滚功能"
# Expected: New Blueprint iteration created
```

## Test 4: Status Commands

```bash
/cmd-init "测试项目"
/cmd-status
/cmd-status-graph
/cmd-status-trace
# Expected: All status commands show correct information
```

## Test 5: Validation and Review

```bash
/cmd-init "验证测试"
/cmd-design
/cmd-validate
/cmd-review
/cmd-diff --from=INT-001 --to=current
# Expected: Validation and review complete successfully
```

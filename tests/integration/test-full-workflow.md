# Integration Test: Full Workflow

## Test 1: Happy Path

```bash
# Step 1: Init
/ccc:init "做一个简单的文件读取Skill"
# Expected: Intent created with quality score > 80

# Step 2: Design
/ccc:design
# Expected: Blueprint created with checkpoint passed

# Step 3: Build
/ccc:build
# Expected: Delivery created with compliance score > 80
```

## Test 2: Quick Workflow

```bash
/ccc:quick "做一个简单的文件读取Skill"
# Expected: Full workflow completes, Delivery ready
```

## Test 3: Iteration

```bash
/ccc:init "做一个部署工具"
/ccc:design
/ccc:iterate "增加回滚功能"
# Expected: New Blueprint iteration created
```

## Test 4: Status Commands

```bash
/ccc:init "测试项目"
/ccc:status
/ccc:status-graph
/ccc:status-trace
# Expected: All status commands show correct information
```

## Test 5: Validation and Review

```bash
/ccc:init "验证测试"
/ccc:design
/ccc:validate
/ccc:review
/ccc:diff --from=INT-001 --to=current
# Expected: Validation and review complete successfully
```

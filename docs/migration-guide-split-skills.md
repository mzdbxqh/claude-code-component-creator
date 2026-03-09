# Skill 拆分迁移指南

## report-renderer 迁移

**旧用法**:
```
/report-renderer docs/reviews/result.json
```

**新用法**:
```
/review-report-renderer docs/reviews/result.json
/architecture-report-renderer docs/arch/result.json
/dependency-report-renderer docs/deps/result.json
/migration-report-renderer docs/migration/result.json
```

## 迁移收益
- Token 消耗降低 87-92%
- 触发更精准
- 加载更快

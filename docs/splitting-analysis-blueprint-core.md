# blueprint-core 拆分分析

## 当前状态
- 总行数: 414 行
- 处理多种组件类型 (Skill/Command/Hook)

## 知识域分析
基于实际内容，blueprint-core 主要是通用的 blueprint 生成器，不需要按组件类型拆分。

## 结论
blueprint-core 当前设计合理，暂不拆分。
原因：
1. 工作流统一 (验证→生成→输出)
2. 知识域共享率高 (>60%)
3. 行数 414 < 450 (软限制内)

## 建议
使用 references/ 优化即可，无需拆分。

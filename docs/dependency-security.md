# 生产依赖安全评估

> 最近评估：2026-08-22
> 范围：`apps/mini` 的小程序与 H5 构建依赖

## 当前结论

`npm audit --omit=dev --json` 的当前统计为 6 项 critical、2 项 high、11 项 moderate。公开发布仍被阻断。

- npm 当前最新的 Taro 版本为 4.2.1；在该版本内没有可直接升级的上游修复。
- `@tarojs/components@4.2.1` 精确依赖 `swiper@11.1.15`，而审计将 `swiper@6.5.1` 至 `<12.1.2` 标记为 critical。
- H5 依赖链还包含 `lodash-es@4.17.21`；它处于当前 high 审计范围。
- 审计给出的自动修复会将 Taro 降至 3.6.40。这是跨主版本迁移，不能作为自动修复执行。

项目源代码目前没有直接导入 `Swiper`、`swiper` 或 `lodash-es`。这只降低直接调用风险，不能消除供应链风险。

## 已排除的做法

- 不运行 `npm audit fix --force`。
- 不用 `overrides` 强制把 Taro 锁定的 Swiper 11 升到 12：该操作跨越上游固定版本，必须先有 Taro 官方兼容说明和独立回归结果。
- 不为了让审计通过而降级 Taro 3，或将实际运行时依赖错误地移到 `devDependencies`。

## 自动化验证

| 命令 | 用途 | 通过条件 |
| --- | --- | --- |
| `npm run audit:prod:baseline` | 生产依赖审计回归 | 不超过已记录的风险基线 |
| `npm run audit:prod:release` | 发布安全门槛 | `critical` 与 `high` 均为 0 |
| `npm run verify:upgrade` | 依赖兼容回归 | 前端检查、小程序/H5 构建、H5 UITest 全部通过 |

CI 对每个 PR 和 `develop`、`daily_dev` 推送执行基线审计与 `verify:upgrade`。基线审计用于防止风险增加；发布门槛仍保持严格阻断。

## 后续决策条件

当 Taro 发布兼容修复时，在隔离分支执行以下步骤：

1. 将全部 `@tarojs/*` 包统一升级到相同版本，重新生成 lockfile；不得混用版本。
2. 运行 `npm run audit:prod:release`。若仍有 high 或 critical，则停止，不提交升级。
3. 运行 `npm run verify:upgrade`，并在微信开发者工具中验证首页、宠物创建、学习、照料和错误提示等已实现流程。
4. 记录包体积变化，确认 H5 首屏预算与微信小程序分包预算未劣化。
5. 在 PR 中附上审计前后报告、构建结果与回滚方式。

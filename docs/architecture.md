# 技术架构

> 决策日期：2026-08-21
> 适用范围：MVP 微信小程序，以及后续移动端迁移

## 1. 已确认的技术选型

| 范围 | 选型 | 责任 |
| --- | --- | --- |
| 小程序前端 | Taro + React + TypeScript | 页面、交互、请求状态与无障碍体验 |
| 后端 API | FastAPI + Pydantic | 鉴权、输入校验、领域规则与 OpenAPI 契约 |
| 关系数据 | PostgreSQL + SQLAlchemy | 事务、账本、宠物生命周期与排行榜快照 |
| 缓存与协调 | Redis（M1 起） | 限流、缓存、幂等协调与异步任务状态 |
| 异步任务 | Python worker（M2 前确定具体实现） | 定时结算、通知和可重试的慢任务 |
| 前端测试 | Vitest + Testing Library；Playwright（H5 验证） | 单元测试和浏览器端到端验证 |
| 后端测试 | Pytest | API 与领域规则单元/集成测试 |

## 2. 责任边界

```text
Taro React 小程序 / 后续移动端
             │ HTTPS + OpenAPI
             ▼
       FastAPI 服务端
             │ 事务与审计
             ▼
 PostgreSQL（事实账本与状态）
             │
             └── Redis / Worker（限流、定时结算、通知）
```

- 客户端不能裁决积分、库存、宠物健康、死亡、排行榜或权限；它只显示服务端结果并提交用户操作。
- FastAPI 是唯一的业务规则权威。积分和库存以不可变账本为事实来源，状态变更采用事务和幂等键。
- API 契约以 FastAPI 自动生成的 OpenAPI 为准。前端通过生成的 TypeScript 类型或受版本控制的客户端调用接口，不复制后端的数值或状态机规则。
- 后续迁移移动端时，优先复用 API、类型、请求层、设计令牌和非 UI 工具函数；小程序平台 API、原生能力和具体页面可按平台重新实现。

## 3. 仓库布局

```text
apps/mini/             Taro React 微信小程序
services/api/          FastAPI 服务端
docs/                  架构与产品文档
.github/workflows/     CI
```

当前阶段不建立“共享业务规则”前端包，避免客户端与服务端出现两套积分或宠物状态逻辑。

## 4. 本地开发

前置条件：Node.js 20+、Python 3.11+、微信开发者工具（用于真机/小程序调试）。

```bash
make web-install
npm run dev:mini

make api-install
make api-run
```

常用检查：

```bash
make web-check
make api-check
make api-test
```

H5 预览固定在 `http://127.0.0.1:10087`，避免与本机常用的 10086 端口冲突。`npm run test:ui` 用 H5 构建启动 Playwright 冒烟测试；微信小程序的真机能力、登录授权和平台 API 还需在微信开发者工具中补充自动化验证。

依赖升级后运行 `npm run verify:upgrade`；生产依赖审计可分别通过 `npm run audit:prod:baseline`（防止风险劣化）和 `npm run audit:prod:release`（发布门槛）执行。

## 5. 依赖安全门槛

- 依赖锁文件必须提交，CI 使用 `npm ci` 安装前端依赖。
- 2026-08-22 的 `npm audit --omit=dev` 报告 6 项 critical、2 项 high、11 项 moderate 风险。Taro 4.2.1 是 npm 当前最新版本，但它精确锁定 `swiper@11.1.15`；该版本仍处于严重漏洞影响范围。审计建议降至 Taro 3.6.40，不属于可直接采用的兼容修复。
- 当前基线不得公开发布。未取得兼容的上游修复或经评审的替代方案前，执行 `npm run audit:prod:release` 必须失败；该命令要求 critical 与 high 均为 0。
- `npm run audit:prod:baseline` 使用 [security/production-audit-baseline.json](../security/production-audit-baseline.json) 检测审计风险是否劣化，并在 CI 的每个 PR 与目标分支推送中执行。基线检查通过不代表可以发布。
- 依赖升级使用 `npm run verify:upgrade`，依次执行格式、静态检查、UnitTest、小程序构建、H5 构建与 Playwright UITest。不得使用 `npm audit fix --force`、强制覆盖 `swiper` 主版本或任意降级来掩盖问题。
- 完整评估、已知限制与后续决策记录在 [docs/dependency-security.md](dependency-security.md)。

## 6. 性能基线

- 当前空白 H5 骨架入口包约为 301 KiB，已超过构建器默认 244 KiB 建议值。M1 前应设定首屏性能预算，并在新增页面、媒体、图表或 SDK 时重新测量；禁止仅靠关闭警告处理。

## 7. 后续决策

- M1 前：确定微信登录的服务端换取流程、会话策略、PostgreSQL 托管服务和对象存储。
- M2 前：确定 Redis 部署、异步 worker 方案、定时结算的重试与监控策略。
- 迁移移动端前：根据原生能力、性能和发布需求，在 Taro React Native 与独立 React Native/Expo UI 层之间评估；后端 API 和数据边界保持不变。

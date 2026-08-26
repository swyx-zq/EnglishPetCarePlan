# English Pet Care Plan — 前后端架构图

> 更新日期：2026-08-22
> 目的：说明当前实现与 M1/M2 目标架构的边界。虚线标注的链路或组件尚未实现，不能视为可用功能。

## 1. 系统总览

```mermaid
flowchart LR
    subgraph frontend["前端客户端"]
        mini["微信小程序\nTaro + React + TypeScript"]
        h5["H5 回归目标\n同一套 Taro 页面"]
        devtools["微信开发者工具\n编译与真机调试"]
    end

    subgraph apiLayer["服务端 API"]
        api["FastAPI\n/api/v1\n当前仅 health"]
        contract["OpenAPI 契约\nPydantic 输入输出校验"]
        domain["领域服务\n学习计划、积分账本、Momo 记忆\nM1/M2 规划中"]
    end

    subgraph dataLayer["数据与协调"]
        postgres[("PostgreSQL\n词库、学习记录、账本与业务事实\nM1 规划中")]
        redis[("Redis\n限流、缓存、幂等协调\nM1 规划中")]
        worker["Python Worker\n延迟复习、可选通知、重试\nM1 规划中"]
    end

    mini -->|"本地构建"| devtools
    mini -.->|"M1：HTTPS + OpenAPI"| api
    h5 -.->|"M1：HTTPS + OpenAPI"| api
    api -->|"已实现：路由与配置"| contract
    contract -.->|"M1/M2：授权后调用"| domain
    domain -.->|"M1：事务读写"| postgres
    domain -.->|"M1：限流与幂等协调"| redis
    worker -.->|"M1：复习与审计读写"| postgres
    worker -.->|"M1：任务协调"| redis
```

### 当前实现状态

| 区域                        | 当前状态                                                | 责任边界                                                   |
| --------------------------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| 微信小程序 / H5             | 已有 Taro React 页面、构建、UnitTest 和 H5 UITest 骨架  | 只负责展示、输入与请求状态；不能裁决积分、库存或宠物状态。 |
| FastAPI                     | 已有应用工厂、`/api/v1/health`、配置模型和 OpenAPI 入口 | 后续是所有业务规则的唯一权威。                             |
| PostgreSQL / Redis / Worker | 尚未接入                                                | 仅为 M1/M2 目标架构，当前没有可连接的业务数据源。          |

## 2. 业务请求与安全边界

```mermaid
sequenceDiagram
    participant client as "小程序或 H5"
    participant api as "FastAPI API"
    participant schema as "Pydantic 与授权校验"
    participant domain as "领域服务"
    participant store as "PostgreSQL 账本"

    Note over client,store: "以下学习计划、积分和记忆请求流程为 M1/M2 目标，当前尚未实现"
    client->>api: "HTTPS 请求与幂等键"
    api->>schema: "验证会话、资源归属和输入"
    schema->>domain: "传递已验证命令"
    domain->>store: "事务写入不可变账本与状态"
    store-->>domain: "提交结果"
    domain-->>api: "状态快照与审计标识"
    api-->>client: "可展示的结果或错误码"
```

安全规则：客户端不得本地结算积分、学习计划、复习、记忆、健康、疾病、死亡或排行榜。所有写入在服务端完成身份验证、资源归属校验、内容/状态校验和幂等控制后，才可进入账本或状态存储。

## 3. 开发与质量门禁

```mermaid
flowchart LR
    change["前后端改动"] --> checks["本地检查\nformat lint typecheck UnitTest"]
    checks --> builds["Taro 小程序与 H5 构建"]
    builds --> ui["Playwright H5 UITest\n微信开发者工具补充验证"]
    ui --> ci["GitHub Actions CI"]
    ci --> audit["生产依赖审计基线"]
    audit --> gate["发布门槛\nhigh 与 critical 必须为 0"]
```

- `npm run verify:upgrade`：执行前端检查、小程序构建、H5 构建与 Playwright UITest。
- `npm run audit:prod:baseline`：阻止生产依赖审计风险超过当前基线。
- `npm run audit:prod:release`：当前会因 Taro 依赖的高风险审计结果而失败，因此公开发布仍被阻断。

## 4. 后续更新规则

当 M1 接入登录、词库、学习任务与积分账本时，应将虚线请求链路改为实线，并补充实际的认证方式、数据库迁移和错误码。当延迟复习调度接入后，再将 Worker 与 Redis 链路标记为已实现。详细架构说明见 [docs/architecture.md](docs/architecture.md)。

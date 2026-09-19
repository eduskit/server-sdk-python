# SDK 总览

面向客户自有后端的 B 端 Server SDK。一份依赖，两个 Client：

| 属性 | 后端 | 默认地址 | 职责 |
|------|------|----------|------|
| `client` | edu `server-api` | `http://localhost:3112` | 注册 C 端用户、课堂/成员/课件/权限；本地签课堂 Token |
| `whiteboardClient` | 白板 `server-api` | `http://localhost:3012` | 录制、截图、文件转码；本地签 Room Token |

两侧 HTTP 鉴权头相同（`x-app-key` + `x-app-secret`），但 **baseUrl、appId 和凭证必须分侧配置**。以下两个方法完全本地执行：

- 课堂 `auth.issueToken`：签发 C 端 `accessToken`，给 EduSDK 调 sdk-api `:3100`
- 白板 `auth.issueRoomToken`：签发 Room Token，给 DrawKit 调 sdk-api `:3000`

本地 JWT 固定使用 HS256，并分别绑定 `eduskit-edu` / `eduskit-room` audience。`appSecret` 只能保存在客户后端，禁止下发到浏览器、App 或小程序。

## 语言包

| 语言 | 文档 | 包名 |
|------|------|------|
| Node.js | [server-sdk-node](https://github.com/eduskit/server-sdk-node) | `@eduskit/server-sdk` |
| Python | [server-sdk-python](https://github.com/eduskit/server-sdk-python) | `eduskit` |
| Java | [server-sdk-java](https://github.com/eduskit/server-sdk-java) | `com.eduskit:server-sdk` |
| Go | [server-sdk-go](https://github.com/eduskit/server-sdk-go) | `github.com/eduskit/server-sdk-go` |
| PHP | [server-sdk-php](https://github.com/eduskit/server-sdk-php) | `eduskit/server-sdk-php` |

方法表见 [api.md](api.md)。Node.js 是参考实现，其它语言只做惯用命名平移。

## 约定

- JSON 字段保持 **camelCase**（`eduUserId`、`originId`、`startsAt`），与 server-api 一致。
- 成功响应拆信封 `{ code, message, data, traceId? }`，方法返回 **`data`**。
- 白板成功体可能没有 `traceId`，SDK 会从响应头 `x-trace-id` 回填到 `lastTraceId`。
- 失败抛 `EduskitError`：`status`、`errorCode`、`message`、`traceId`、`path`、`source`（`classroom` / `whiteboard`）。
- 未配置的一侧被访问时立即抛 `SDK_CLIENT_NOT_CONFIGURED`，不发请求。
- 不在 HTTP Body 传 `appId`；配置中的 `appId` 只用于本地签 Token。
- v1 不做自动重试（`start` / `end` / 开录等非幂等）。

## 不做

- 不调 C 端 sdk-api（课堂 `:3100`、白板 `:3000`）
- 不调 console-api / admin-api
- 不封装 Webhook HMAC 验签

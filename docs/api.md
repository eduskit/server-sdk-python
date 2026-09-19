# API 方法表

语义方法与 HTTP 的对应关系。各语言命名见各包 README（Python 为 snake_case，Go 为 PascalCase）。

## `client`（课堂）

| 方法 | HTTP | 说明 |
|------|------|------|
| `users.register` | `POST /v1/users` | 注册或按 `originId` 幂等更新 C 端用户 |
| `auth.issueToken` | 本地 | 为已注册用户签发 C 端 accessToken，不发 HTTP |
| `classrooms.create` | `POST /v1/classrooms` | 创建课堂 |
| `classrooms.start` | `POST /v1/classrooms/{id}/start` | 开课 |
| `classrooms.end` | `POST /v1/classrooms/{id}/end` | 结课 |
| `classrooms.members.add` | `POST /v1/classrooms/{id}/members` | 添加成员 |
| `classrooms.members.list` | `GET /v1/classrooms/{id}/members` | 列出成员 |
| `classrooms.members.replaceStudents` | `PUT /v1/classrooms/{id}/members/students` | 全量替换学生花名册 |
| `classrooms.permissions.get` | `GET .../members/{eduUserId}/permissions` | 查询成员权限 |
| `classrooms.permissions.set` | `POST .../members/{eduUserId}/permissions` | 代老师 grant/revoke |
| `classrooms.permissions.clear` | `DELETE .../permissions/{permission}` | 清除权限覆盖 |
| `classrooms.coursewares.list` | `GET /v1/classrooms/{id}/coursewares` | 列出已绑定课件 |
| `classrooms.coursewares.bind` | `POST /v1/classrooms/{id}/coursewares` | 绑定课件（幂等） |
| `classrooms.coursewares.unbind` | `DELETE /v1/classrooms/{id}/coursewares` | 解绑课件 |
| `app.getUiConfig` | `GET /v1/app/ui-config` | 获取 App UI |
| `app.setUiConfig` | `PUT /v1/app/ui-config` | 设置 App UI（不影响已创建课堂快照） |

### 常用入参

**users.register**

| 字段 | 必填 | 说明 |
|------|------|------|
| `nickname` | 是 | 昵称 |
| `avatar` | 是 | http(s) 头像 URL |
| `originId` | 否 | 客户系统用户 ID，`(appId, originId)` 幂等 |

**auth.issueToken**

| 字段 | 必填 | 说明 |
|------|------|------|
| `eduUserId` | 是 | `users.register` 返回的平台 C 端用户 ID |
| `originId` | 否 | 客户系统用户 ID，仅作为 Token 附加 claim |
| `role` | 否 | `teacher` / `assistant` / `student` / `inspector`，仅写入 JWT 提示 |
| `expiresIn` | 否 | 秒，默认 86400 |

**classrooms.create** 必填：`name`、`startsAt`、`endsAt`、`teacherEduUserId`。可选：`resolution`、`maxOnStage`、`videoOnly`、`recordMode`、`joinPolicy`、`studentEduUserIds`、`coursewareIds` 等，见 [edu-server-api.yaml](../spec/edu-server-api.yaml)。

**permissions.set** 必填：`permission`（`camera` / `microphone` / `whiteboard` / `screen_share` / `chat`）、`effect`（`grant` / `revoke`）、`operatorEduUserId`（课堂内老师或助教）。

## `whiteboardClient`（白板）

| 方法 | HTTP | 说明 |
|------|------|------|
| `auth.issueRoomToken` | 本地 | 签发 Room Token，不发 HTTP |
| `recordings.start` | `POST /v1/rooms/{roomId}/recording/start` | 开始录制 |
| `recordings.stop` | `POST /v1/rooms/{roomId}/recording/stop` | 停止录制（不自动出片） |
| `recordings.list` | `GET /v1/rooms/{roomId}/recordings` | 列出房间录制 |
| `recordings.get` | `GET /v1/recordings/{recordingId}` | 录制详情 |
| `recordings.registerMediaAsset` | `POST /v1/recordings/{id}/media-assets` | 登记媒体 URL |
| `recordings.deleteMediaAsset` | `DELETE .../media-assets/{assetId}` | 删除媒体资产 |
| `recordings.enqueueVideoExport` | `POST /v1/recordings/{id}/video-exports` | 入队视频导出 |
| `recordings.getVideoExport` | `GET .../video-exports/{jobId}` | 查询导出任务 |
| `captures.create` | `POST /v1/rooms/{roomId}/captures` | 创建页截图 |
| `captures.list` | `GET /v1/rooms/{roomId}/captures` | 列出截图 |
| `files.convert` | `POST /v1/files/convert` | 提交转码 |
| `files.getConvertJob` | `GET /v1/files/convert/{jobId}` | 查询转码任务 |

### 常用入参

**auth.issueRoomToken** 必填：`roomId`、`userId`、`role`（`host` / `participant` / `observer`）。可选：`expiresIn`（秒，最小 60，默认 3600）。

**recordings.stop** 必填：`recordingId`。

**files.convert** 至少提供 `sourceUrl` 或 `objectKey`。可选：`fileName`、`clientReference`。

录制出片流程：`start` → `stop` → `enqueueVideoExport` → 轮询 `getVideoExport` 或等 Webhook。

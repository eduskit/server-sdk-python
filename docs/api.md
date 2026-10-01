# API 方法表

语义方法与 HTTP 的对应关系。GET/DELETE 的标识放 query；POST/PUT/PATCH 的标识与业务字段放 JSON body。SDK 将方法的 ID 参数写入相应位置，对外方法签名不变。各语言命名见各包 README（Python 为 snake_case，Go 为 PascalCase）。

## `client`（课堂）

| 方法 | HTTP | 说明 |
|------|------|------|
| `users.register` | `POST /v1/users` | 注册或按 `originId` 幂等更新 C 端用户 |
| `auth.issueToken` | `LOCAL HS256 (eduskit-edu)` | 为已注册用户签发 C 端 accessToken，不发 HTTP |
| `classrooms.create` | `POST /v1/classrooms` | 创建课堂 |
| `classrooms.start` | `POST /v1/classrooms/start` | 开课 |
| `classrooms.end` | `POST /v1/classrooms/end` | 结课 |
| `classrooms.members.add` | `POST /v1/classrooms/members` | 添加成员 |
| `classrooms.members.list` | `GET /v1/classrooms/members` | 列出成员 |
| `classrooms.members.replaceStudents` | `PUT /v1/classrooms/members/students` | 全量替换学生花名册 |
| `classrooms.permissions.get` | `GET /v1/classrooms/members/permissions` | 查询成员权限 |
| `classrooms.permissions.set` | `POST /v1/classrooms/members/permissions` | 代老师 grant/revoke |
| `classrooms.permissions.clear` | `DELETE /v1/classrooms/members/permissions` | 清除权限覆盖 |
| `classrooms.coursewares.list` | `GET /v1/classrooms/coursewares` | 列出已绑定课件 |
| `classrooms.coursewares.bind` | `POST /v1/classrooms/coursewares` | 绑定课件（幂等） |
| `classrooms.coursewares.unbind` | `DELETE /v1/classrooms/coursewares` | 解绑课件 |
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
| `auth.issueRoomToken` | `LOCAL HS256 (eduskit-room)` | 签发 Room Token，不发 HTTP |
| `recordings.start` | `POST /v1/rooms/recording/start` | 开始录制 |
| `recordings.stop` | `POST /v1/rooms/recording/stop` | 停止录制（不自动出片） |
| `recordings.list` | `GET /v1/rooms/recordings` | 列出房间录制 |
| `recordings.get` | `GET /v1/recordings` | 录制详情 |
| `recordings.registerMediaAsset` | `POST /v1/recordings/media-assets` | 登记媒体 URL |
| `recordings.deleteMediaAsset` | `DELETE /v1/recordings/media-assets` | 删除媒体资产 |
| `recordings.enqueueVideoExport` | `POST /v1/recordings/video-exports` | 入队视频导出 |
| `recordings.getVideoExport` | `GET /v1/recordings/video-exports` | 查询导出任务 |
| `captures.create` | `POST /v1/rooms/captures` | 创建页截图 |
| `captures.list` | `GET /v1/rooms/captures` | 列出截图 |
| `files.convert` | `POST /v1/files/convert` | 提交转码 |
| `files.getConvertJob` | `GET /v1/files/convert` | 查询转码任务 |

### 常用入参

**auth.issueRoomToken** 必填：`roomId`、`userId`、`role`（`host` / `participant` / `observer`）。可选：`expiresIn`（秒，最小 60，默认 3600）。

**recordings.stop** 必填：`recordingId`。

**files.convert** 至少提供 `sourceUrl` 或 `objectKey`。可选：`fileName`、`clientReference`。

录制出片流程：`start` → `stop` → `enqueueVideoExport` → 轮询 `getVideoExport` 或等 Webhook。

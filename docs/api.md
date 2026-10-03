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

本地签发的 JWT 必填 `access_generation: null`，适用于共享房间；私有作品 generation 必须
通过白板授权服务从当前授权读取后签发。本地方法不签发私有权限。

**recordings.stop** 必填：`recordingId`。

**files.convert** 至少提供 `sourceUrl` 或 `objectKey`。可选：`fileName`、`clientReference`。

录制出片流程：`start` → `stop` → `enqueueVideoExport` → 轮询 `getVideoExport` 或等 Webhook。

## 私有教学白板与固定作品

Node.js 的 `whiteboardClient.rooms` 新增以下方法。Python、Java、Go、PHP 使用各语言惯用命名，对应完全相同的 HTTP body/response；完整字段见 [白板 OpenAPI](../spec/whiteboard-server-api.yaml)。所有请求使用 `x-app-key` 与 `x-app-secret`，应用归属来自服务端凭证校验，body 不能传 `appId` 或令牌授权版本。

| 方法 | POST 路由 | 语义 |
|---|---|---|
| `provisionPrivateRoom(roomId, assignmentId)` | `/v1/rooms/private` | 创建不可变作业私有房间；不能转换已有共享房间 |
| `changePrivateRoomGrant(roomId, input)` | `/v1/rooms/private/grants` | 精确 requestId 回执与 expectedGeneration CAS；grant 必传 role，revoke 禁止 role |
| `getPrivateRoomAccess(roomId, userId)` | `/v1/rooms/private/access/query` | 查询当前授权；未授权返回 grant=null |
| `issuePrivateRoomToken(roomId, input)` | `/v1/rooms/private/token` | HTTP 查询最新授权后签发；不会使用本地共享房间签名器 |
| `sealPrivateRoom(roomId)` | `/v1/rooms/private/seal` | 永久停止新写入；重复返回原冻结水位与时间 |
| `createFrozenSnapshot(roomId, snapshotId)` | `/v1/rooms/private/snapshots` | 封写后注册独立固定作品任务 |
| `initializePrivateWorkspace(roomId, assignmentId, sourceSnapshotId)` | `/v1/rooms/private/initializations` | 原子创建独立私有工作房间；显式 null 创建空文档，作品 ID 复制已 ready 的同 app 固定作品 |
| `schedulePrivateRoomWrites(roomId, requestId, opensAt, closesAt)` | `/v1/rooms/private/write-window` | 配置唯一不可变的作答区间；无区间时文档只读 |
| `getPrivateWorkspaceInitialization(roomId)` | `/v1/rooms/private/initializations/query` | 查询初始化状态；ready 前无法授权、写入或封卷，不返回正文/下载地址 |
| `getFrozenSnapshot(roomId, snapshotId)` | `/v1/rooms/private/snapshots/query` | 查询 pending/running/ready/failed 状态与引用 |
| `getFrozenSnapshotDownload(roomId, snapshotId)` | `/v1/rooms/private/snapshots/download` | ready 时签发 60 秒私有下载 URL |

`expectedGeneration`、`generation`、`frozenSeq`、`sizeBytes` 全部是规范十进制字符串，不能转为 JavaScript Number。授权版本上限为 signed int64；初次授予使用 expectedGeneration="0"，成功返回正版本。相同 requestId 重试必须保持完整请求一致；旧请求回执不会重新生效已被后来命令撤销的授权。业务服务需要持久化 requestId 与期望版本，SDK 不执行自动重试。

尚无授权时也可以使用 `action="revoke"`、`expectedGeneration="0"` 建立撤销水位，返回 generation="1"、role="observer"、revoked=true。这是无权限的撤销记录，阻止随后到达的首次授权；不会授予 observer 权限。已存在授权的撤销保留原 role 并增加 generation。业务后台应先记录可能发出的授权意图，再在成员移除同事务中预约撤权，以处理外部授权回执丢失和授权/退出竞争。

私有 token 的 expiresIn 可省略；显式提供时必须为 60–604800 的整数，null 被拒绝。共享房间 `auth.issueRoomToken` 仍为本地签名，显式 access_generation=null；私有房间必须调用 `rooms.issuePrivateRoomToken`，由服务器写入最新正版本并在每次房间请求及写事务中验证。

固定作品不是协作 checkpoint。作品关联 assignmentId、冻结水位和时间；ready 后对象键、checksum、sizeBytes 与 completedAt 不可变。非 ready 状态的 objectKey/checksum/completedAt 为 ""、sizeBytes="0"。只有 ready 可以取得下载链接，未就绪返回冲突错误；签名 URL 不应持久化或写入日志。SDK 只返回状态和引用，不拉取 workspace 正文。

工作版本初始化以新 roomId 绑定 assignmentId 和 sourceSnapshotId，相同完整命令幂等，不同来源/作业冲突；不能对已有房间追加初始化。同一 assignmentId 可以拥有多个独立工作房间，旧作品和旧授权不会被复制。所有语言均要求显式提供第三个参数：Node.js/Java/PHP 为 null、Python 为 None、Go 为 nil（复制时 Go 传 string 指针），不能省略字段。Java HTTP 序列化保留显式 null。

初始化 metadata 的 sourceSnapshotId、checkpointId、completedAt、lastError 是必有的 nullable 字段；待完成的 checkpointId/completedAt 为 null，ready 才有独立 server checkpoint 0。status 为 pending/running/ready/failed，attemptCount 为最多 3 次的整数；失败只返回受控错误标识。业务方轮询到 ready 后才能单独 grant 和签发 token，初始化不会继承源房间成员或替业务方裁决模板/作业来源权限。

应用凭证能管理应用内私有房间，业务方必须在调用前验证课堂成员、作业归属及提交/批阅权限。五语言测试验证路由和参数，不代表教学业务流程或真实对象存储已经验收。当前修改是本地开发源码与归档，未发布到包仓库。


私有文档初始化 ready 或取得 grant 不会自动允许新写入。使用 `schedulePrivateRoomWrites`（Python `schedule_private_room_writes`，Go `SchedulePrivateRoomWrites`）显式提供四个参数。opensAt/closesAt 必须是规范 UTC ISO 毫秒字符串，closesAt > opensAt；SDK 保留原字符串，不转换时区、不设置默认期限。相同 room/request/区间重发返回原回执，改变 requestId/区间冲突；不能延长、重开或给已 seal 房间首次开窗口。新工作版本的新房间需独立设置窗口。绘图、演示和客户端 checkpoint 由白板数据库时刻裁定 opensAt <= now < closesAt，截止拒绝新写入不依赖任务调度；纯回执重放、当前授权的读取和服务器基线/作品物化可继续。

# eduskit

Python B 端 Server SDK。`sdk.client` 调课堂 server-api，`sdk.whiteboard_client` 调白板 server-api。

方法名为 snake_case；**请求/响应 JSON 字段仍为 camelCase**（`originId`、`eduUserId`）。

概念与方法表见 [docs/overview.md](docs/overview.md)、[docs/api.md](docs/api.md)。

## 安装

```bash
pip install -e .
```

要求 Python 3.9+，无第三方运行时依赖（标准库 `urllib`）。

```bash
PYTHONPATH=. python3 -m unittest tests.test_eduskit -v
```

## 初始化

```python
from eduskit import Eduskit, EduskitError

sdk = Eduskit(
    timeout_ms=10_000,
    lang="zh-CN",
    client={
        "base_url": "http://localhost:3112",
        "app_id": "app_edu",
        "app_key": "edu_key",
        "app_secret": "edu_secret",
    },
    whiteboard_client={
        "base_url": "http://localhost:3012",
        "app_id": "app_wb",
        "app_key": "wb_key",
        "app_secret": "wb_secret",
    },
)
```

配置字典键是 snake_case（`base_url` / `app_id` / `app_key` / `app_secret`）。两侧均可选。

## 课堂 `sdk.client`

```python
user = sdk.client.users.register(
    originId="stu_001",
    nickname="小明",
    avatar="https://example.com/a.png",
)
token = sdk.client.auth.issue_token(eduUserId=user["eduUserId"], originId="stu_001")
classroom = sdk.client.classrooms.create(
    name="一年级数学",
    startsAt="2026-08-17T10:00:00.000Z",
    endsAt="2026-08-17T11:00:00.000Z",
    teacherEduUserId=user["eduUserId"],
)
sdk.client.classrooms.start(classroom["classroomId"])
sdk.client.classrooms.members.add(
    classroom["classroomId"],
    eduUserId=user["eduUserId"],
    role="student",
)
sdk.client.classrooms.members.replace_students(
    classroom["classroomId"],
    eduUserIds=[user["eduUserId"]],
)
sdk.client.classrooms.permissions.set(
    classroom["classroomId"],
    user["eduUserId"],
    permission="camera",
    effect="grant",
    operatorEduUserId=user["eduUserId"],
)
sdk.client.classrooms.coursewares.bind(
    classroom["classroomId"],
    coursewareIds=["cw_xxx"],
)
sdk.client.app.get_ui_config()
```

| 方法 | 对应 Node |
|------|-----------|
| `users.register(**input)` | `users.register` |
| `auth.issue_token(**input)` | `auth.issueToken` |
| `classrooms.create/start/end` | 同名 |
| `classrooms.members.add/list` | 同名 |
| `classrooms.members.replace_students` | `replaceStudents` |
| `classrooms.permissions.get/set/clear` | 同名 |
| `classrooms.coursewares.list/bind/unbind` | 同名 |
| `app.get_ui_config` / `set_ui_config` | `getUiConfig` / `setUiConfig` |

## 白板 `sdk.whiteboard_client`

```python
credential = sdk.whiteboard_client.auth.issue_room_token(
    roomId="room_1",
    userId=user["eduUserId"],
    role="host",
    expiresIn=3600,
)
session = sdk.whiteboard_client.recordings.start("room_1", externalRef="lesson_001")
sdk.whiteboard_client.recordings.stop("room_1", recordingId=session["recordingId"])
sdk.whiteboard_client.recordings.enqueue_video_export(session["recordingId"], profile="hd")
sdk.whiteboard_client.files.convert(sourceUrl="https://cdn.example.com/lesson.pptx")
```

| 方法 | 对应 Node |
|------|-----------|
| `auth.issue_room_token` | `issueRoomToken` |
| `recordings.start/stop/list/get` | 同名 |
| `recordings.register_media_asset` / `delete_media_asset` | camelCase 版 |
| `recordings.enqueue_video_export` / `get_video_export` | camelCase 版 |
| `captures.create/list` | 同名 |
| `files.convert` / `get_convert_job` | `getConvertJob` |

## 错误

```python
try:
    sdk.client.auth.issue_token(eduUserId="")
except EduskitError as e:
    print(e.error_code, e.status, e.trace_id, e.source)
```

`sdk.client.last_trace_id` / `sdk.whiteboard_client.last_trace_id`。

## 示例

- [examples/classroom_quickstart.py](examples/classroom_quickstart.py)

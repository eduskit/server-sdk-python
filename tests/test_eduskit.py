import json
import base64
import unittest

from eduskit import Eduskit, EduskitError


def mock_fetch(body, status=200, headers=None):
    calls = []

    def fetch(url, method, req_headers, payload, timeout_ms):
        calls.append(
            {
                "url": url,
                "method": method,
                "headers": req_headers,
                "body": json.loads(payload.decode()) if payload else None,
            }
        )
        return status, headers or {"x-trace-id": "wb-trace"}, json.dumps(body).encode()

    return fetch, calls


class EduskitTest(unittest.TestCase):
    def test_private_room_server_routes(self):
        fetch, calls = mock_fetch({"code": 0, "data": {"marker": "server-result"}})
        sdk = Eduskit(whiteboard_client={"base_url": "http://wb.test", "app_id": "app_wb", "app_key": "wk", "app_secret": "ws"}, fetch=fetch)
        rooms = sdk.whiteboard_client.rooms
        operations = [
            lambda: rooms.provision_private_room("room_a", "assignment_a"),
            lambda: rooms.change_private_room_grant("room_a", userId="student_a", requestId="grant_a", expectedGeneration="9223372036854775806", action="grant", role="participant"),
            lambda: rooms.get_private_room_access("room_a", "student_a"),
            lambda: rooms.issue_private_room_token("room_a", userId="student_a", role="participant", expiresIn=600),
            lambda: rooms.seal_private_room("room_a"),
            lambda: rooms.create_frozen_snapshot("room_a", "snapshot_a"),
            lambda: rooms.get_frozen_snapshot("room_a", "snapshot_a"),
            lambda: rooms.get_frozen_snapshot_download("room_a", "snapshot_a"),
            lambda: rooms.initialize_private_workspace("room_a", "assignment_a", None),
            lambda: rooms.initialize_private_workspace("room_a", "assignment_a", "snapshot_a"),
            lambda: rooms.get_private_workspace_initialization("room_a"),
            lambda: rooms.schedule_private_room_writes("room_a", "window_a", "2026-10-02T00:00:00.000Z", "2026-10-02T00:10:00.000Z"),
        ]
        for operation in operations:
            self.assertEqual(operation(), {"marker": "server-result"})
        expected = ["", "/grants", "/access/query", "/token", "/seal", "/snapshots", "/snapshots/query", "/snapshots/download", "/initializations", "/initializations", "/initializations/query", "/write-window"]
        self.assertEqual([call["url"] for call in calls], ["http://wb.test/v1/rooms/private" + suffix for suffix in expected])
        for call in calls:
            self.assertEqual(call["method"], "POST")
            self.assertEqual(call["body"]["roomId"], "room_a")
            self.assertEqual(call["headers"]["x-app-key"], "wk")
        self.assertEqual(calls[1]["body"]["expectedGeneration"], "9223372036854775806")
        self.assertNotIn("accessGeneration", calls[3]["body"])
        self.assertEqual(calls[8]["body"], {"roomId": "room_a", "assignmentId": "assignment_a", "sourceSnapshotId": None})
        self.assertEqual(calls[9]["body"]["sourceSnapshotId"], "snapshot_a")
        self.assertEqual(calls[10]["body"], {"roomId": "room_a"})
        self.assertEqual(calls[11]["body"], {"roomId":"room_a", "requestId":"window_a", "opensAt":"2026-10-02T00:00:00.000Z", "closesAt":"2026-10-02T00:10:00.000Z"})

    def test_classroom_register(self):
        fetch, calls = mock_fetch(
            {
                "code": 0,
                "data": {"eduUserId": "eu_1", "nickname": "n"},
                "traceId": "body-trace",
            }
        )
        sdk = Eduskit(
            client={"base_url": "http://edu.test", "app_id": "app_edu", "app_key": "k", "app_secret": "secret-edu"},
            fetch=fetch,
        )
        user = sdk.client.users.register(nickname="n", avatar="https://a")
        self.assertEqual(user["eduUserId"], "eu_1")
        self.assertEqual(sdk.client.last_trace_id, "body-trace")
        self.assertEqual(calls[0]["url"], "http://edu.test/v1/users")
        self.assertEqual(calls[0]["headers"]["x-app-key"], "k")

    def test_whiteboard_issue_room_token(self):
        fetch, calls = mock_fetch({"code": 0, "data": {"token": "rt"}})
        sdk = Eduskit(
            whiteboard_client={
                "base_url": "http://wb.test",
                "app_id": "app_wb",
                "app_key": "wk",
                "app_secret": "ws",
            },
            fetch=fetch,
        )
        token = sdk.whiteboard_client.auth.issue_room_token(
            roomId="r1", userId="u1", role="host"
        )
        self.assertEqual(token["appId"], "app_wb")
        self.assertEqual(len(token["token"].split(".")), 3)
        segment = token["token"].split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))
        self.assertIn("access_generation", claims)
        self.assertIsNone(claims["access_generation"])
        self.assertEqual(calls, [])

    def test_error_envelope(self):
        fetch, _ = mock_fetch(
            {
                "code": 404,
                "errorCode": "EDU_USER_NOT_FOUND",
                "message": "missing",
                "traceId": "err",
            },
            status=404,
        )
        sdk = Eduskit(
            client={"base_url": "http://edu.test", "app_id": "app_edu", "app_key": "k", "app_secret": "secret-edu"},
            fetch=fetch,
        )
        with self.assertRaises(EduskitError) as ctx:
            sdk.client.auth.issue_token(eduUserId="")
        self.assertEqual(ctx.exception.error_code, "SDK_TOKEN_INPUT_INVALID")

    def test_unconfigured(self):
        sdk = Eduskit(
            client={"base_url": "http://edu.test", "app_id": "app_edu", "app_key": "k", "app_secret": "secret-edu"}
        )
        with self.assertRaises(EduskitError) as ctx:
            _ = sdk.whiteboard_client
        self.assertEqual(ctx.exception.error_code, "SDK_CLIENT_NOT_CONFIGURED")


if __name__ == "__main__":
    unittest.main()

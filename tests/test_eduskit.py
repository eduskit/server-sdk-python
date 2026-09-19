import json
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

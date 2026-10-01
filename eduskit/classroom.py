from __future__ import annotations

from urllib.parse import urlencode

from typing import Any

from .http import HttpTransport
from .token import iso_time, sign_hs256


class _Users:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def register(self, **input: Any) -> Any:
        return self._http.request("POST", "/v1/users", input)


class _Auth:
    def __init__(self, app_id: str, app_secret: str) -> None:
        self._app_id = app_id
        self._app_secret = app_secret

    def issue_token(self, **input: Any) -> Any:
        user_id = input.get("eduUserId")
        if not isinstance(user_id, str) or not user_id:
            from .errors import EduskitError
            raise EduskitError("eduUserId is required", error_code="SDK_TOKEN_INPUT_INVALID", source="classroom")
        expires_in = input.get("expiresIn", 86400)
        claims = {"appId": self._app_id}
        if input.get("originId"):
            claims["originId"] = input["originId"]
        if input.get("role"):
            claims["role"] = input["role"]
        token, expires_at = sign_hs256(self._app_id, self._app_secret, user_id,
            "eduskit-edu-auth", "eduskit-edu", expires_in, claims, "classroom")
        return {"accessToken": token, "expiresIn": expires_in, "expiresAt": iso_time(expires_at),
                "tokenType": "Bearer", "appId": self._app_id, "eduUserId": user_id,
                "originId": input.get("originId", ""), "role": input.get("role", "")}


class _Members:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def add(self, classroom_id: str, **input: Any) -> Any:
        return self._http.request("POST", '/v1/classrooms/members', {**(input or {}), 'classroomId': classroom_id})

    def list(self, classroom_id: str) -> Any:
        return self._http.request("GET", '/v1/classrooms/members' + "?" + urlencode({'classroomId': classroom_id}))

    def replace_students(self, classroom_id: str, **input: Any) -> Any:
        return self._http.request(
            "PUT",
            '/v1/classrooms/members/students',
            {**(input or {}), 'classroomId': classroom_id},
        )


class _Permissions:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def get(self, classroom_id: str, edu_user_id: str) -> Any:
        return self._http.request(
            "GET",
            '/v1/classrooms/members/permissions' + "?" + urlencode({'classroomId': classroom_id, 'eduUserId': edu_user_id}),
        )

    def set(self, classroom_id: str, edu_user_id: str, **input: Any) -> Any:
        return self._http.request(
            "POST",
            '/v1/classrooms/members/permissions',
            {**(input or {}), 'classroomId': classroom_id, 'eduUserId': edu_user_id},
        )

    def clear(
        self,
        classroom_id: str,
        edu_user_id: str,
        permission: str,
        **input: Any,
    ) -> Any:
        return self._http.request(
            "DELETE",
            '/v1/classrooms/members/permissions' + "?" + urlencode({'classroomId': classroom_id, 'eduUserId': edu_user_id, 'permission': permission}),
            input,
        )


class _Coursewares:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def list(self, classroom_id: str) -> Any:
        return self._http.request("GET", '/v1/classrooms/coursewares' + "?" + urlencode({'classroomId': classroom_id}))

    def bind(self, classroom_id: str, **input: Any) -> Any:
        return self._http.request(
            "POST",
            '/v1/classrooms/coursewares',
            {**(input or {}), 'classroomId': classroom_id},
        )

    def unbind(self, classroom_id: str, **input: Any) -> Any:
        return self._http.request(
            "DELETE",
            '/v1/classrooms/coursewares' + "?" + urlencode({'classroomId': classroom_id}),
            input,
        )


class _Classrooms:
    def __init__(self, http: HttpTransport) -> None:
        self.members = _Members(http)
        self.permissions = _Permissions(http)
        self.coursewares = _Coursewares(http)
        self._http = http

    def create(self, **input: Any) -> Any:
        return self._http.request("POST", "/v1/classrooms", input)

    def start(self, classroom_id: str) -> Any:
        return self._http.request("POST", '/v1/classrooms/start', {'classroomId': classroom_id})

    def end(self, classroom_id: str) -> Any:
        return self._http.request("POST", '/v1/classrooms/end', {'classroomId': classroom_id})


class _App:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def get_ui_config(self) -> Any:
        return self._http.request("GET", "/v1/app/ui-config")

    def set_ui_config(self, **input: Any) -> Any:
        return self._http.request("PUT", "/v1/app/ui-config", input)


class ClassroomClient:
    def __init__(self, http: HttpTransport, *, app_id: str, app_secret: str) -> None:
        self.users = _Users(http)
        self.auth = _Auth(app_id, app_secret)
        self.classrooms = _Classrooms(http)
        self.app = _App(http)
        self._http = http

    @property
    def last_trace_id(self) -> str:
        return self._http.last_trace_id

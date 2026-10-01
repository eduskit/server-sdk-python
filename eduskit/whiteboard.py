from __future__ import annotations

from urllib.parse import urlencode

from typing import Any

from .http import HttpTransport
from .errors import EduskitError
from .token import iso_time, sign_hs256


class _Auth:
    def __init__(self, app_id: str, app_secret: str) -> None:
        self._app_id = app_id
        self._app_secret = app_secret

    def issue_room_token(self, **input: Any) -> Any:
        room_id, user_id, role = input.get("roomId"), input.get("userId"), input.get("role")
        if not room_id or not user_id or role not in ("host", "participant", "observer"):
            raise EduskitError("roomId, userId and a valid role are required", error_code="SDK_TOKEN_INPUT_INVALID", source="whiteboard")
        expires_in = input.get("expiresIn", 3600)
        token, expires_at = sign_hs256(self._app_id, self._app_secret, user_id,
            "eduskit", "eduskit-room", expires_in,
            {"app_id": self._app_id, "room_id": room_id, "role": role, "source": "server_sdk"},
            "whiteboard")
        return {"token": token, "appId": self._app_id, "roomId": room_id, "userId": user_id,
                "role": role, "expiresIn": expires_in, "expiresAt": iso_time(expires_at)}


class _Recordings:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def start(self, room_id: str, **input: Any) -> Any:
        return self._http.request("POST", '/v1/rooms/recording/start', {**(input or {}), 'roomId': room_id})

    def stop(self, room_id: str, **input: Any) -> Any:
        return self._http.request("POST", '/v1/rooms/recording/stop', {**(input or {}), 'roomId': room_id})

    def list(self, room_id: str) -> Any:
        return self._http.request("GET", '/v1/rooms/recordings' + "?" + urlencode({'roomId': room_id}))

    def get(self, recording_id: str) -> Any:
        return self._http.request("GET", '/v1/recordings' + "?" + urlencode({'recordingId': recording_id}))

    def register_media_asset(self, recording_id: str, **input: Any) -> Any:
        return self._http.request(
            "POST",
            '/v1/recordings/media-assets',
            {**(input or {}), 'recordingId': recording_id},
        )

    def delete_media_asset(self, recording_id: str, asset_id: str) -> Any:
        return self._http.request(
            "DELETE",
            '/v1/recordings/media-assets' + "?" + urlencode({'recordingId': recording_id, 'assetId': asset_id}),
        )

    def enqueue_video_export(self, recording_id: str, **input: Any) -> Any:
        return self._http.request(
            "POST",
            '/v1/recordings/video-exports',
            {**(input or {}), 'recordingId': recording_id},
        )

    def get_video_export(self, recording_id: str, job_id: str) -> Any:
        return self._http.request(
            "GET",
            '/v1/recordings/video-exports' + "?" + urlencode({'recordingId': recording_id, 'jobId': job_id}),
        )


class _Captures:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def create(self, room_id: str, **input: Any) -> Any:
        body = {"roomId": room_id, **input}
        return self._http.request("POST", '/v1/rooms/captures', {**(body or {}), 'roomId': room_id})

    def list(self, room_id: str) -> Any:
        return self._http.request("GET", '/v1/rooms/captures' + "?" + urlencode({'roomId': room_id}))


class _Files:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def convert(self, **input: Any) -> Any:
        return self._http.request("POST", "/v1/files/convert", input)

    def get_convert_job(self, job_id: str) -> Any:
        return self._http.request("GET", '/v1/files/convert' + "?" + urlencode({'jobId': job_id}))


class WhiteboardClient:
    def __init__(self, http: HttpTransport, *, app_id: str, app_secret: str) -> None:
        self.auth = _Auth(app_id, app_secret)
        self.recordings = _Recordings(http)
        self.captures = _Captures(http)
        self.files = _Files(http)
        self._http = http

    @property
    def last_trace_id(self) -> str:
        return self._http.last_trace_id

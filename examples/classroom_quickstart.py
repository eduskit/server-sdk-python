from eduskit import Eduskit

sdk = Eduskit(
    client={
        "base_url": "http://localhost:3112",
        "app_id": "app_dev",
        "app_key": "dev_app_key",
        "app_secret": "dev_app_secret",
    }
)
user = sdk.client.users.register(
    originId="stu_001",
    nickname="小明",
    avatar="https://example.com/a.png",
)
token = sdk.client.auth.issue_token(eduUserId=user["eduUserId"], originId="stu_001")
print(user["eduUserId"], token["accessToken"])

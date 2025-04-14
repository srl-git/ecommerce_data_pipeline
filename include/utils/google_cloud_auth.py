import google.auth
import google.auth.transport.requests


def get_identity_token() -> str:

    credentials, _ = google.auth.default()
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.id_token

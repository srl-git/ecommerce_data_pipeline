import google.auth
import google.auth.transport.requests


def get_identity_token() -> str:
    """
    Retrieve identity token for the Google Cloud credentials.

    Uses the default Google authentication credentials and refreshes them
    to obtain an identity token for the current session.

    Returns:
        str: The identity token for the current authenticated session.
    """
    credentials, _ = google.auth.default()
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.id_token

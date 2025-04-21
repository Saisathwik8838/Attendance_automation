from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json  # Import JSON to handle token storage

# File Paths
TOKEN_FILE = r"C:\Users\saisa\OneDrive\Desktop\google_photos_project\token.json"
CREDENTIALS_FILE = r"C:\Users\saisa\OneDrive\Desktop\google_photos_project\client_secret.json"

# Google API Scopes
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

def authenticate_google():
    creds = None

    # ✅ Load existing token if available
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # ✅ Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())


    # ✅ If no valid credentials, start new authentication flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

        # ✅ Save new credentials for future use
        with open(TOKEN_FILE, "w") as token_file:
            json.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }, token_file)

        print("✅ Authentication successful! Token saved.")

    return creds

# Run authentication if script is executed directly
if __name__ == "__main__":
    authenticate_google()

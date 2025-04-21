import os
import json
import csv
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

# Google Photos API scope
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

# File paths
CREDS_JSON_FILE = r"C:\Users\saisa\OneDrive\Desktop\google_photos_project\client_secret.json"
TOKEN_FILE = r"C:\Users\saisa\OneDrive\Desktop\google_photos_project\token.json"
SAVE_DIR = os.path.expanduser(r"C:\Users\saisa\OneDrive\Desktop\google_photos_project")
CSV_FILE = os.path.join(SAVE_DIR, "albums_data.csv")


def authenticate_google():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token_file:
            token_data = json.load(token_file)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_JSON_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(TOKEN_FILE, 'w') as token_file:
            json.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }, token_file)

    return creds


def fetch_albums():
    creds = authenticate_google()
    albums = []
    url = "https://photoslibrary.googleapis.com/v1/albums?pageSize=50"
    headers = {"Authorization": f"Bearer {creds.token}"}

    while url:
        response = requests.get(url, headers=headers).json()
        albums.extend(response.get("albums", []))
        url = response.get("nextPageToken")
        if url:
            url = f"https://photoslibrary.googleapis.com/v1/albums?pageSize=50&pageToken={url}"

    return albums


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def export_to_csv(albums, filename=CSV_FILE):
    ensure_directory_exists(SAVE_DIR)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    album_photo_data = {album.get('title', 'Untitled'): int(album.get('mediaItemsCount', 0)) for album in albums}

    existing_data = []
    if os.path.exists(filename):
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            existing_data = list(reader)

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        if existing_data:
            headers = existing_data[0]
            headers.append(timestamp)
        else:
            headers = ["Albums", timestamp]

        writer.writerow(headers)

        updated_rows = []
        existing_albums = set(row[0] for row in existing_data[1:])

        for row in existing_data[1:]:
            album_name = row[0]
            new_count = album_photo_data.get(album_name, 0)
            row.append(str(new_count))
            updated_rows.append(row)

        for album, count in album_photo_data.items():
            if album not in existing_albums:
                new_row = [album] + ["0"] * (len(headers) - 2) + [str(count)]
                updated_rows.append(new_row)

        for row in updated_rows:
            writer.writerow(row)

    print(f"\u2705 Album data recorded at {timestamp}, saved to {filename}")


if __name__ == "__main__":
    albums = fetch_albums()
    export_to_csv(albums)

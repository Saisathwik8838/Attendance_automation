import requests
from authenticate import authenticate_google

def fetch_albums():
    creds = authenticate_google()
    headers = {"Authorization": f"Bearer {creds.token}"}
    albums = []
    next_page_token = None

    while len(albums) < 200:  # Fetch at least 200 albums
        url = "https://photoslibrary.googleapis.com/v1/albums?pageSize=50"
        if next_page_token:
            url += f"&pageToken={next_page_token}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            albums.extend(data.get('albums', []))
            next_page_token = data.get('nextPageToken')

            if not next_page_token:  # Stop if no more pages
                break
        else:
            print(f"Error fetching albums: {response.status_code} - {response.text}")
            break

    return albums[:200]  # Ensure max 200 albums

if __name__ == "__main__":
    albums = fetch_albums()
    print(f"Total Albums Fetched: {len(albums)}")
    for album in albums:
        print(f"Album: {album.get('title', 'Untitled')} - {album.get('mediaItemsCount', '0')} photos")

import requests
import csv
from urllib.parse import quote  # Import for URL encoding
from fuzzywuzzy import fuzz

# Replace with your Spotify Client ID and Client Secret
SPOTIFY_CLIENT_ID = "client id here"
SPOTIFY_CLIENT_SECRET = "secret here"


# Retrieve access token from spotify web api
def get_spotify_access_token(client_id, client_secret):
    """Retrieve an access token from Spotify API."""
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(auth_url, headers=headers, data=data, auth=(client_id, client_secret))
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get Spotify access token: " + response.text)


# iterate over artists given
def read_artists_from_csv(file_path):
    """Read artist names from a CSV file."""
    artists = []
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # Make sure the row is not empty
                artists.append(row[0])  # Assuming the artist names are in the first column
    return artists

# check for an individual artist on spotify
def check_artist_on_spotify(artist_name, access_token):
    """Check if an artist exists on Spotify."""
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["artists"]["items"]:
            artist = data["artists"]["items"][0]
            result = {
                "exists": True,
                "search_term": artist_name,
                "retrieved_name": artist["name"],
                "id": artist["id"],
                "genres": artist["genres"],
                "popularity": artist["popularity"],
                "followers": artist["followers"]["total"]
            }
        else:
            result = {"exists": False, "search_term": artist_name, "retrieved_name": None}
    else:
        raise Exception("Spotify API error: " + response.text)

    return result

# process list of artists against spotify
def process_csv(input_file, output_file, access_token, threshold=40):
    """Read data from a CSV file, process it, and write updated data to a new CSV file."""
    updated_rows = []

    # Read the CSV file
    with open(input_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames + ["delete? Y/N"] if "delete? Y/N" not in reader.fieldnames else reader.fieldnames

        # Process each row
        for row in reader:
            artist_name = row.get("content", "")
            if artist_name:
                # Query Spotify for the artist
                result = check_artist_on_spotify(artist_name, access_token)
                if result:
                    print(f"artist name in csv: {artist_name}")
                    print(f"retrieved artist name: {result['retrieved_name']}")
                    print("\n")
                    # Use fuzzywuzzy to compare search term and retrieved artist name
                    similarity = fuzz.ratio(artist_name.lower(), result["retrieved_name"].lower())
                    # Based on similarity, assign "Y" or "N" for delete
                    if similarity >= threshold:
                        row["delete? Y/N"] = "N"  # Mark as "keep" if similarity is above threshold
                    else:
                        row["delete? Y/N"] = "Y"  # Mark for deletion if similarity is below threshold
                else:
                    row["delete? Y/N"] = "Y"  # Mark for deletion if no artist is found in Spotify

            else:
                row["delete? Y/N"] = "Y"  # Default to "Y" if no artist name is provided

            updated_rows.append(row)

            # Write the updated data to a new CSV file
        with open(output_file, mode='w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        print(f"CSV processing complete. Updated file saved to {output_file}")

# def query_artist_on_spotify(artist_name, access_token):
#     """Query a single artist on Spotify and return the result."""
#     search_url = "https://api.spotify.com/v1/search"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     params = {
#         "q": quote(artist_name),
#         "type": "artist",
#         "limit": 1
#     }
#     response = requests.get(search_url, headers=headers, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         print(data)
#         if data["artists"]["items"]:
#             artist = data["artists"]["items"][0]
#             retrieved_name = artist["name"]
#
#             # Use fuzzywuzzy to check the similarity
#             similarity = fuzz.ratio(artist_name.lower(), retrieved_name.lower())
#             delete_flag = "Y" if similarity < threshold else "N"
#
#             result = {
#                 "exists": True,
#                 "search_term": artist_name,
#                 "name": artist["name"],
#                 "id": artist["id"],
#                 "genres": artist["genres"],
#                 "popularity": artist["popularity"],
#                 "followers": artist["followers"]["total"]
#             }
#         else:
#             result = {"exists": False, "message": "Artist not found"}
#     else:
#         raise Exception("Spotify API error: " + response.text)
#
#     # Output the result to the console
#     if result["exists"]:
#         print("\nSearch Term:", result["search_term"])
#         print("\nArtist found:")
#         print(f"  Name: {result['name']}")
#         print(f"  ID: {result['id']}")
#         print(f"  Genres: {', '.join(result['genres']) if result['genres'] else 'None'}")
#         print(f"  Popularity: {result['popularity']}")
#         print(f"  Followers: {result['followers']}")
#     else:
#         print("\nArtist not found.")
#         print(f"  Query: {artist_name}")
#
#     return result


def main():
    # Path to the CSV file with artist names
    input_csv = "malicious-artists.csv"
    output_csv = "updated-artists.csv"

    try:
        # Get Spotify access token
        access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

        # Process the CSV file
        process_csv(input_csv, output_csv, access_token)
        print(f"Updated CSV saved to {output_csv}")
    except Exception as e:
        print(f"Error: {e}")




if __name__ == "__main__":
    main()

    # this is for querying for an individual artist
    # access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    # query_artist_on_spotify("es real poniendo alabanza en los labios", access_token)
import requests
import sys
import csv
import json
import config
from urllib.parse import urlparse

# arguments passed
playlist_url = sys.argv[1] if len(sys.argv) > 1 else 0
file_output_name = sys.argv[2] if len(sys.argv) > 2 else 0
state = sys.argv[3] if len(sys.argv) > 3 else 0

# Constants
client_id = config.CLIENT_ID
client_secret = config.CLIENT_SECRET

auth_url = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(auth_url, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

auth_response_data = auth_response.json()

access_token = auth_response_data['access_token']

api_url = 'https://api.spotify.com/v1/'

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# Variables

song_list = []
song_id_list = []

total_song_count = 0
playlist_count = 0

isState = False

# Check url

playlists = [
    # 70s Music
    "https://open.spotify.com/playlist/37i9dQZF1DWTJ7xPn4vNaz?si=c6ff259b874944ec",
    "https://open.spotify.com/playlist/37i9dQZF1DWYOqWoDP009i?si=41571d2ccefc4d74",
    "https://open.spotify.com/playlist/37i9dQZF1DWWwzidNQX6jx?si=65f4e1ceccfb4db5",
    "https://open.spotify.com/playlist/37i9dQZF1DWTTn6daQVbOa?si=def43b9ad24c495b",
    "https://open.spotify.com/playlist/37i9dQZF1DWWg3YRMu4AEF?si=a416c4d987234ab3",
    "https://open.spotify.com/playlist/37i9dQZF1DWSWNiyXQAvbl?si=9724070e46a9448b",

    # 10s Music
    "https://open.spotify.com/playlist/37i9dQZF1DX5Ejj0EkURtP?si=fe86b552d4d54926",
    "https://open.spotify.com/playlist/37i9dQZF1DX99DRG9N39X3?si=3372db4e85b84963",
    "https://open.spotify.com/playlist/37i9dQZF1DWXbttAJcbphz?si=26eb9dd87a20492e",
    "https://open.spotify.com/playlist/37i9dQZF1DX1uHCeFHcn8X?si=fa21557de9cd4845",
    "https://open.spotify.com/playlist/37i9dQZF1DWSMyFeHM3son?si=c168e276b3194b90",
    "https://open.spotify.com/playlist/37i9dQZF1DWVTfbQdQ8l7H?si=2917239b9586421a"
]

for playlist in playlists:

    playlist_path = urlparse(str(playlist)).path
    playlist_id = playlist_path.split('/')[-1]

    spotify_playlist = requests.get(api_url + 'playlists/' + playlist_id + '/tracks', headers=headers).json()

    if spotify_playlist:

        song_count = 0

        if 'items' in spotify_playlist:
            for item in spotify_playlist['items']:
                if 'track' in item:
                    if 'id' in item['track']:
                        if not item['track']['id'] in song_id_list:
                            song_id_list.append(item['track']['id'])
                            try:
                                spotify_song = requests.get(api_url + 'audio-analysis/' + item['track']['id'], headers=headers).json()

                                # if state == 1:
                                #     isState = True
                                if playlist_count <= 5:
                                    isState = True

                                new_song = [
                                    spotify_song['track']['end_of_fade_in'],
                                    spotify_song['track']['start_of_fade_out'],
                                    spotify_song["track"]['loudness'],
                                    spotify_song["track"]['tempo'],
                                    spotify_song["track"]['tempo_confidence'],
                                    spotify_song["track"]['time_signature'],
                                    spotify_song["track"]['time_signature_confidence'],
                                    spotify_song["track"]['key'],
                                    spotify_song["track"]['key_confidence'],
                                    spotify_song["track"]['mode'],                       
                                    spotify_song["track"]['mode_confidence'],
                                    spotify_song['bars'],
                                    spotify_song['beats'],
                                    spotify_song['sections'],
                                    spotify_song['segments'],
                                    spotify_song['tatums'],
                                    isState
                                ]
                                song_list.append(new_song)
                                print('Scraped Song ' + str(song_count+1) + "/" + str(len(spotify_playlist['items'])) + " | " + str(total_song_count) + " Cumulative")
                                song_count += 1
                            except TypeError:
                                print('⚠️  Error Fetching Song ' + str(song_count+1))
                        else:
                            print('Already Fetched Song')
    
    playlist_count += 1
    total_song_count += song_count
    print("Finished Playlist " + str(playlist_count) + " ==========================================")
    print("Completed " + str(total_song_count) + " songs so far")


print('📦 Creating CSV for ' + str(total_song_count) +' songs...')
if file_output_name == 0:
    file_output_name = 'songs'

with open('./' + str(file_output_name) + '.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['end_of_fade_out', 'start_of_fade_out', 'loudness', 'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence', 'bars', 'beats', 'sections', 'segments', 'tatums', 'isState'])
    writer.writerows(song_list)
f.close()

print('Finished outputting to ./' + str(file_output_name) + '.csv')

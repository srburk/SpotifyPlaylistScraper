import requests
import sys
import csv
import json

# arguments passed
playlist_id = sys.argv[1] if len(sys.argv) > 1 else 0
file_output_name = sys.argv[2] if len(sys.argv) > 2 else 0

client_id = '83ae548c8bdb40a9a65a4b6e2a174bd6'
client_secret = '9961fe6a1fe94d11a256d13a65b44efb'

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

isRetro = True

song_list = []

song_count = 0

spotify_playlist = requests.get(api_url + 'playlists/' + playlist_id + '/tracks', headers=headers).json()

if spotify_playlist:
    if 'items' in spotify_playlist:
        for item in spotify_playlist['items']:
            if 'track' in item:
                if 'id' in item['track']:
                    try:
                        spotify_song = requests.get(api_url + 'audio-features/' + item['track']['id'], headers=headers).json()
                        new_song = [
                            spotify_song['danceability'],
                            spotify_song["energy"],
                            spotify_song["key"],
                            spotify_song["loudness"],
                            spotify_song["speechiness"],
                            spotify_song["acousticness"],
                            spotify_song["instrumentalness"],
                            spotify_song["liveness"],
                            spotify_song["valence"],
                            spotify_song["tempo"],                       
                            spotify_song["time_signature"],
                            isRetro
                        ]
                        song_list.append(new_song)
                        print('Scraped Song ' + str(song_count+1) + ' | ' + str(song_list[song_count]))
                        song_count += 1
                    except TypeError:
                        print('⚠️  Error Fetching Song ' + str(song_count+1))


print('📦 Creating CSV for ' + str(song_count) +' songs...')
if not file_output_name:
    file_output_name = 'songs'
else:
    with open('./' + str(file_output_name) + '.csv', 'a+') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'isRetro'])
        # for song in song_list:
        #     writer.writerow(song)
        writer.writerows(song_list)
    f.close()

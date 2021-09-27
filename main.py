import os, spotipy, subprocess
from requests.exceptions import ConnectionError

import mp3_dl
import tokens

def process_input(link):
    if 'open.spotify.com' in link:
        mp3_dl.spotipy_initialize(tokens.SPOTIPY_CLIENT_ID, tokens.SPOTIPY_CLIENT_SECRET)
        if 'open.spotify.com/track/' in link:
            try:
                track = mp3_dl.sp.track(track_id=link)
            except ConnectionError:
                print('ERROR: Connection failed, check internet connection.')
                return
            except spotipy.client.SpotifyException:
                print('ERROR: Invalid spotify track URL.')
                return
            track = mp3_dl.sp.track(link)
            mp3_dl.dl_sp_track(track, silent=False)
        
        elif 'open.spotify.com/playlist/' in link:
            try:
                playlist = mp3_dl.sp.playlist(playlist_id=link)
            except ConnectionError:
                print('ERROR: Connection failed, check internet connection.')
                return
            except spotipy.client.SpotifyException:
                print('Invalid spotify playlist URL.')
                return
            mp3_dl.dl_spotify(playlist, silent=False)                

        elif 'open.spotify.com/album/' in link:
            try:
                album = mp3_dl.sp.album(album_id=link)
            except ConnectionError:
                print('ERROR: Connection failed, check internet connection.')
                return
            except spotipy.client.SpotifyException:
                print('Invalid spotify playlist URL.')
                return
            mp3_dl.dl_spotify(album, silent=False)

        elif 'open.spotify.com/artist/' in link:
            print('Spotify artist support has not been implemented yet')

        else:
            print('ERROR: Unrecognized Spotify link. Please use playlist, album, artist, or song share link.')
    elif 'www.youtube.com' in link:
        if '?v=' in link:
            mp3_dl.dl_yt_video(link, silent=False)
        elif 'list=' in link:
            mp3_dl.dl_yt_playlist(link, silent=False)
        else:
            print('ERROR: Invalid Youtube link. Please make sure the videoid or playlistid is present.')
    elif not link or link.isspace():
        print("Please provide an input")
    else:
        mp3_dl.dl_query(link, silent=False)


if __name__ == '__main__':

    if not os.path.exists('out'):
        os.mkdir('out')
    os.chdir(mp3_dl.root + '/out')

    while True:
        link = input('Insert Spotify/Youtube link or Youtube search query: ')
        ffmpeg_path = "./ffmpeg/ffmpeg.exe"
        try:
            #p = subprocess.Popen([process_input(ffmpeg_path), link])
            process_input(link)
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise e
            print('ERROR: Unrecognized error. Please try again.')
            print(e)
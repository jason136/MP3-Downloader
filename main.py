import os, spotipy
from spotipy.oauth2 import SpotifyOAuth

import mp3_dl, tokens

if __name__ == '__main__':

    if not os.path.exists('out'):
        os.mkdir('out')
    os.chdir(mp3_dl.root + '/out')

    while True:
        link = input('Insert Spotify/Youtube link or Youtube search query: ')

        try:
        #if True:
            if 'open.spotify.com' in link:
                mp3_dl.spotipy_initialize()
                if 'open.spotify.com/track/' in link:
                    try:
                        track = mp3_dl.sp.track(track_id=link)
                    except ConnectionError:
                        print('ERROR: Connection failed, check internet connection.')
                        continue
                    except spotipy.client.SpotifyException:
                        print('ERROR: Invalid spotify track URL.')
                        continue
                    track = mp3_dl.sp.track(link)
                    mp3_dl.dl_sp_track(track, silent=False)
                
                elif 'open.spotify.com/playlist/' in link:
                    try:
                        playlist = mp3_dl.sp.playlist(playlist_id=link)
                    except ConnectionError:
                        print('ERROR: Connection failed, check internet connection.')
                        continue
                    except spotipy.client.SpotifyException:
                        print('Invalid spotify playlist URL.')
                        continue
                    mp3_dl.dl_spotify(playlist, silent=False)                

                elif 'open.spotify.com/album/' in link:
                    try:
                        album = mp3_dl.sp.album(album_id=link)
                    except ConnectionError:
                        print('ERROR: Connection failed, check internet connection.')
                        continue
                    except spotipy.client.SpotifyException:
                        print('Invalid spotify playlist URL.')
                        continue
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
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise e
            print('ERROR: Unrecognized error. Please try again.')
            print(e)
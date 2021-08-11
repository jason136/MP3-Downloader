import mp3-dl

if __name__ == '__main__':

    if not os.path.exists('out'):
        os.mkdir('out')
    os.chdir(root + '/out')

    while True:
        link = input('Insert Spotify/Youtube link or Youtube search query: ')

        try:
            if 'open.spotify.com' in link:
                sp = spotipy.Spotify(
                    auth_manager=SpotifyOAuth(
                        client_id=tokens.SPOTIPY_CLIENT_ID, 
                        client_secret=tokens.SPOTIPY_CLIENT_SECRET, 
                        redirect_uri='http://localhost:8000', 
                        scope='user-library-read', 
                        cache_path='{}/OAuthCache.txt'.format(root)
                    )
                )
                if 'open.spotify.com/track/' in link:
                    try:
                        track = sp.track(track_id=link)
                    except ConnectionError:
                        print('ERROR: Connection failed, check internet connection.')
                        continue
                    except spotipy.client.SpotifyException:
                        print('ERROR: Invalid spotify track URL.')
                        continue
                    track = sp.track(link)
                    dl_sp_track(track, silent=False)
                
                elif 'open.spotify.com/playlist/' in link:
                    try:
                        playlist = sp.playlist(playlist_id=link)
                    except ConnectionError:
                        print('ERROR: Connection failed, check internet connection.')
                        continue
                    except spotipy.client.SpotifyException:
                        print('Invalid spotify playlist URL.')
                        continue
                    dl_spotify(playlist, silent=False)                

                elif 'open.spotify.com/album/' in link:
                    try:
                        album = sp.album(album_id=link)
                    except ConnectionError:
                        print('ERROR: Connection failed, check internet connection.')
                        continue
                    except spotipy.client.SpotifyException:
                        print('Invalid spotify playlist URL.')
                        continue
                    dl_spotify(album, silent=False)

                elif 'open.spotify.com/artist/' in link:
                    print('Spotify artist support has not been implemented yet')

                else:
                    print('ERROR: Unrecognized Spotify link. Please use playlist, album, artist, or song share link.')
            elif 'www.youtube.com' in link:
                if '?v=' in link:
                    dl_yt_video(link, silent=False)
                elif 'list=' in link:
                    dl_yt_playlist(link, silent=False)
                else:
                    print('ERROR: Invalid Youtube link. Please make sure the videoid or playlistid is present.')
            else:
                dl_query(link, silent=False)
        except Exception as e:
            print('ERROR: Unrecognized error. Please try again.')
            print(e)
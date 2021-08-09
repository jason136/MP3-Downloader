import youtube_dl, spotipy, os, requests
from spotipy.oauth2 import SpotifyOAuth
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, error
from youtube_dl.utils import DownloadError
from requests.exceptions import ConnectionError

import tokens

root = os.getcwd()

ytdl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'extractaudio': True,
    'audioformat': 'mp3',
    'hls-prefer-ffmpeg': True, 
    'outtmpl': '%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn', 
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)

def dl_query(query, duration=None):
    try:
        if duration:
            lyric_vids = ytdl.extract_info('ytsearch4:{} lyrics'.format(query), download=False, extra_info={'duration', 'id'})['entries']
            print(len(lyric_vids))
            best_diff = abs(duration - lyric_vids[0]['duration'])
            best_option = lyric_vids[0]

            for result in reversed(lyric_vids):
                diff = abs(duration - result['duration'])
                print('diff: ', diff, ' best diff: ', best_diff)
                if (diff <= best_diff):
                    best_option = result
            
            print(duration, ' ------------ ', result['duration'])

            ytdl.download([best_option['webpage_url']])

            filename = '{}.mp3'.format(best_option['id'])
        else:
            result = ytdl.extract_info('ytsearch:{} lyrics'.format(query))
            filename = '{}.mp3'.format(result['entries'][0]['id'])
    except DownloadError:
        print('Error during ytdl download of: ', query, '. Retrying...')
        try:
            result = ytdl.extract_info('ytsearch:{}'.format(query))
            print('Retry successful!')
        except DownloadError:
            return None
    
    return filename

def dl_yt_playlist(link):
    print('Gathering Youtube playlist data...')
    result = ytdl.extract_info(link, download=False)
    playlist_name = result['title']
    playlist_name = legalize_chars(playlist_name)
    if not os.path.exists(playlist_name):
        os.mkdir(playlist_name)
    os.chdir(playlist_name)
    total = len(result['entries'])
    count = 0
    for video in result['entries']:
        progress(count, total, video['title'])
        dl_yt_video(video['webpage_url'])
        count = count + 1
    os.chdir(root + '/out')
    print('{}/{} 100{}. Playlist download complete!'.format(count, total, '%'))

def dl_yt_video(link, silent=True):
    try:
        result = ytdl.extract_info(link, download=False)
        if not silent:
            print('Downloading Youtube audio from: {}'.format(result['title']))
        filename = '{}.mp3'.format(result['id'])
        new_name = '{}.mp3'.format(result['title'])
        new_name = legalize_chars(new_name)
        if os.path.exists(new_name):
            return
        ytdl.download([result['webpage_url']])
        os.rename(filename, new_name)
        if not silent:
            print('Download complete!')
    except DownloadError:
        print('Error during download of: ', result['title'], '. Retrying...')
        try:
            result = ytdl.extract_info('ytsearch:{}'.format(result['title']))
            print('Retry successful!')
        except:
            return None

def dl_spotify(playlist):
    playlist_name = playlist['name']
    print('Downloading Spotify playlist: {}'.format(playlist_name))
    playlist_name = legalize_chars(playlist_name)
    if not os.path.exists(playlist_name):
        os.mkdir(playlist_name)
    os.chdir(playlist_name)
    
    playlist = playlist['tracks']
    total = 0
    while playlist['next']:
        total = total + 100
        playlist = sp.next(playlist)
    tracks = playlist['items']
    total = total + len(tracks)

    count = 0
    retries = []
    while playlist['next']:
        tracks = playlist['items']
        for track in tracks:
            progress(count, total, '{} - {}'.format(
                track['track']['name'], 
                track['track']['artists'][0]['name']
            ))
            retry = dl_sp_track(track['track'])
            if retry:
                retries.append(retry)
            else:
                count = count + 1
        playlist = sp.next(playlist)
    tracks = playlist['items']
    for track in tracks:
        progress(count, total, '{} - {}'.format(
                track['track']['name'], 
                track['track']['artists'][0]['name']
            ))
        retry = dl_sp_track(track['track'])
        if retry:
            retries.append(retry)
        else:
            count = count + 1
    while count < total:
        for track in retries:
            progress(count, total, '{} - {}'.format(
                track['track']['name'], 
                track['track']['artists'][0]['name']
            ))
            retry = dl_sp_track(track['track'])
            if retry:
                retries.append(retry)
            else:
                count = count + 1

    print('{}/{} 100{}, Playlist download complete!'.format(count, total, '%'))
    os.remove('thumbnail.jpg')
    os.chdir(root + '/out')

def dl_sp_track(track, silent=True):
    title = track['name']
    artist = track['artists'][0]['name']
    if not silent:
        print('Downloading Spotify track: {} - {}'.format(title, artist))
    query = '{} {}'.format(title, artist)
    new_name = '{} - {}.mp3'.format(title, artist)
    new_name = legalize_chars(new_name)
    if os.path.isfile(new_name):
        return 

    duration = int(track['track']['duration_ms'] / 1000)
    filename = dl_query(query, duration)
    if not filename:
        print('Retry unsucessful. Song will be reaquired at the end of queue')
        return track

    if not os.path.isfile(new_name): 
        os.rename(filename, new_name)

    with open('thumbnail.jpg', 'wb') as handle:
        try:
            thumbnail = requests.get(track['track']['album']['images'][0]['url']).content
            handle.write(thumbnail)
        except:
            print('Thumbnail error on thumbnail for: ', title, ' - ', artist)
    
    audio = MP3(new_name, ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass
    audio.tags.add(
        APIC(
            encoding=3,
            mime='image/jpg',
            type=3, 
            desc=u'Cover',
            data=open('thumbnail.jpg', 'rb').read()
        )
    )
    audio.save(v2_version=3)
    audio = ID3(new_name)
    audio.add(TIT2(encoding=3, text=title))
    audio.add(TPE1(encoding=3, text=artist))
    audio.add(TALB(encoding=3, text=track['track']['album']['name']))
    audio.save()

    if not silent:
        print('Download complete!')

def progress(count=0, total=1, song=''):
    percentage = int(count * 1000 / total)
    print(
        '{}/{} '.format(count, total),
        percentage / 10.0, '%', 
        'Complete. Now Processing: ', 
        song
    )

def legalize_chars(filename):
    illegal_chars = ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        if char in filename:
            filename = filename.replace(char, '')
    return filename

if __name__ == '__main__':

    if not os.path.exists('out'):
        os.mkdir('out')
    os.chdir(root + '/out')

    while True:
        link = input('Insert Spotify/Youtube link or Youtube search query: ')

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
            if 'open.spotify.com/playlist/' in link:
                try:
                    playlist = sp.playlist(playlist_id=link)
                except ConnectionError:
                    print('Connection error, check internet connection')
                    continue
                except spotipy.client.SpotifyException:
                    print('Invalid spotify playlist url')
                    continue
                dl_spotify(playlist)

            elif 'open.spotify.com/track/' in link:
                try:
                    track = sp.track(track_id=link)
                except ConnectionError:
                    print('Connection error, check internet connection')
                    continue
                except spotipy.client.SpotifyException:
                    print('Invalid spotify track url')
                    continue
                track = sp.track(link)
                dl_sp_track(track, False)
            elif 'open.spotify.com/artist/' in link:
                pass
            else:
                print('Invalid Spotify link. Please use playlist, album, or song share link')
        if 'www.youtube.com' in link:
            if 'list=' in link:
                dl_yt_playlist(link)
            elif '?v=' in link:
                dl_yt_video(link, False)
            else:
                print('Invalid Youtube link. Please make sure the videoid or playlistid is present')
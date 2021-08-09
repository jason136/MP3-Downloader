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
            lyric_vids = ytdl.extract_info('ytsearch4:{} lyrics'.format(query), download=False)['entries']
            print(len(lyric_vids))
            music_vids = ytdl.extract_info('ytsearch:{}'.format(query), download=False)['entries']
            print(len(music_vids))
            best_diff = abs(duration - lyric_vids[0]['duration'])
            best_option = lyric_vids[0]

            for result in lyric_vids:
                if abs(duration - result['duration']) < best_diff:
                    best_option = result
            for result in music_vids:
                if abs(duration - result['duration']) < 3:
                    best_option = result
            
            print(duration, ' ------------ ', result['duration'])

            ytdl.download([best_option['webpage_url']])

            filename = '{}.mp3'.format(best_option['id'])
        else:
            result = ytdl.extract_info('ytsearch:{} lyrics'.format(query))
            filename = '{}.mp3'.format(result['entries'][0]['id'])
    except Exception as e:
        raise e
        print('error during ytdl download of ', query, ', retrying...')
        try:
            result = ytdl.extract_info('ytsearch:{}'.format(query))
            print('retry successful!')
        except:
            return None
    
    return filename

def dl_yt_playlist(link):
    print('gathering Youtube playlist data...')
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
    print('{}/{} 100{}, playlist download complete!'.format(count, total, '%'))

def dl_yt_video(link):
    result = ytdl.extract_info(link, download=False)
    filename = '{}.mp3'.format(result['id'])
    new_name = '{}.mp3'.format(result['title'])
    new_name = legalize_chars(new_name)
    if os.path.exists(new_name):
        return
    ytdl.download([result['webpage_url']])
    os.rename(filename, new_name)

def dl_spotify(link):
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=tokens.SPOTIPY_CLIENT_ID, 
            client_secret=tokens.SPOTIPY_CLIENT_SECRET, 
            redirect_uri='http://localhost:8000', 
            scope='user-library-read', 
            cache_path='{}/OAuthCache.txt'.format(root)
        )
    )

    try:
        playlist = sp.playlist(playlist_id=link)
    except ConnectionError:
        print('connection error, check internet connection')
        return
    except spotipy.client.SpotifyException:
        print('invalid spotify playlist url')
        return

    playlist_name = playlist['name']
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
            retry = dl_sp_track(track)
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
        retry = dl_sp_track(track)
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
            retry = dl_sp_track(track)
            if retry:
                retries.append(retry)
            else:
                count = count + 1

    print('{}/{} 100{}, playlist download complete!'.format(count, total, '%'))
    os.remove('thumbnail.jpg')
    os.chdir(root + '/out')

def dl_sp_track(track):
    title = track['track']['name']
    artist = track['track']['artists'][0]['name']
    query = '{} {}'.format(title, artist)
    new_name = '{} - {}.mp3'.format(title, artist)
    new_name = legalize_chars(new_name)
    if os.path.isfile(new_name):
        return 

    duration = int(track['track']['duration_ms'] / 1000)
    filename = dl_query(query)
    if not filename:
        print('retry unsucessful, song will be reaquired at the end of queue')
        return track

    if not os.path.isfile(new_name): 
        os.rename(filename, new_name)

    with open('thumbnail.jpg', 'wb') as handle:
        try:
            thumbnail = requests.get(track['track']['album']['images'][0]['url']).content
            handle.write(thumbnail)
        except:
            print('thumbnail error on ', title, ' - ', artist)
    
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
        link = input('insert Spotify/Youtube link or Youtube search query: ')

        if 'open.spotify.com' in link:
            if 'open.spotify.com/playlist/' in link:
                dl_spotify(link)
            elif 'open.spotify.com/track/' in link:
                pass
            elif 'open.spotify.com/artist/' in link:
                pass
            else:
                print('invalid Spotify link, please use playlist, album, or song share link')
        if 'www.youtube.com' in link:
            try:
                if 'list=' in link:
                    dl_yt_playlist(link)
                elif '?v=' in link:
                    dl_yt_video(link)
                else:
                    print('invalid Youtube link, please make sure the videoid or playlistid is present')
            except DownloadError as e:
                raise e
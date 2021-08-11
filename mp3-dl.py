import youtube_dl, spotipy, os, requests, subprocess
from spotipy.oauth2 import SpotifyOAuth
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, error
from youtube_dl.utils import DownloadError
from requests.exceptions import ConnectionError

import tokens

root = os.getcwd()

count = 0
total = 0
retries = []

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

def dl_yt_playlist(link, silent=False):
    print('Gathering Youtube playlist data...')
    try:
        result = ytdl.extract_info(link, download=False)
    except DownloadError as e:
        if 'This video is DRM protected' in str(e):
            print('ERROR: Invalid Youtube playlist URL')
        return
    playlist_name = result['title']
    print('Downloading Youtube playlist: \"{}\"'.format(playlist_name))
    playlist_name = legalize_chars(playlist_name)
    if not os.path.exists(playlist_name):
        os.mkdir(playlist_name)
    os.chdir(playlist_name)
    total = len(result['entries'])
    count = 0
    for video in result['entries']:
        if not silent:
            progress(count, total, video['title'])
        dl_yt_video(video['webpage_url'])
        count = count + 1
    os.chdir(root + '/out')
    if not silent:
        print('{}/{}  100{}. Playlist download complete!'.format(count, total, '%'))

def dl_yt_video(link, silent=True, recurse=False):
    try:
        if not silent:
            print('Downloading Youtube video...')
        result = ytdl.extract_info(link)
        filename = '{}.mp3'.format(result['id'])
        new_name = result['title']
        new_name = '{}.mp3'.format(legalize_chars(new_name))
        if not silent:
            print('Audio from: \"{}\" Download complete!'.format(result['title']))
        if os.path.exists(new_name):
            os.remove(new_name)
        os.rename(filename, new_name)
    except DownloadError as e:
        if 'Incomplete YouTube ID' in str(e):
            return
        elif 'Video unavailable' in str(e):
            return
        if recurse:
            print('Retry unsucessful!')
            return None
        else:
            print('ERROR: Download of: \"{}\" failed. Retrying...'.format(link))
            dl_yt_video(link, silent=True, recurse=True)
    if recurse:
        print('Retry sucessful!')
    try:
        return filename
    except UnboundLocalError as e:
        if str(e) == 'local variable \'filename\' referenced before assignment':
            return None

def dl_query(query, silent=True, duration=None, recurse=False):
    try:
        if duration:
            lyric_vids = ytdl.extract_info('ytsearch:{} lyrics'.format(query), download=False, extra_info={'duration', 'id'})['entries']
            best_diff = abs(duration - lyric_vids[0]['duration'])
            best_option = lyric_vids[0]

            for result in reversed(lyric_vids):
                diff = abs(duration - result['duration'])
                if (diff <= best_diff + 5):
                    best_option = result
                    best_diff = diff
            
            ytdl.download([best_option['webpage_url']])
            filename = '{}.mp3'.format(best_option['id'])
        else:
            if not silent:
                print('Querying Youtube search for \"{}\"...'.format(link))
            result = ytdl.extract_info('ytsearch:{}'.format(query))
            filename = '{}.mp3'.format(result['entries'][0]['id'])
            new_name = result['entries'][0]['title']
            if not silent:
                print('Audio from: \"{}\" Download complete!'.format(new_name))
            new_name = '{}.mp3'.format(legalize_chars(new_name))
            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(filename, new_name)
    except DownloadError as e:
        if recurse:
            print('Retry unsucessful!')
            return None
        else:
            print('ERROR: Download for query: \"', query, '\" failed. Retrying...')
            filename = dl_query(query, duration=duration, silent=True, recurse=True)
    if recurse:
        print('Retry sucessful, Download complete!')
    return filename

def dl_spotify(input_link, silent=False):
    playlist_name = input_link['name']
    if len(input_link['tracks']['items'][0]) == 6:
        playlist_type = 'playlist'
    else:
        playlist_type = 'album'
        cover = []
        cover.append(input_link['images'][0]['url'])
        cover.append(playlist_name)

    print('Downloading Spotify {}: \"{}\"....'.format(playlist_type, playlist_name))
    playlist_name = legalize_chars(playlist_name)
    if not os.path.exists(playlist_name):
        os.mkdir(playlist_name)
    os.chdir(playlist_name)
    
    playlist = input_link['tracks']
    total = 0
    while playlist['next']:
        total = total + 100
        playlist = sp.next(playlist)
    tracks = playlist['items']
    total = total + len(tracks)

    tracks = playlist['items']
    if playlist_type == 'playlist':
        track = track['track']

    while playlist['next']:
        for track in tracks:
            if not silent:
                progress(count, total, '{} - {}'.format(
                    track['track']['name'], 
                    track['track']['artists'][0]['name']
                ))
            retry = dl_sp_track(track) if playlist_type == 'playlist' else dl_sp_track(track, album=cover)
            if retry:
                retries.append(retry)
            else:
                count = count + 1
        playlist = sp.next(playlist)
    for track in tracks:
        if not silent:
            progress(count, total, '{} - {}'.format(
                    track['name'], 
                    track['artists'][0]['name']
                ))
        retry = dl_sp_track(track) if playlist_type == 'playlist' else dl_sp_track(track, album=cover)
        if retry:
            retries.append(retry)
        else:
            count = count + 1

    for track in retries:
        if playlist_type == 'playlist':
            track = track['track']
        if not silent:
            progress(count, total, '{} - {}'.format(
                track['name'], 
                track['artists'][0]['name']
            ))
        retry = dl_sp_track(track) if playlist_type == 'playlist' else dl_sp_track(track, album=cover)
        if retry:
            retries.append(retry)
        else:
            count = count + 1
            
    if not silent:
        print('{}/{} 100{}, Playlist download complete!'.format(count, total, '%'))
    os.chdir(root + '/out')

def dl_sp_track(track, silent=True, album=None):
    title = track['name']
    artist = track['artists'][0]['name']
    if not silent:
        print('Downloading Spotify track: \"{} - {}\".'.format(title, artist))
    query = '{} {}'.format(title, artist)
    new_name = '{} - {}.mp3'.format(title, artist)
    new_name = legalize_chars(new_name)
    if os.path.isfile(new_name):
        return 

    duration = int(track['duration_ms'] / 1000)
    filename = dl_query(query, duration=duration)
    if not filename:
        return track

    if not os.path.isfile(new_name): 
        os.rename(filename, new_name)

    album_name = album[1] if album else track['album']['name']
    with open('{}.jpg'.format(album_name), 'wb') as handle:
        try:
            if album:
                thumbnail = requests.get(album[0]).content
            else:
                thumbnail = requests.get(track['album']['images'][0]['url']).content
            handle.write(thumbnail)
        except Exception as e:
            print('ERROR: Processing of thumbnail for \"{} - {}\" failed.'.format(title, artist))
    
    audio = MP3(new_name, ID3=ID3)
    try:
        audio.add_tags()
    except error as e:
        if 'an ID3 tag already exists' in str(e):
            pass
        else:
            print('ERROR: ID3 tags unable to be written.')
    audio.tags.add(
        APIC(
            encoding=3,
            mime='image/jpg',
            type=3, 
            desc=u'Cover',
            data=open('{}.jpg'.format(album_name), 'rb').read()
        )
    )
    audio.save(v2_version=3)    
    print(track.keys())
    audio = ID3(new_name)
    audio.add(TIT2(encoding=3, text=title))
    audio.add(TPE1(encoding=3, text=artist))
    audio.add(TALB(encoding=3, text=album_name))
    audio.save()
    os.remove('{}.jpg'.format(album_name))
    if not silent:
        print('Download complete!')

def progress(count=0, total=1, song=''):
    percentage = int(count * 1000 / total)
    print(
        '{}/{} '.format(count, total),
        percentage / 10.0, '%', 
        'Complete. Now Processing: \"{}\".'.format(song), 
    )

def legalize_chars(filename):
    illegal_chars = ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        if char in filename:
            filename = filename.replace(char, '')
    return filename

def sp_playlist_thread():
    global count, total, retries

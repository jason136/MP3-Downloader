import youtube_dl, spotipy, os, requests
from spotipy.oauth2 import SpotifyOAuth
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, error

SPOTIPY_CLIENT_ID = '***REMOVED***'
SPOTIPY_CLIENT_SECRET = '***REMOVED***'

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
    'outtmpl': '%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
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

def dl_query(query):

    try:
        result = ytdl.extract_info('ytsearch:{}'.format(query))
    except Exception as e:
        print('error during ytdl download of ', query, '\n')
        result = ytdl.extract_info('ytsearch:{}'.format(query))
    
    filename = '{}.mp3'.format(result['entries'][0]['id'])
    return filename

def dl_link(link):
    try:
        ytdl.download([link])
    except:
        print('invalid youtube video link passed')

def dl_spotify(link):

    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, 
            client_secret=SPOTIPY_CLIENT_SECRET, 
            redirect_uri='http://localhost:8000', 
            scope='user-library-read', 
            cache_path='{}/OAuthCache.txt'.format(root)
            )
        )
    except:
        print('error initializing spotify client, check internet connection')
    try:
        playlist = sp.playlist(playlist_id=link)
    except:
        print('invalid spotify playlist url')
        pass

    os.chdir(root + '/out')
    if not os.path.exists(playlist['name']):
        os.mkdir(playlist['name'])
    os.chdir(playlist['name'])
    
    playlist = playlist['tracks']
    total = 0
    while playlist['next']:
        total = total + 100
        playlist = sp.next(playlist)
    tracks = playlist['items']
    total = total + len(tracks)

    count = 0
    while playlist['next']:
        tracks = playlist['items']
        for track in tracks:
            sp_helper(track, count, total)
            count = count + 1
        playlist = sp.next(playlist)
    tracks = playlist['items']
    for track in tracks:
        sp_helper(track, count, total)
        count = count + 1

    print('{}/{} 100{} complete'.format(count, total, '%'))
    os.remove('thumbnail.jpg')
    os.chdir(root + '/out')

def sp_helper(track, count, total):
    title = track['track']['name']
    artist = track['track']['artists'][0]['name']

    percentage = int(count * 1000 / total)
    print(
        '{}/{} '.format(count, total),
        percentage / 10.0, '%', 
        ' Complete. Now Processing: {} - {}'.format(title, artist)
    )

    query = '{} {} lyrics'.format(title, artist)
    new_name = '{} - {}.mp3'.format(title, artist)
    illegal_chars = ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        if char in new_name:
            new_name = new_name.replace(char, '')

    if os.path.isfile(new_name):
        return
    filename = dl_query(query)
    if not os.path.isfile(new_name): 
        try:
            os.rename(filename, new_name)
        except Exception as e:
            os.remove(new_name)
            os.rename(filename, new_name)
            print(e, '\n')

    with open('thumbnail.jpg', 'wb') as handle:
        try:
            thumbnail = requests.get(track['track']['album']['images'][0]['url']).content
            handle.write(thumbnail)
        except Exception as e:
            print('thumbnail error on ', title, ' - ', artist)
            print(e, '\n')
    
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

if __name__ == '__main__':

    if not os.path.exists('out'):
        os.mkdir('out')

    while True:
        link = input('insert Spotify playlist link: ')

        dl_spotify(link)
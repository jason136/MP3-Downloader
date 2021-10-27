# Music Downloader
> Want music but don't have Spotify premium or youtube premium music red (whatever it's called)? Want to obtain music in the jankiest way possible? Want to watch as the cute lil songs populate your hard drive automatically? If you answered yes to at least two of these questions then this music downloader is for you!

---

# Usage:
Requirements are Python and FFmpeg, reccomended latest versions but tested on Python 3.9 and FFmpeg 4.4. 
FFpmeg must be installed and included in the PATH to avoid codec/encoding errors. 

Used modules include youtube_dl, spotipy, os, requests, and mutagen
This repository does not include any executebles, so these modules will have to be installed for the script to work.

The main.py can be executed to download music from the python console (sparks joy), while importing and calling its helper methods also works (does not spark joy, you will have to see the messy code). Helper methods will be documented below the console method how-to. 

If it does not already exist, the script will create a directory in its location called 'out', where all music will be downloaded to. 

A general usage tip: the script will encounter 403 Forbidden errors but will recovery and retry the download automatically. If the script seems stuck, please close the instance and try the download again; the script will pick up from where it left off. 

If you notice your wifi speed is slower but your cpu is stronger, consider increasing the number of active threads. This can be done by changing the variable at the top of [mp3_dl.py](mp3_dl.py), the default value is 10. Conversely, if your wifi is fast but cpu is slow, consider decreasing this number for better results. 

# Spotify
Music downloaded from Spotify will include title, album, artist, track number, and album art metadata embedded in the mp3 as an ID3 tag. 

Spotify playlists, albums, and tracks can be downloaded by inputting the link of the playlist when it is called for. If it is the first time using the Spotify API or the refresh token has expired the user will have to preform an OAuth authentication before proceeding. 

For albums and playlists, the files will be downloaded in the 'out' folder in another folder of the album/playlist's name, for tracks it will just be in the 'out' folder. 

Spotify links need to be provided in the following forms for the script to work correctly:
- Spotify Playlists:
    ```https://open.spotify.com/playlist/73DYbNJDh5eWZ2zuzjpbRG?si=a26f27dbf2834883```
- Spotify Albums:
    ```https://open.spotify.com/album/3Gt7rOjcZQoHCfnKl5AkK7?si=eokGV3XXSICNbYt_CM6o0g&dl_branch=1```
- Spotify Tracks:
    ```https://open.spotify.com/track/1YrnDTqvcnUKxAIeXyaEmU?si=c41eb834e184467d```

# Youtube
Music downloaded from Youtube will always come as-is, without any form of metadata. 

Youtube playlists and tracks can be downloaded in the same fashon as Spotify playlists and tracks, with playlists in their own folder and tracks directly in 'out'. 

Youtube links need to be provided in the following forms for the script to work correctly, however, the download may still work as long as videoID or playlistID is present:
- Youtube Playlists:
    ```https://www.youtube.com/playlist?list=PLef6-19fy90AbWJilApi31AwXHgjwbY4d```
- Youtube Tracks:
    ```https://www.youtube.com/watch?v=dQw4w9WgXcQ```

# DISCLAIMERS
All music is downloaded from YouTube

- If it's a super obscure song or it has a misleading title the downloaded audio file may not be what was expected
- The audio quality is the best found on YouTube and no better 
- YouTube creator sometimes add intros or outtros even to lytic videos (idk why it sucks i know).
- Artists sometimes add cutscenes or sound effects

All of these are remedied to an extent, ie matching up the closest song duration and looking for best audio quality, but it will not be perfect for everything. 

# Reference
```python
dl_yt_playlist(link, silent=False):
```
Downloads a Youtube playlist  
Parameters:
- link: str of Youtube playlist link to download from
- silent: bool for whether to return status updates or not

```python
dl_yt_video(link, silent=True, recurse=False):
```
Downloads a Youtube video from a Youtube link  
Parameters:
- link: str of Youtube video link to download from
- silent: bool for whether to return status update or not
- recurse: int, 4-recurse times to recursively retry downloads

```python
dl_query(query, silent=True, duration=None, recurse=0):
```
Downloads a Youtube video from a search query  
Parameters:
- query: str of Youtube query to search and download from
- silent: bool for whether to return status update or not
- duration: int of seconds to search for closest duration
- recurse: int, 4-recurse times to recursively retry downloads

```python
dl_spotify(input_link, silent=False):
```
Downloads a Spotify playlist or album  
Parameters:
- link: str of Spotify playlist/album link to download from
- silent: bool for whether to return status update or not

```python
dl_sp_track(track, silent=True, album=None):
```
Downloads a Spotify track  
Parameters:
- link: str of Youtube video link to download from
- silent: bool for whether to return status update or not
- album: list containing metadata not obtainable from track object
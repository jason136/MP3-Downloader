# Music Downloader
> Want music but don't have spotify premium or youtube premium music red (whatever it's called)? Want to obtain music in the jankiest way possible? Want to watch as the cute lil songs populate your hard drive automatically?If you answered yes to at least two of these questions then this music downloader is for you!

---

# Usage:
Requirements are Python and FFmpeg, reccomended latest versions but tested on Python 3.9 and FFmpeg 4.4. 

Used modules include youtube_dl, spotipy, os, requests, and mutagen
This repository does not include any executebles, so these modules will have to be installed for the script to work.

The script currently only outputs mp3 files. 

The script can be executed to download music from the python console (sparks joy) or by importing and calling its helper methods (does not spark joy, you will have to see the messy code). Only the python console version will be documented below. 

If it does not already exist, the script will create a directory in its location called out, where all music will be downloaded to. 

///more coming///

## Spotify Playlists
Music downloaded from spotify will include title, album, artist, and album art metadata embedded in the mp3. 

Spotify playlists can be downloaded in their entirety by inputting the link of the playlist when it is called for. If it is the first time using the Spotify API or the refresh token has expired the user will have to preform an OAuth authentication before proceeding. 

The playlist will be downloaded in the 'out' folder in another folder of the playlist's name

As of now only Spotify playlists are supported, albums or artist urls will result in error

# DISCLAIMERS
All music is downloaded from YouTube

* If it's a super obscure song or it has a misleading title the downloaded audio file may not be what was expected
* The audio quality is the best found on YouTube and no better 
* YouTube creator sometimes add intros or outtros even to lytic videos (idk why it sucks i know).
* Artists sometimes add cutscenes or sound effects

All of these are remedied to an extent, ie matching up the closest song duration and looking for best audio quality, but it will not be perfect for everything. 
on das a lie actwaly i was only thinking abt the duration thing but im thinking long abt it an itll be soon 

## todo
youtube playlist support
youtube individual song support
spotify individual song support
spotify album support
spotify artist support
^soon^

better error handling
^ill get to it soon^

other sites?
^unlikely ill get to it^
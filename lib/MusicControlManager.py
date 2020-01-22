'''
 The player functions for Spotify (like play, pause, etc. - everything that is 
 in Cody Music for Javascript), as well as the AppleScript commands, could be 
 in a separate file (MusicControlManager).
'''
import os
import requests
import sublime_plugin
import sublime
from threading import Thread, Timer, Event
import webbrowser

from .Playlists import *
from .SoftwareMusic import *
# from .SoftwareUtil import *
# from ..Software import *
# from .MusicCommandManager import *


# Play song from playlist without playlist_id
def playThisSong(currentDeviceId, track_id):
    if isMac() == True and userTypeInfo() == "non-premium":
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}"'
        '''.format(track_id) 
        os.system(script)
        print("Played from desktop")

    else:    
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        data = {}
        try:
            print("track_id",track_id)
            data = {"uris":["spotify:track:" + track_id]}
            payload = json.dumps(data)
            playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playThisSong",e)
    currentTrackInfo()


# Play song from playlist using playlist_id and track_id
def playSongFromPlaylist(currentDeviceId, playlistid, track_id):
    global playlist_id
    playlist_id = playlistid
    if isMac() == True and userTypeInfo() == "non-premium":
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}" in context "spotify:playlist:{}"'
        '''.format(track_id,playlist_id) 
        os.system(script)
        print("Played from desktop")
        pass

    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
        data = {}
        try:
            data["context_uri"] = "spotify:playlist:"+ playlist_id
            data['offset'] =  {"uri": "spotify:track:"+ track_id}
            payload = json.dumps(data)
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playSongFromPlaylist",e)
    currentTrackInfo()


# Song's Controls: Play
def playSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium": 
        playPlayer()
        currentTrackInfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        # print("headers",headers)
        # print(getActiveDeviceInfo())
        playstr = SPOTIFY_API + "/v1/me/player/play?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()#currentDeviceId
        plays = requests.put(playstr, headers=headers)
        # print(plays.status_code)
        print("Web player Working | Playing :", plays.status_code, "|",plays.text)
        currentTrackInfo()

# Song's Controls: Pause
def pauseSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium":
        print(isMac())
        pausePlayer()
        currentTrackInfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        pausestr = SPOTIFY_API + "/v1/me/player/pause?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()#currentDeviceId
        pause = requests.put(pausestr, headers=headers)
        print("Web player Working | Paused ...", pause.status_code, "|",pause.text)
        currentTrackInfo()

# Song's Controls: Next
def nextSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium":
        nextTrack()
        currentTrackInfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        nxtstr = SPOTIFY_API + "/v1/me/player/next?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()#currentDeviceId
        nxt = requests.post(nxtstr, headers=headers)
        print("Web player Working | Next ...", nxt.status_code, "|",nxt.text)
        currentTrackInfo()

# Song's Controls: Previous
def previousSong():
    getActiveDeviceInfo()
    # print("isMac",isMac(),'|',userTypeInfo())
    if isMac() == True and userTypeInfo() == "non-premium":
        previousTrack()
        currentTrackInfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        prevstr = SPOTIFY_API + "/v1/me/player/previous?" + ACTIVE_DEVICE.get('device_id')
        prev = requests.post(prevstr, headers=headers)
        print("Web player Working | previous ...", prev.status_code, "|",prev.text)
        # showStatus("▶️ "+currentTrackInfo()[0])# if currentTrackInfo()[1] is True else print("Paused",currentTrackInfo()[0])
        currentTrackInfo()

# Launch Spotify player
def startPlayer():
    args = "open -a Spotify"
    os.system(args)

# Song's Controls: Play from Desktop
def playPlayer():
    play = '''
    osascript -e 'tell application "Spotify" to play'
    '''
    os.system(play)


# Song's Controls: Pause from Desktop
def pausePlayer():
    pause = '''
    osascript -e 'tell application "Spotify" to pause'  
    '''
    os.system(pause)
    # args = { "osascript", "-e", "tell application \""+ playerName + "\" to pause" }
    # return runCommand(args, None)

# Song's Controls: Previous from Desktop
def previousTrack():
    prev = '''
    osascript -e 'tell application "Spotify" to play (previous track)'
    ''' 
    os.system(prev)

# Song's Controls: Next from Desktop
def nextTrack():
    nxt = '''
    osascript -e 'tell application "Spotify" to play (next track)'
    '''
    os.system(nxt)

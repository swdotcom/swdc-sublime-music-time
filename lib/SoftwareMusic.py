from threading import Thread, Timer, Event
import sublime_plugin
import sublime
import copy
import time

from .SoftwareHttp import *
from .SoftwareUtil import *
from ..Software import *
from .MusicPlaylistProvider import *
from .SoftwareMusic import *

current_track_info = {}
ACTIVE_DEVICE = {}
DEVICES = []
Liked_songs_ids = []

current_track_id = ""


# To fetch and show music-time dashboard
def getMusicTimedashboard():
    api = "/dashboard/music"
    resp = requestIt("GET", api)
    if resp.status_code == 200:
        print("Music Time: launching MusicTime.txt")
    else:
        print('getMusicTimedashboard error\n', resp.text)

    file = getDashboardFile()
    with open(file, 'w', encoding='utf-8') as f:
        f.write(resp.text)

    file = getDashboardFile()
    sublime.active_window().open_file(file)


def gatherMusicInfo():
    global current_track_info

    # get the music track playing
    # the trackInfo should be a dictionary
    trackInfo = getTrackInfo()
    now = round(time.time())
    start = now
    local_start = now - time.timezone

    # state = "nice" if is_nice else "not nice"
    currentTrackId = current_track_info.get("id", None)
    trackId = trackInfo.get("id", None)
    trackType = trackInfo.get("type", None)

    if (trackId is not None and trackType == "itunes"):
        itunesTrackState = getItunesTrackState()
        trackInfo["state"] = itunesTrackState
        try:
            # check if itunes is found, if not it'll raise a ValueError
            idx = trackId.index("itunes")
            if (idx == -1):
                trackId = "itunes:track:" + str(trackId)
                trackInfo["id"] = trackId
        except ValueError:
            # set the trackId to "itunes:track:"
            trackId = "itunes:track:" + str(trackId)
            trackInfo["id"] = trackId
    elif (trackId is not None and trackType == "spotify"):
        spotifyTrackState = getSpotifyTrackState()
        trackInfo["state"] = spotifyTrackState

    trackState = trackInfo.get("state", None)
    duration = trackInfo.get("duration", None)

    if (duration is not None):
        duration_val = float(duration)
        if (duration_val > 1000):
            trackInfo["duration"] = duration_val / 1000
        else:
            trackInfo["duration"] = duration_val
    '''
    conditions:
    1) if the currentTrackInfo doesn't have data and trackInfo does
       that means we should send it as a new song starting
    2) if the currentTrackInfo has data and the trackInfo does
       and has the same trackId, then don't send the payload
    3) if the currentTrackInfo has data and the trackInfo has data
       and doesn't have the same trackId then send a payload
       to close the old song and send a payload to start the new song
    '''
    if (trackId is not None):
        isPaused = False

        if (trackState != "playing"):
            isPaused = True

        if (currentTrackId is not None and (currentTrackId != trackId or isPaused is True)):
            # update the end time of the previous track and post it
            current_track_info["end"] = start - 1
            gatherCodingDataAndSendSongSession(current_track_info)
            response = requestIt("POST", "/data/music",
                                 json.dumps(current_track_info), getItem("jwt"))
            if (response is None):
                log("Code Time: error closing previous track")
            # re-initialize the current track info to an empty object
            current_track_info = {}

        if (isPaused is False and (currentTrackId is None or currentTrackId != trackId)):
            # starting a new song
            trackInfo["start"] = start
            trackInfo["local_start"] = local_start
            trackInfo["end"] = 0
            gatherCodingDataAndSendSongSession(current_track_info)
            response = requestIt("POST", "/data/music",
                                 json.dumps(trackInfo), getItem("jwt"))
            if (response is None):
                log("Code Time: error sending new track")

            # clone the trackInfo to the current_track_info
            for key, value in trackInfo.items():
                current_track_info[key] = value
    else:
        if (currentTrackId is not None):
            # update the end time since there are no songs coming
            # in and the previous one is stil available
            current_track_info["end"] = start - 1
            gatherCodingDataAndSendSongSession(current_track_info)
            response = requestIt("POST", "/data/music",
                                 json.dumps(current_track_info), getItem("jwt"))
            if (response is None):
                log("Code Time: error closing previous track")

        # re-initialize the current track info to an empty object
        current_track_info = {}

    # fetch the daily kpm session info in 15 seconds
    gatherMusicInfoTimer = Timer(15, gatherMusicInfo)
    gatherMusicInfoTimer.start()
    pass

def gatherCodingDataAndSendSongSession(current_track_info):
    # end current keystroke data gathering
    PluginData.send_all_datas()


# Fetch Active device  and Devices(all device including inactive devices)
def getActiveDeviceInfo():
    # print("{}".format(getItem('spotify_access_token')))
    global DEVICES
    # global playlist_id
    # global current_song

    api = "/v1/me/player/devices"
    getdevs = requestSpotify("GET", api)

    if getdevs.status_code == 200:

        devices = getdevs.json()
        DEVICES = []
        # try:
        if devices['devices'] == []:# and userTypeInfo() == "premium":
            msg = sublime.ok_cancel_dialog("Please launch Spotify player", "Ok")
            if msg is True:
                current_window = sublime.active_window()
                current_window.run_command("select_player")
            else:
                pass

        else:
            for i in devices:
                for j in range(len(devices['devices'])):

                    # get devices name list to display in tree view
                    DEVICES.append(devices['devices'][j]['name'])

                    if devices['devices'][j]['is_active'] == True or devices['devices'][j]['type'] == "Computer":
                        ACTIVE_DEVICE['device_id'] = devices['devices'][j]['id']
                        ACTIVE_DEVICE['name'] = devices['devices'][j]['name']
                        print("Music Time: Active device found > ",
                              ACTIVE_DEVICE['name'])

            # DEVICES.append(devices['devices'][j]['name'])
            print("ACTIVE_DEVICE", ACTIVE_DEVICE)
            print("DEVICES :", DEVICES)
            print("Music Time: Number of connected devices: ", len(DEVICES))
            # print("ACTIVE_DEVICE",ACTIVE_DEVICE)
    elif getdevs.status_code == 401:
        refreshSpotifyToken()

        # except Exception as E:
        #     print("Music Time: getActiveDeviceInfo", E)

    # refreshDeviceStatus()

# Function to check whether current track is liked or not
check_liked_songs = lambda x :"  ❤️" if (x in Liked_songs_ids) else " "
# ❤️ https://emojipedia.org/red-heart/
# ♥️ https://emojipedia.org/heart-suit/


def getLikedSongsIds():
    global Liked_songs_ids

    api = "/v1/me/tracks"
    tracklist = requestSpotify("GET", api)
    if tracklist.status_code == 200:
        track_list = tracklist.json()
        ids = []
        names = []
        tracks = {}
        for i in track_list['items']:
            ids.append(i['track']['id'])
            names.append(i['track']['name'])
            tracks = tuple(zip(names, ids))
        Liked_songs_ids = ids
        # print("Liked_songs_ids",Liked_songs_ids)
        return Liked_songs_ids
    else:
        return []

# Liked_songs_ids = getLikedSongs()

def currentTrackInfo():
    # global ACTIVE_DEVICE
    trackstate = ''
    trackinfo = ''
    Liked_songs_ids = getLikedSongsIds()

    # global current_track_id
    # try:
    if isMac() == True and userTypeInfo() == "non-premium":
        '''For MAC user get info from desktop player'''
        # startPlayer()
        try:
            trackstate = getSpotifyTrackState()
            trackinfo = getTrackInfo()["name"]
            track_id = getTrackInfo()['id'][14:]
            isLiked = check_liked_songs(track_id)

        # getTrackInfo {'duration': '268210', 'state': 'playing', 'name': 'Dhaga Dhaga', \
        # 'artist': 'harsh wavre', 'genre': '', 'type': 'spotify', 'id': 'spotify:track:79TKZDxCWEonklGmC5WbDC'}
            if trackstate == "playing":
                showStatus("Now Playing "+str(trackinfo) + isLiked)
                # print("Playing "+trackinfo)
            else:
                showStatus("Paused "+str(trackinfo) + isLiked)
                # print("Paused "+trackinfo)
        except Exception as e:
            print("Music time: player not found", e)
            showStatus("Connect Premium")

    else:
        try:
            # print("ACTIVE_DEVICE in currentTrackInfo 1:",ACTIVE_DEVICE)
            if ACTIVE_DEVICE == {}:
                getActiveDeviceInfo()

            api = "/v1/me/player/currently-playing?" + ACTIVE_DEVICE.get('device_id')
            track = requestSpotify("GET", api)

            if track.status_code == 200:
                trackinfo = track.json()['item']['name']
                trackstate = track.json()['is_playing']
                track_id = track.json()['item']['id']
                current_track_id = track_id
                # print("current_track_id",current_track_id)
                isLiked = check_liked_songs(track_id)
                # print("Liked_songs_ids:",Liked_songs_ids,"\nisLiked:",isLiked) 

                if trackstate == True:
                    showStatus("Now Playing "+str(trackinfo) + isLiked)
                    # print("Playing "+trackinfo)
                else:
                    showStatus("Paused "+str(trackinfo) + isLiked)
                    # print("Paused "+trackinfo)

            elif track.status_code == 401:
                # showStatus("Loading . . . ")
                showStatus("Spotify Connected")
                try:
                    refreshSpotifyToken()
                    currentTrackInfo()
                except KeyError:
                    showStatus("Connect Spotify")

        # except Exception as e:
        #     print('Music Time: currentTrackInfo', e)
        #     showStatus("Spotify Connected. No Active device found.")
        except Exception as ex:
            print('Music Time: currentTrackInfo ConnectionError')
            showStatus("Spotify Connected")
            time.sleep(5)
            pass
    refreshStatusBar()


# Continuous refresh statusbar
def refreshStatusBar():
    try:
        t = Timer(10, currentTrackInfo)
        t.start()
        # schedule.every(5).seconds.do(currentTrackInfo())
        # while True:
        #     schedule.run_pending()
    except Exception as E:
        print("Music Time: refreshStatusBar", E)
        showStatus("No device found . . . ")
        # showStatus("Connect Spotify")
        pass

# Continuous refresh devices
# def refreshDeviceStatus():
#     try:
#         t = Timer(60, getActiveDeviceInfo)
#         t.start()
#     except Exception as E:
#         print("Music Time: refreshStatusBar", E)
#         showStatus("No device found . . . ")
#         # showStatus("Connect Spotify")
#         pass


#  function for checking user
def check_user(): return "Spotify Connected" if (userTypeInfo() == "premium") else (
    "Connect Premium" if (userTypeInfo() == "open") else "Connect Spotify")

# to get all device names



# # Show Active/connected/no device msg


# def myToolTip():
#     # global DEVICES
#     # getActiveDeviceInfo()
#     header = "<h3>Music Time</h3>"
#     connected = '<p><b>{}</b></p>'.format(check_user())
#     close_msg = '(Press <b>Esc</b> to close)'

#     if len(activeDeviceName()) > 0:
#         show_str = activeDeviceName()
#         # print(show_str)
#         listen_on = '<p><b>Listening on </b><i>{}</i></p>'.format(show_str)
#         body = "<body>" + header + connected + listen_on + close_msg + "</body>"
#         # print("\n",body)

#     else:
#         if getDeviceNames() == "Device not found":
#             show_str = getDeviceNames()
#             # print(show_str)
#             no_device_msg = '<p><i>No device found</i></p>'
#             body = "<body>" + header + connected + no_device_msg + close_msg + "</body>"
#             # print("\n",body)
#         else:
#             show_str = getDeviceNames()
#             # print(show_str)
#             available_on = '<p><b>Connected on </b><i>{}</i></p>'.format(
#                 show_str)
#             body = "<body>" + header + connected + available_on + close_msg + "</body>"
#     # print("\n",body)
#     return body


# To open spotify playlist/track web url
def openTrackInWeb(playlist_ids, current_songs):
    global playlist_id
    global current_song
    playlist_id = playlist_ids
    current_song = current_songs

    print("open Track In Web", "\nplaylist_id :", playlist_id,
          "\ncurrent_song:", current_song, "\nACTIVE_DEVICE", ACTIVE_DEVICE)

    if userTypeInfo() == "premium" and len(ACTIVE_DEVICE.values()) == 0:

        if len(current_song) > 0 and (playlist_id == "" or playlist_id == None):
            print("without playlist id ")
            url = SPOTIFY_WEB_PLAYER + "/track/" + current_song

        elif len(playlist_id) > 0 and len(current_song) > 0:
            print("with playlist id ")
            # https://open.spotify.com/playlist
            url = SPOTIFY_WEB_PLAYER + "/playlist/" + \
                playlist_id + "?highlight=spotify:track:" + current_song

        else:
            url = SPOTIFY_WEB_PLAYER
        # player = sublime.ok_cancel_dialog("Please open Spotify player", "Ok")
        webbrowser.open(url)
        time.sleep(5)

    elif userTypeInfo() != "premium":
        args = "open -a Spotify"
        os.system(args)
    
    # elif current_song is None:
    #     message_dialog = sublime.message_dialog("Songs not found")
    #     pass

    else:
        pass

# ---------------------------------------------------plug292

# class SelectPlayer(sublime_plugin.WindowCommand):

#     def run(self):
#         player = ["Launch Web Player", "Launch Desktop Player"]
#         self.window.show_quick_panel(player, lambda id: self.on_done(id, player))

#     def on_done(self, id, player):
#         if id >= 0 and player[id] == "Launch Web Player":
#             webbrowser.open("https://open.spotify.com/")

#         else:
#             # open desktop
#             result = subprocess.Popen("cmd /c spotify.exe", shell=True,
#                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             output,error = result.communicate()

#             if len(error) is not 0:
#                 print("Spotify not found in C")
#                 result = subprocess.Popen("%APPDATA%/Spotify/Spotify.exe", shell=True,
#                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#                 output,error = result.communicate()
#                 if len(error) is not 0:
#                     print("Desktop player not found. Opening Web player. \nError:",error)
            
            









#----------------------------------------------plug57
existingtrack = {}
playingtrack = {}

def isValidExistingTrack():
    if existingtrackid is True:
        return True
    return False


def isValidTrack():
    if playingtrackid is True:
        return True
    return False


def isNewTrack():
    if existingtrackid != playingtrackid:
        return True 
    return False


def trackIsdone(playingrack):
    if playingtrack["progress_ms"] == None:
        return False
    
    playingTrackId = playingtrack["id"]

    if playingTrackId and playingtrack["progress_ms"] > 0:
        hasProgress = True
    else:
        hasProgress = False
    # return hasProgress

    if playingTrackId is not None or (playingtrack["state"] != TrackStatus['playing'] ):
        isPausedOrNotPlaying = True
    isPausedOrNotPlaying = False
    # return isPausedOrNotPlaying

    if isPausedOrNotPlaying is True and hasProgress is not None:
        return true
    return false


def trackIsLongPaused(playingTrack):
    if playingTrack["progress_ms"] == None:
        return False
    
    if playingTrack:
        if playingTrack["id"] is not None:
            playingTrackId = playingTrack["id"]
        else:
            playingTrackId = None

    pauseThreshold = 60 * 5

    pass


def isEndInRange(playingTrack):
    if playingTrack is None or playingTrack['id'] is None:
        return False
    
    buffer_val = playingTrack['duration_ms'] * 0.07
    if (playingTrack['duration_ms'] - buffer_val) <= playingTrack['duration_ms']:
        return True


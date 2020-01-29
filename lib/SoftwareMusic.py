from threading import Thread, Timer, Event
import sublime_plugin
import sublime
import copy
import time

from .SoftwareHttp import *
from .SoftwareUtil import *
from ..Software import *
# from .MusicControlManager import *

currentTrackInfo = {}
ACTIVE_DEVICE = {}
DEVICES = []


# To fetch and show music-time dashboard
def getMusicTimedashboard():
    jwt = getItem("jwt")
    headers = {'content-type': 'application/json', 'Authorization': jwt}
    dash_url = SOFTWARE_API + "/dashboard/music"
    # dash_url = "https://api.software.com/dashboard?plugin=music-time&linux=false&html=false"
    resp = requests.get(dash_url, headers=headers)
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
    global currentTrackInfo

    # # get the music track playing
    # # the trackInfo should be a dictionary
    # trackInfo = getTrackInfo()
    # now = round(time.time())
    # start = now
    # local_start = now - time.timezone

    # # state = "nice" if is_nice else "not nice"
    # currentTrackId = currentTrackInfo.get("id", None)
    # trackId = trackInfo.get("id", None)
    # trackType = trackInfo.get("type", None)

    # if (trackId is not None and trackType == "itunes"):
    #     itunesTrackState = getItunesTrackState()
    #     trackInfo["state"] = itunesTrackState
    #     try:
    #         # check if itunes is found, if not it'll raise a ValueError
    #         idx = trackId.index("itunes")
    #         if (idx == -1):
    #             trackId = "itunes:track:" + str(trackId)
    #             trackInfo["id"] = trackId
    #     except ValueError:
    #         # set the trackId to "itunes:track:"
    #         trackId = "itunes:track:" + str(trackId)
    #         trackInfo["id"] = trackId
    # elif (trackId is not None and trackType == "spotify"):
    #     spotifyTrackState = getSpotifyTrackState()
    #     trackInfo["state"] = spotifyTrackState

    # trackState = trackInfo.get("state", None)
    # duration = trackInfo.get("duration", None)

    # if (duration is not None):
    #     duration_val = float(duration)
    #     if (duration_val > 1000):
    #         trackInfo["duration"] = duration_val / 1000
    #     else:
    #         trackInfo["duration"] = duration_val

    # # conditions
    # # 1) if the currentTrackInfo doesn't have data and trackInfo does
    # #    that means we should send it as a new song starting
    # # 2) if the currentTrackInfo has data and the trackInfo does
    # #    and has the same trackId, then don't send the payload
    # # 3) if the currentTrackInfo has data and the trackInfo has data
    # #    and doesn't have the same trackId then send a payload
    # #    to close the old song and send a payload to start the new song

    # if (trackId is not None):
    #     isPaused = False

    #     if (trackState != "playing"):
    #         isPaused = True

    #     if (currentTrackId is not None and (currentTrackId != trackId or isPaused is True)):
    #         # update the end time of the previous track and post it
    #         currentTrackInfo["end"] = start - 1
    #         response = requestIt("POST", "/data/music",
    #                              json.dumps(currentTrackInfo), getItem("jwt"))
    #         if (response is None):
    #             log("Code Time: error closing previous track")
    #         # re-initialize the current track info to an empty object
    #         currentTrackInfo = {}

    #     if (isPaused is False and (currentTrackId is None or currentTrackId != trackId)):
    #         # starting a new song
    #         trackInfo["start"] = start
    #         trackInfo["local_start"] = local_start
    #         trackInfo["end"] = 0
    #         response = requestIt("POST", "/data/music",
    #                              json.dumps(trackInfo), getItem("jwt"))
    #         if (response is None):
    #             log("Code Time: error sending new track")

    #         # clone the trackInfo to the currentTrackInfo
    #         for key, value in trackInfo.items():
    #             currentTrackInfo[key] = value
    # else:
    #     if (currentTrackId is not None):
    #         # update the end time since there are no songs coming
    #         # in and the previous one is stil available
    #         currentTrackInfo["end"] = start - 1
    #         response = requestIt("POST", "/data/music",
    #                              json.dumps(currentTrackInfo), getItem("jwt"))
    #         if (response is None):
    #             log("Code Time: error closing previous track")

    #     # re-initialize the current track info to an empty object
    #     currentTrackInfo = {}

    # # fetch the daily kpm session info in 15 seconds
    # gatherMusicInfoTimer = Timer(15, gatherMusicInfo)
    # gatherMusicInfoTimer.start()
    pass


# Fetch Active device  and Devices(all device including inactive devices)
def getActiveDeviceInfo():
    # print("{}".format(getItem('spotify_access_token')))
    global DEVICES
    global playlist_id
    global songs_tree

    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    get_device_url = SPOTIFY_API + "/v1/me/player/devices"
    getdevs = requests.get(get_device_url, headers=headers)

    devices = getdevs.json()
    DEVICES = []
    try:
        if devices['devices'] == [] and userTypeInfo() == "premium":
            try:
                url = "https://open.spotify.com/album/"+playlist_id+"?highlight=spotify:track:"+songs_tree
            except:
                # url = "https://open.spotify.com/track/"+songs_tree
            # else:
                url = "https://open.spotify.com/"
            # player = sublime.ok_cancel_dialog("Please open Spotify player", "Ok")
            # if player:
            webbrowser.open(url)
            # else:
                # print("Music Time: No active device found.")
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

    except Exception as E:
        print("Music Time: getActiveDeviceInfo", E)

    refreshDeviceStatus()


def currentTrackInfo():
    trackstate = ''
    trackinfo = ''
    # try:
    if isMac() == True and userTypeInfo() == "non-premium":
        '''For MAC user get info from desktop player'''
        # startPlayer()
        try:
            trackstate = getSpotifyTrackState()
            trackinfo = getTrackInfo()["name"]
        # getTrackInfo {'duration': '268210', 'state': 'playing', 'name': 'Dhaga Dhaga', \
        # 'artist': 'harsh wavre', 'genre': '', 'type': 'spotify', 'id': 'spotify:track:79TKZDxCWEonklGmC5WbDC'}
            if trackstate == "playing":
                showStatus("Now Playing "+str(trackinfo) +
                           " on " + ACTIVE_DEVICE.get('name'))
                # print("Playing "+trackinfo)
            else:
                showStatus("Paused "+str(trackinfo) +
                           " on " + ACTIVE_DEVICE.get('name'))
                # print("Paused "+trackinfo)
        except Exception as e:
            print("Music time: player not found", e)
            showStatus("Connect Premium")

    else:
        try:
            headers = {"Authorization": "Bearer {}".format(
                getItem('spotify_access_token'))}
            trackstr = SPOTIFY_API + "/v1/me/player/currently-playing?" + \
                ACTIVE_DEVICE.get('device_id')  # getActiveDeviceInfo()
            track = requests.get(trackstr, headers=headers)

            if track.status_code == 200:
                trackinfo = track.json()['item']['name']
                trackstate = track.json()['is_playing']
                # print(trackinfo,"|",trackstate)
                if trackstate == True:
                    showStatus("Now Playing "+str(trackinfo) +
                               " on "+ACTIVE_DEVICE.get('name'))
                    # print("Playing "+trackinfo)
                else:
                    showStatus("Paused "+str(trackinfo) +
                               " on "+ACTIVE_DEVICE.get('name'))
                    # print("Paused "+trackinfo)

            else:
                # showStatus("Loading . . . ")
                showStatus("Spotify Connected")
                try:
                    refreshSpotifyToken()
                    currentTrackInfo()
                except KeyError:
                    showStatus("Connect Spotify")

        except Exception as e:
            print('Music Time: currentTrackInfo', e)
            showStatus("Spotify Connected. No Active device found.")
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


def refreshDeviceStatus():
    try:
        t = Timer(60, getActiveDeviceInfo)
        t.start()
    except Exception as E:
        print("Music Time: refreshStatusBar", E)
        showStatus("No device found . . . ")
        # showStatus("Connect Spotify")
        pass


# Lambda function for checking user
check_user = lambda : "Spotify Connected" if (userTypeInfo() == "premium") else ("Connect Premium" if (userTypeInfo() == "open") else "Connect Spotify")


def myToolTip():
    # global DEVICES
    # getActiveDeviceInfo()
    header = "<h3>Music Time</h3>"
    # connected = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">{}</a></p>'.format(check_user())
    connected = '<p><b>{}</b></p>'.format(check_user())
    listen_on = '<p><b>Listening on </b><i>{}</i></p>'.format(ACTIVE_DEVICE.get('name'))
    # print("DEVICES",DEVICES)
    available_on = '<p><b>Connected on </b><i>{}</i></p>'.format(','.join(DEVICES))
    no_device_msg = '<p><i>No device found</i></p>'
    close_msg = '(Press <b>Esc</b> to close)'

    if len(ACTIVE_DEVICE.values()) != 0:
        body = "<body>" + header + connected + listen_on + available_on + close_msg + "</body>"

    elif len(DEVICES) == 0 and len(ACTIVE_DEVICE.values()) == 0:
        body = "<body>" + header + connected + no_device_msg +  close_msg + "</body>"

    else:
        body = "<body>" + header + connected + available_on + close_msg + "</body>"
        
    print(body)
    return body

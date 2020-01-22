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


# To fetch and shoe music-time dashboard


def getMusicTimedashboard():
    # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTI0MTYwLCJpYXQiOjE1NzYwNzI2NDZ9.96PjeOosPVsA4mfWwizhxJ5Skqy8Onvia8Oh-mQCHf8"
    jwt = getItem("jwt")
    headers = {'content-type': 'application/json', 'Authorization': jwt}
    dash_url = SOFTWARE_API + "/dashboard/music"
    # dash_url = "https://api.software.com/dashboard?plugin=music-time&linux=false&html=false"
    resp = requests.get(dash_url, headers=headers)
    if resp.status_code == 200:
        print("Music Time: launch MusicTime.txt")
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
    # global currentDeviceId
    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    get_device_url = SPOTIFY_API + "/v1/me/player/devices"
    getdevs = requests.get(get_device_url, headers=headers)

    devices = getdevs.json()
    # print(devices)
    try:
        if devices['devices'] == [] and userTypeInfo() == "premium":
            url = "https://open.spotify.com/"
            webbrowser.open(url)
            print("Music Time: No active device found. Opening Spotify player")
        else:
            for i in devices:
                for j in range(len(devices['devices'])):
                    DEVICES = []
                    # get devices name list to display in tree view
                    DEVICES.append(devices['devices'][j]['name'])

                    if devices['devices'][j]['is_active'] == True:
                        ACTIVE_DEVICE['device_id'] = devices['devices'][j]['id']
                        ACTIVE_DEVICE['name'] = devices['devices'][j]['name']
                        print("Music Time: Active device found > ",
                              ACTIVE_DEVICE['name'])

            DEVICES.append(devices['devices'][j]['name'])
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

        # print("BEFORE",currentTrackInfo)
        # refreshStatusBar()
        # print("After",currentTrackInfo)

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
                showStatus(
                    "No Active device found. Please open Spotify player and play the music ")
                try:
                    refreshSpotifyToken()
                    currentTrackInfo()
                except KeyError:
                    showStatus("Connect Spotify")

        except Exception as e:
            print('Music Time: currentTrackInfo', e)
            showStatus(
                "No Active device found. Please open Spotify player and play the music ")
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
        # schedule.every(5).seconds.do(currentTrackInfo())
        # while True:
        #     schedule.run_pending()
    except Exception as E:
        print("Music Time: refreshStatusBar", E)
        showStatus("No device found . . . ")
        # showStatus("Connect Spotify")
        pass

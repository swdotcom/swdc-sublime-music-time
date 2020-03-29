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
from .SoftwareOffline import *

existing_track = {}
ACTIVE_DEVICE = {}
DEVICES = []
Liked_songs_ids = []

current_track_id = ""


# To fetch and show music-time dashboard
def getMusicTimedashboard():
    api = "/dashboard/music"
    # resp = requestIt("GET", api, None, getItem("jwt"))
    # print("type",type(resp))
    # print("resp",resp["status"])
    headers = {'content-type': 'application/json', 'Authorization': getItem("jwt")}
    dash_url = SOFTWARE_API + api
    # dash_url = "https://api.software.com/dashboard?plugin=music-time&linux=false&html=false"
    resp = requests.get(dash_url, headers=headers)
    if resp.status_code == 200:
    # if resp["status"] == 200:
        print("Music Time: launching MusicTime.txt")
    else:
        print('getMusicTimedashboard error\n')

    file = getDashboardFile()
    with open(file, 'w', encoding='utf-8') as f:
        f.write(resp.text)

    file = getDashboardFile()
    sublime.active_window().open_file(file)


def gatherMusicInfo():
    global existing_track

    sendTrackSession = False

    # check if the use has spotify access
    access_token = getItem("spotify_access_token")
    if (access_token is not None):
        trackInfo = getSpotifyTrackInfo()

        # print("track info: %s" % trackInfo)
        now = round(time.time())
        start = now
        local_start = now - time.timezone

        currentTrackId = None
        if (trackInfo is not None):
            currentTrackId = trackInfo.get("id", None)

        existingTrackId = None
        if (existing_track is not None):
            existingTrackId = existing_track.get("id", None)

        if (existingTrackId is None and currentTrackId is not None):
            # set the existing empty track to the current non-empty track
            existing_track = trackInfo
        elif (existingTrackId is not None and currentTrackId != existingTrackId):
            # a new track, send the existing one
            sendTrackSession = True
        elif (existingTrackId is not None and currentTrackId is None):
            # no track playing but existing one is not empty, send it
            sendTrackSession = True

        # print("sendTrackSession: %s" % sendTrackSession)..........

        resetExistingTrack = False
        # send the song session if we've detected a new track
        if (sendTrackSession == True):
            songSession = existing_track
            songSession["end"] = start
            songSession["local_end"] = local_start
            gatherCodingDataAndSendSongSession(songSession)
            resetExistingTrack = True

        # set the track info to the current track or empty
        if ((resetExistingTrack or existingTrackId is None) and currentTrackId is not None):
            existing_track = trackInfo
            existing_track["start"] = start
            existing_track["local_start"] = local_start
        elif(resetExistingTrack and currentTrackId is None):
            # just reset it to empty
            existing_track = {}

    t = Timer(6, gatherMusicInfo)
    t.start()


def getSpotifyTrackInfo():
    api = "/v1/me/player/currently-playing"
    trackData = requestSpotify("GET", api, None, getItem('spotify_access_token'))

    # print("fetched track: %s" % track)
    track = None
    if trackData is not None and trackData.get("status", 0) == 200:

        track = trackData["item"]
        track["is_playing"] = trackData["is_playing"]
        
        # trackinfo = track.json()['item']['name']
        trackInfoName = trackData["item"]["name"]
        # trackstate = track.json()['is_playing']
        trackState = trackData["is_playing"]
        # track_id = track.json()['item']['id']
        track_id = trackData["item"]["id"]
        current_track_id = track_id
        # print("current_track_id",current_track_id)
        isLiked = check_liked_songs(track_id)
        # print("Liked_songs_ids:",Liked_songs_ids,"\nisLiked:",isLiked)

        # if trackState == True:
        #     print("getSpotifyTrackInfo")
        #     showStatus("Now Playing "+str(trackInfoName) + isLiked)
        #     # print("Playing "+trackinfo)
        # else:
        #     print("getSpotifyTrackInfo")
        #     showStatus("Paused "+str(trackInfoName) + isLiked)
            # print("Paused "+trackinfo)

    elif track is not None and track.get("status", 0) == 401:
        # showStatus("Loading . . . ")
        showStatus("Spotify Connected")
        try:
            refreshSpotifyToken()
            currentTrackInfo()
        except KeyError:
            showStatus("Connect Spotify")

    return track

def gatherCodingDataAndSendSongSession(songSession):

    # print("current track: %s" % songSession)
    payloads = getKpmPayloads()
    aggregatedSource = getActiveData()
    if (aggregatedSource is None):
        aggregatedSource = {}

    # print("current aggregated source: %s" % aggregatedSource)

    if (payloads is not None and len(payloads) > 0):
        for i in range(len(payloads)):
            minutePayload = payloads[i]
            if (minutePayload is not None and minutePayload.get("source", None) is not None):
                # get the payload's source then check if it's start/end is in range
                source = minutePayload["source"]
                if (source is not None):
                    for key, fileInfo in source.items():
                        # check if the payload is in the song session range
                        if (kpmPayloadMatchesSongTimeRange(songSession, fileInfo)):
                            try:
                                if (aggregatedSource.get(key, None) is None):
                                    aggregatedSource[key] = fileInfo
                            except Exception as e:
                                print("aggregatedSource Error\n",e)
                            else:
                                aggregatedSource['paste'] += fileInfo.get("paste", 0)
                                aggregatedSource['open'] += fileInfo.get("open", 0)
                                aggregatedSource['close'] += fileInfo.get("close", 0)
                                aggregatedSource['delete'] += fileInfo.get("delete", 0)
                                aggregatedSource['netkeys'] += fileInfo.get("netkeys", 0)
                                aggregatedSource['add'] += fileInfo.get("add", 0)
                                aggregatedSource['linesAdded'] += fileInfo.get("linesAdded", 0)
                                aggregatedSource['linesRemoved'] += fileInfo.get("linesRemoved", 0)
    
    # print("aggregated source: %s" % aggregatedSource)
    songSession["source"] = aggregatedSource
    # Serialize obj to a JSON formatted str
    songSession = json.dumps(songSession)
    print("songSession\n$$$$$$$$$$$$$$$$",songSession,"\n$$$$$$$$$$$$$$$$$")
    # requestIt("POST", "/data/music", songSession, getItem("jwt"))
    sendPayload = requestIt("POST", "/music/session", songSession, getItem("jwt"))
    if sendPayload["statusCode"] == 200:
        with open(getMusicDataFile(),'w'):
            pass
        #   print("Cleared the musicData.json")
        # os.remove(getMusicDataFile())

def kpmPayloadMatchesSongTimeRange(track, payload):
    if (payload["start"] < track["start"] and payload["end"] < track["start"]):
        return False

    if (payload["start"] > track["end"]):
        return False

    return True


def batchSendPayloadData(api, file, payloads):
    if (payloads is not None and len(payloads) > 0):

        # go through the payloads array 50 at a time
        batch = []
        length = len(payloads)
        for i in range(length):
            payload = payloads[i]
            if (len(batch) >= 50):
                requestIt("POST", "/data/batch", json.dumps(batch), getItem("jwt"))
                # send batch
                batch = []
            batch.append(payload)

        # send remaining batch
        if (len(batch) > 0):
            requestIt("POST", "/data/batch", json.dumps(batch), getItem("jwt"))
        
        os.remove(file)



# Fetch Active device  and Devices(all device including inactive devices)
def getActiveDeviceInfo():
    # print("{}".format(getItem('spotify_access_token')))
    global DEVICES
    # global playlist_id
    # global current_song

    api = "/v1/me/player/devices"
    getdevs = requestSpotify("GET", api, None, getItem('spotify_access_token'))

    if getdevs["status"] == 200:

        # devices = getdevs.json()
        devices = getdevs
        DEVICES = []
        # try:
        if devices['devices'] == []:# and userTypeInfo() == "premium":
            # msg = sublime.ok_cancel_dialog("Please select Spotify player or use 'Alt+Ctrl+D' to switch the device", "Ok")
            # if msg is True:
            #     current_window = sublime.active_window()
            #     current_window.run_command("select_player")
            print("Devices Not found")
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
    elif getdevs["status"] == 401:
        refreshSpotifyToken()



# Function to check whether current track is liked or not.
check_liked_songs = lambda x :"  ❤️" if (x in Liked_songs_ids) else " "
# ❤️ https://emojipedia.org/red-heart/
# ♥️ https://emojipedia.org/heart-suit/


def getLikedSongsIds():
    global Liked_songs_ids

    api = "/v1/me/tracks"
    tracklist = requestSpotify("GET", api, None, getItem('spotify_access_token'))
    if tracklist["status"] == 200:
        # track_list = tracklist.json()
        ids = []
        names = []
        tracks = {}
        for i in tracklist['items']:
            ids.append(i['track']['id'])
            # names.append(i['track']['name'])
            # tracks = tuple(zip(names, ids))
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
    try:
        Liked_songs_ids = getLikedSongsIds()
    except Exception as e:
        print("Liked_songs_ids error",e)
        # Liked_songs_ids =[]
    

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
            # showStatus("Connect Premium")

    else:
        try:
            # print("ACTIVE_DEVICE in currentTrackInfo 1:",ACTIVE_DEVICE)
            if ACTIVE_DEVICE == {}:
                getActiveDeviceInfo()

            # api = "/v1/me/player/currently-playing?" + ACTIVE_DEVICE.get('device_id')
            api = "/v1/me/player/currently-playing"
            # method, api, payload, access token, tries, allowRetry
            track = requestSpotify("GET", api, None, getItem('spotify_access_token'), 0, False)

            if track is not None and track["status"] == 200:
                # trackinfo = track.json()['item']['name']
                trackInfo = track["item"]["name"]
                trackState = track["is_playing"]
                track_id = track["item"]["id"]
                current_track_id = track_id
                # print("current_track_id",current_track_id)
                isLiked = check_liked_songs(track_id)
                # print("Liked_songs_ids:",Liked_songs_ids,"\nisLiked:",isLiked) 

                if trackState == True:
                    showStatus("Now Playing "+str(trackInfo) + isLiked)
                    # print("Playing "+trackinfo)
                else:
                    showStatus("Paused "+str(trackInfo) + isLiked)
                    # print("Paused "+trackinfo)

            elif track["status"] == 401:
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
            print('Music Time: currentTrackInfo ConnectionError\n',ex)
            showStatus("Spotify Connected")
            time.sleep(5)
            # current_window = sublime.active_window()
            # current_window.run_command("select_player")
            pass

    refreshStatusBar()


# Continuous refresh statusbar
def refreshStatusBar():
    try:
        t = Timer(10, currentTrackInfo)
        t.start()
        logged_on = getValue("logged_on", True)
        if logged_on is False:
            t.cancel()
            showStatus("Connect Spotify")
        # schedule.every(5).seconds.do(currentTrackInfo())
        # while True:
        #     schedule.run_pending()
    except Exception as E:
        print("Music Time: refreshStatusBar", E)
        # showStatus("No device found . . . ")
        showStatus("Connect Spotify")
        pass


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


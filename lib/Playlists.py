import sublime_plugin
import sublime
from threading import Thread, Timer, Event
from .SoftwareUtil import *
from .SoftwareHttp import *
import requests
# from .schedule import *


ACTIVE_DEVICE = {'id':"","name":""}
DEVICES = []


# mock data
data = [
    {"id": 1, "name": "Running", "songs": ["Diane Young", "Ottoman", "This Life"]},
    {"id": 2, "name": "Working", "songs": ["How Long", "Jerusalem, New York, Berlin", "Harmony Hall"]},
    {"id": 3, "name": "Fun", "songs": ["A-Punk", "Step", "Sunflower"]}
]

'''
 * Spotify Error Cases
 * When performing an action that is restricted,
 * 404 NOT FOUND (NO_ACTIVE_DEVICE)
 * 403 FORBIDDEN will be returned together with a player error message.(non-premium)
'''

# global variables
current_playlist_name = "Running"
current_song = "Diane Young"

class OpenPlaylistsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        infoMsg = "Playlists opened"
        print(infoMsg)
        return PlaylistInputHandler()

    def run(self, edit, playlists_tree):
        self.view.insert(edit, 0, playlists_tree)

class OpenSongsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        return SongInputHandler()

    def run(self, edit, songs_tree):
        self.view.insert(edit, 0, songs_tree)

class PlaylistInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        super(sublime_plugin.ListInputHandler, self).__init__()

    def name(self):
        return "playlists_tree"

    def initial_text(self):
        return None

    def placeholder(self):
        return "Select a playlist"

    def list_items(self):
        return get_playlists()

    def confirm(self, value):
        global current_playlist_name
        current_playlist_name = value
        print(current_playlist_name)

    def next_input(self, args):
        return SongInputHandler()

class SongInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        super(sublime_plugin.ListInputHandler, self).__init__()

    def name(self):
        return "songs_tree"

    def placeholder(self):
        return "Select a song"

    def list_items(self):
        global current_playlist_name
        return get_songs_in_playlist(current_playlist_name)

    def confirm(self, value):
        global current_song
        current_song = value
        print(current_song)

def get_playlists():
    global data
    playlists = []
    for playlist in data:
        playlists.append(playlist.get("name"))
    return playlists

def get_songs_in_playlist(playlist_name):
    global data
    for playlist in data:
        if playlist.get("name")==playlist_name:
            return playlist.get("songs")


class PlaySong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            playsong()
        except Exception as E:
            print("play",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class PauseSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            pausesong()
        except Exception as E:
            print("pause",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class NextSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            nextsong()
        except Exception as E:
            print("next",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class PrevSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            prevsong()
        except Exception as E:
            print("prev",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

        
class OpenSpotify(sublime_plugin.TextCommand):
    def run(self, edit):
        if isMac() == True:
            os.system("open -a spotify")
        else:
            webbrowser.open("https://open.spotify.com/")


def playsong():
    getActivedevice()
    # print("isMac",isMac(),'|',UserInfo())
    if isMac() == True and UserInfo() == "non-premium": 
        playPlayer()
        currenttrackinfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        # print("headers",headers)
        # print(getActivedevice())
        playstr = "https://api.spotify.com/v1/me/player/play?" + ACTIVE_DEVICE.get('device_id')#getActivedevice()#currentDeviceId
        plays = requests.put(playstr, headers=headers)
        # print(plays.status_code)
        print("Web player Working | Playing :", plays.status_code, "|",plays.text)
        currenttrackinfo()


def pausesong():
    getActivedevice()
    # print("isMac",isMac(),'|',UserInfo())
    if isMac() == True and UserInfo() == "non-premium":
        print(isMac())
        pausePlayer()
        currenttrackinfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        pausestr = "https://api.spotify.com/v1/me/player/pause?" + ACTIVE_DEVICE.get('device_id')#getActivedevice()#currentDeviceId
        pause = requests.put(pausestr, headers=headers)
        print("Web player Working | Paused ...", pause.status_code, "|",pause.text)
        currenttrackinfo()


def nextsong():
    getActivedevice()
    # print("isMac",isMac(),'|',UserInfo())
    if isMac() == True and UserInfo() == "non-premium":
        nextTrack()
        currenttrackinfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        nxtstr = "https://api.spotify.com/v1/me/player/next?" + ACTIVE_DEVICE.get('device_id')#getActivedevice()#currentDeviceId
        nxt = requests.post(nxtstr, headers=headers)
        print("Web player Working | Next ...", nxt.status_code, "|",nxt.text)
        currenttrackinfo()


def prevsong():
    getActivedevice()
    # print("isMac",isMac(),'|',UserInfo())
    if isMac() == True and UserInfo() == "non-premium":
        previousTrack()
        currenttrackinfo()
        print("desktop player Working")
    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        prevstr = "https://api.spotify.com/v1/me/player/previous?" + ACTIVE_DEVICE.get('device_id')#getActivedevice()#currentDeviceId
        prev = requests.post(prevstr, headers=headers)
        print("Web player Working | previous ...", prev.status_code, "|",prev.text)
        # showStatus("▶️ "+currenttrackinfo()[0])# if currenttrackinfo()[1] is True else print("Paused",currenttrackinfo()[0])
        currenttrackinfo()


def startPlayer():
    args = "open -a Spotify"
    os.system(args)


def playPlayer():
    play = '''
    osascript -e 'tell application "Spotify" to play'
    '''
    os.system(play)


def pausePlayer():
    pause = '''
    osascript -e 'tell application "Spotify" to pause'  
    '''
    os.system(pause)
    # args = { "osascript", "-e", "tell application \""+ playerName + "\" to pause" }
    # return runCommand(args, None)


def previousTrack():
    prev = '''
    osascript -e 'tell application "Spotify" to play (previous track)'
    ''' 
    os.system(prev)


def nextTrack():
    nxt = '''
    osascript -e 'tell application "Spotify" to play (next track)'
    '''
    os.system(nxt)

def getActivedevice():
    # print("{}".format(getItem('spotify_access_token')))
    # global currentDeviceId
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    getdevs = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
    
    devices = getdevs.json()
    #print(devices)
    try:
        if devices['devices'] == [] and UserInfo() == "premium":
            webbrowser.open("https://open.spotify.com/")
            print("Music Time: No active device")
        else:
            for i in devices:
                for j in range(len(devices['devices'])):
                    DEVICES = []
                    #get devices name list to display in tree view
                    DEVICES.append(devices['devices'][j]['name'])    
                
                    if devices['devices'][j]['is_active'] == True:
                        ACTIVE_DEVICE['device_id'] = devices['devices'][j]['id']
                        ACTIVE_DEVICE['name'] = devices['devices'][j]['name']
                        print("Music Time: Active device found > ",ACTIVE_DEVICE['name'])
        
            DEVICES.append(devices['devices'][j]['name'])
            print("Music Time: Number of connected devices: ",len(DEVICES))
            # print("ACTIVE_DEVICE",ACTIVE_DEVICE)
                    
    except Exception as E:
        print("Music Time: getActivedevice" ,E)

    refreshdevicestatus()
    '''
    try:
        if getdevs.status_code == 401:
            Refreshspotifytoken()
            getActivedevice()
        else:
            devs = getdevs.json()
            devices = []
            # device_id =''
            if devs['devices'] == []:
                # sublime.yes_no_cancel_dialog('open spotify player ', 'Yeah, Ok!', 'No way!')
                webbrowser.open("https://open.spotify.com/")

                # time.sleep(5)
                getdevs = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
                print("Music Time: Opening Spotify player ...")
                devs = getdevs.json()
                for i in devs:
                    for j in range(len(devs['devices'])):
        #                 if devs['devices'][0]['is_active'] == True:
                            currentDeviceId = devs['devices'][0]['id']
                            print("1st condition")
                            return currentDeviceId  
            else:
            # elif devs['devices'] != []:
                for i in devs:
                    for j in range(len(devs['devices'])):
                        if devs['devices'][j]['is_active'] == True:
                            currentDeviceId = devs['devices'][j]['id']
                            print("2nd condition ")
                            return currentDeviceId
                
                        else:
                            currentDeviceId = devs['devices'][0]['id']
                            print("no active devices")
                            # webbrowser.open("https://open.spotify.com/")
                            # break
                            return currentDeviceId
    except Exception as e:
        print(getActivedevice,e)
        showStatus("Connect Spotify")
        pass
    '''


def currenttrackinfo():
    trackstate = ''
    trackinfo =''
    # try:
    if isMac() == True and UserInfo() == "non-premium":
        '''For MAC user get info from desktop player'''
        # startPlayer()
        try:
            trackstate = getSpotifyTrackState()
            trackinfo = getTrackInfo()["name"]
        # getTrackInfo {'duration': '268210', 'state': 'playing', 'name': 'Dhaga Dhaga', \
        #'artist': 'harsh wavre', 'genre': '', 'type': 'spotify', 'id': 'spotify:track:79TKZDxCWEonklGmC5WbDC'}
            if trackstate == "playing":
                showStatus("Playing ▶️ "+str(trackinfo))
                print("Playing "+trackinfo)
            else:
                showStatus("Paused ⏸️ "+str(trackinfo))
                print("Paused "+trackinfo)
        except Exception as e:
            print("Music time: player not found")
            showStatus("Connect Premium")

        # print("BEFORE",currenttrackinfo)
        # refreshstatusbar()
        # print("After",currenttrackinfo)

    else:
        try:
            headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
            trackstr = "https://api.spotify.com/v1/me/player/currently-playing?" + ACTIVE_DEVICE.get('device_id')#getActivedevice()
            track = requests.get(trackstr, headers=headers)

        # track = requests.get(trackstr, headers=headers)
        

            if track.status_code == 200:
                trackinfo = track.json()['item']['name']
                trackstate = track.json()['is_playing']
                # print(trackinfo,"|",trackstate)
                if trackstate == True:
                    showStatus("Playing ▶️ "+str(trackinfo))
                    print("Playing "+trackinfo)
                else:
                    showStatus("Paused ⏸️ "+str(trackinfo))
                    print("Paused "+trackinfo)

            # elif track.status_code == 204:
            #     headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
            #     trackstr = "https://api.spotify.com/v1/me/player/recently-played?" + getActivedevice()
            #     track = requests.get(trackstr, headers=headers)
            #     trackinfo = track.json()['item']['name']
            #     trackstate = track.json()['is_playing']

            #     if trackstate is True:
            #         showStatus("Playing ▶️"+str(trackinfo))
            #         print("Playing "+trackinfo)
            #     else:
            #         showStatus("Paused ⏸️ "+str(trackinfo))
            #         print("Paused "+trackinfo)
            else:
                # showStatus("Loading . . . ")
                showStatus("No Active device found. Please open Spotify player and play the music ")
                try:
                    Refreshspotifytoken()
                    currenttrackinfo()
                except KeyError:
                    showStatus("Connect Spotify")

        except Exception as e:
            print('Music Time: currenttrackinfo',e)
            showStatus("No Active device found. Please open Spotify player and play the music ")
            pass
    refreshstatusbar()
    # except Exception as E:
    #     print('currenttrackinfo',E)
    #     pass
        
    # return trackinfo,trackstate
    

        # print("BEFORE",currenttrackinfo)
        # refreshstatusbar(5)
        # print("After",currenttrackinfo)

    # except Exception as e:
    #     print("currenttrackinfo didn't work",e)

    # refreshstatusbar(5)
        # try:
        #     updatestatusbar = Timer(20, currenttrackinfo())
        #     updatestatusbar.start()
        # except Exception as e:
        #     print("timer",e)
def refreshstatusbar():

    try:
        t = Timer(30, currenttrackinfo)
        t.start()
        # schedule.every(5).seconds.do(currenttrackinfo())
        # while True:
        #     schedule.run_pending()
    except Exception as E:
        print("Music Time: refreshstatusbar",E)
        showStatus("No device found . . . ")
        # showStatus("Connect Spotify")
        pass


def refreshdevicestatus():

    try:
        t = Timer(60, getActivedevice)
        t.start()
        # schedule.every(5).seconds.do(currenttrackinfo())
        # while True:
        #     schedule.run_pending()
    except Exception as E:
        print("Music Time: refreshstatusbar",E)
        showStatus("No device found . . . ")
        # showStatus("Connect Spotify")
        pass

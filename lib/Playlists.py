import sublime_plugin
import sublime
from threading import Thread, Timer, Event
from .SoftwareUtil import *
from .SoftwareHttp import *
import requests

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
        # pass

    # def is_enabled(self):
    #     pass

class PauseSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            pausesong()
        except Exception as E:
            print("pause",E)
        pass

    # def is_enabled(self):
    #     pass

class NextSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            nextsong()
        except Exception as E:
            print("next",E)
        pass

    # def is_enabled(self):
    #     pass

class PrevSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            prevsong()
        except Exception as E:
            print("prev",E)
        pass

    # def is_enabled(self):
    #     pass
class OpenSpotify(sublime_plugin.TextCommand):
    def run(self, edit):
        webbrowser.open("https://open.spotify.com/")
        pass


def playsong():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    # print("headers",headers)
    print(getActivedevice())
    playstr = "https://api.spotify.com/v1/me/player/play?" + getActivedevice()#currentDeviceId
    plays = requests.put(playstr, headers=headers)
    # print(plays.status_code)
    print("Playing :", plays.status_code, "|",plays.text)
    currenttrackinfo()
    # showStatus("▶️ "+(currenttrackinfo()[0]))# if currenttrackinfo()[1] is True else print("Paused",currenttrackinfo()[0]))
    # showStatus(song)

def pausesong():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    pausestr = "https://api.spotify.com/v1/me/player/pause?" + getActivedevice()#currentDeviceId
    pause = requests.put(pausestr, headers=headers)
    print("Paused ...", pause.status_code, "|",pause.text)
    currenttrackinfo()
    # showStatus("|| "+(currenttrackinfo()[0]))# if currenttrackinfo()[1] is True else print("Paused",currenttrackinfo()[0]))
    # showStatus(song)

def nextsong():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    nxtstr = "https://api.spotify.com/v1/me/player/next?" + getActivedevice()#currentDeviceId
    nxt = requests.post(nxtstr, headers=headers)
    print(" next ...", nxt.status_code, "|",nxt.text)
    currenttrackinfo()
    # showStatus("▶️ "+(currenttrackinfo()[0]))# if currenttrackinfo()[1] is True else print("Paused",currenttrackinfo()[0]))
    # showStatus(song)

def prevsong():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    prevstr = "https://api.spotify.com/v1/me/player/previous?" + getActivedevice()#currentDeviceId
    prev = requests.post(prevstr, headers=headers)
    print(" previous ...", prev.status_code, "|",prev.text)
    # showStatus("▶️ "+currenttrackinfo()[0])# if currenttrackinfo()[1] is True else print("Paused",currenttrackinfo()[0])
    currenttrackinfo()
    # showStatus(song)

def getActivedevice():
    print("{}".format(getItem('spotify_access_token')))
    global currentDeviceId
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    getdevs = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
    if getdevs.status_code == 401:
        Refreshspotifytoken()
        getActivedevice()
    else:
        devs = getdevs.json()
        devices = []
        device_id =''
        if devs['devices'] == []:
            webbrowser.open("https://open.spotify.com/")
            time.sleep(5)
            getdevs = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
            print("idfogio")
            devs = getdevs.json()
            for i in devs:
                for j in range(len(devs['devices'])):
    #                 if devs['devices'][0]['is_active'] == True:
                        currentDeviceId = devs['devices'][0]['id']
                        print("1")
                        return currentDeviceId  
        
        elif devs['devices'] != []:
            for i in devs:
                for j in range(len(devs['devices'])):
                    if devs['devices'][j]['is_active'] == True:
                        currentDeviceId = devs['devices'][j]['id']
                        print("2")
                        return currentDeviceId
            
        else:
            for i in devs:
                for j in range(len(devs['devices'])):
    #                 if devs['devices'][0]['is_active'] == True:
                    currentDeviceId = devs['devices'][0]['id']
                    print("3")
                    return currentDeviceId
                    pass


def currenttrackinfo():
    while True:
        try:
            headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
            trackstr = "https://api.spotify.com/v1/me/player/currently-playing?" + getActivedevice()
            track = requests.get(trackstr, headers=headers)
            

            if track.status_code == 200:
                trackinfo = track.json()['item']['name']
                trackstate = track.json()['is_playing']
                # print(trackinfo,"|",trackstate)
                if trackstate is True:
                    showStatus("Playing "+str(trackinfo))
                    print("Playing "+trackinfo)
                else:
                    showStatus("Paused "+str(trackinfo))
                    print("Paused "+trackinfo)

            elif track.status_code == 204:
                headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
                trackstr = "https://api.spotify.com/v1/me/player/recently-played?" + getActivedevice()
                track = requests.get(trackstr, headers=headers)
                trackinfo = track.json()['item']['name']
                trackstate = track.json()['is_playing']

                if trackstate is True:
                    showStatus("Playing "+str(trackinfo))
                    print("Playing "+trackinfo)
                else:
                    showStatus("Paused "+str(trackinfo))
                    print("Paused "+trackinfo)
            else:
                showStatus("Loading . . . ")
                Refreshspotifytoken()
                currenttrackinfo()

            return trackinfo,trackstate
            # schedule.every(5).seconds.do(currenttrackinfo)
            
            # while True:
            #     schedule.run_pending()
        except Exception as e:
            print("currenttrackinfo",e)
        try:
            updatestatusbar = Timer(20, currenttrackinfo())
            updatestatusbar.start()
        except Exception as e:
            print("timer",e)



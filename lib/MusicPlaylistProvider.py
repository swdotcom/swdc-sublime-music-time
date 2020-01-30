'''
 MusicPlaylistProvider.py will have all of the code to set up,
 refresh the UI, manage actions like getting, adding tracks to,
 and creating playlists.
'''
import requests
import sublime
import sublime_plugin
from threading import Thread, Timer, Event
import webbrowser

from .SoftwareUtil import *
from .SoftwareHttp import *
from ..Software import *
from .SoftwareMusic import *
# from .MusicCommandManager import *
from .MusicControlManager import *


# global variables
current_playlist_name = "Running"
current_song = "Diane Young"

SOFTWARE_API = "https://api.software.com"
SPOTIFY_API = "https://api.spotify.com"

# ACTIVE_DEVICE = {}
# DEVICES = []

playlist_info = {}
playlist_id = ''
# data = []
playlist_data = []
user_id = ""


class OpenPlaylistsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        infoMsg = "Music Time: Playlists opened"
        print(infoMsg)
        return PlaylistInputHandler()

    def run(self, edit, playlists_tree):
        self.view.insert(edit, 0, playlists_tree)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class OpenSongsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        return SongInputHandler()

    def run(self, edit, songs_tree):
        self.view.insert(edit, 0, songs_tree)

        # if len(ACTIVE_DEVICE.values()) != 0:
        #     url = "https://open.spotify.com/album/"+playlist_id+"?highlight=spotify:track:"+songs_tree
        #     webbrowser.open(url)
        getActiveDeviceInfo()
        
        if playlist_id == None:
            playThisSong(ACTIVE_DEVICE.get('device_id'), songs_tree)
        else:
            playSongFromPlaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,songs_tree)
        # print("+"*20,songs_tree)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


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
        return getPlaylists()

    def confirm(self, value):
        global current_playlist_name
        global playlist_id
        current_playlist_name = value
        playlist_id = playlist_info.get(current_playlist_name)
        print("current_playlist_name:",current_playlist_name,"\nPlaylist_id",playlist_id)

    def next_input(self, args):
        return SongInputHandler()

class SongInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        super(sublime_plugin.ListInputHandler, self).__init__()

    def name(self):
        # print(SongInputHandler.name(self))
        return "songs_tree"

    def placeholder(self):
        return "Select a song"

    def list_items(self):
        global current_playlist_name
        return getSongsInPlaylist(current_playlist_name)

    def confirm(self, value):
        global current_song
        current_song = value
        print(current_song)
        # if len(ACTIVE_DEVICE.values()) != 0:
        #     url = "https://open.spotify.com/album/"+playlist_id+"?highlight=spotify:track:"+songs_tree
        #     webbrowser.open(url)

        getActiveDeviceInfo()
        if playlist_id == None:
            print('#'*10,'playlist_id == None SongInputHandler')
            playThisSong(ACTIVE_DEVICE.get('device_id'), current_song)
        else:
            print('#'*10,'else == None SongInputHandler')
            playSongFromPlaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,current_song)
        # print("="*20,current_song)


def getPlaylists():
    playlists = []
    for playlist in playlist_data:
        playlists.append(playlist.get("name"))
    print('playlists',playlists)
    return playlists

def getSongsInPlaylist(playlist_name):
    global playlist_data
    for playlist in playlist_data:
        if playlist.get("name")==playlist_name:
            return playlist.get("songs")

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
            data["context_uri"] = "spotify:playlist:" + playlist_id
            data['offset'] =  {"uri": "spotify:track:" + track_id}
            payload = json.dumps(data)
            print(playSongFromPlaylist,payload)
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playSongFromPlaylist",e)
    currentTrackInfo()

# fetch liked songs tracks
def getLikedSongs():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/me/tracks"
    tracklist =requests.get(playlist_track,headers=headers )
    if tracklist.status_code == 200:
        track_list = tracklist.json()
        ids = []
        names = []
        tracks = {}
        for i in track_list['items']:
            ids.append(i['track']['id'])
            names.append(i['track']['name'])
            tracks = tuple(zip(names,ids))
    else:
        tracks = list('No song found',)
#             tracks = dict(zip(names,ids))
    return list(tracks)


#GET playlist name and ids ro view
def getUserPlaylistInfo(user_id):
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/users/"+user_id+"/playlists"
    playlist =requests.get(playlist_track,headers=headers )
    try:    
        if playlist.status_code == 200:
            playlistname = playlist.json()
            names = []
            ids = []
            playlist=[]
            for i in playlistname['items']:
                names.append(i['name'])
                ids.append(i['id'])
                playlist=dict(zip(names,ids))
    except Exception as e:
        print("getUserPlaylistInfo err",e)
        
    return playlist


# get tracks data using playlist id
def getTracks(playlist_id):
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/playlists/" + playlist_id + "/tracks"
    tracklist =requests.get(playlist_track,headers=headers )
    if tracklist.status_code == 200:
        track_list = tracklist.json()
        ids = []
        names = []
        tracks = {}
        for i in track_list['items']:
            ids.append(i['track']['id'])
            names.append(i['track']['name'])
            tracks = tuple(zip(names,ids))
    else:
        tracks = list('No song found',"")

    return list(tracks)


# Populate playlist data include playlists name/ids and tracks name/ids
def getSortedUserPlaylists():
    # global playlist_info
    user_id = userMeInfo().get('id')
    print("user_id: ",user_id)
    global playlist_data
    playlist_data = []
    '''
    playlist data should be in this form
    data = [{"id": 1, "name": "Running", "songs": [('Tokyo Drifting (with Denzel Curry)', '3AHqaOkEFKZ6zEHdiplIv7'),
                                               ('Alan Silvestri', '0pHcFONMGTN8g18jbz6lJu')]}]
    '''
    try:
        playlist_info = getUserPlaylistInfo(user_id)
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror",e)

    sorted_playlist = dict(sorted(playlist_info.items(), key=lambda playlist_info: playlist_info[0]))
    # print(sorted_playlist)


    for k,v in sorted_playlist.items():
      playlist_data.append({'id':v, 'name':k ,'songs':getTracks(v)})
    playlist_data.append({'id':'000','name':'Liked songs', 'songs':getLikedSongs()})
    print("GOT playlist data :\n",playlist_data)


# Populate playlist data include playlists name/ids and tracks name/ids
def getUserPlaylists():
    global playlist_info
    user_id = userMeInfo().get('id')
    print("user_id: ",user_id)
    global playlist_data
    playlist_data = []
    '''
    playlist data should be in this form
    data = [{"id": 1, "name": "Running", "songs": [('Tokyo Drifting (with Denzel Curry)', '3AHqaOkEFKZ6zEHdiplIv7'),
                                               ('Alan Silvestri', '0pHcFONMGTN8g18jbz6lJu')]}]
    '''
    try:
        playlist_info = getUserPlaylistInfo(user_id)
        print("List of Playlists: ",playlist_info)
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror",e)
    for k,v in playlist_info.items():
      playlist_data.append({'id':v, 'name':k ,'songs':getTracks(v)})
    playlist_data.append({'id':'000','name':'Liked songs', 'songs':getLikedSongs()})
    print("GOT playlist data :\n",playlist_data)



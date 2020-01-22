
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
# from .MusicControlManager import *


# global variables
current_playlist_name = "Running"
current_song = "Diane Young"

SOFTWARE_API = "https://api.software.com"
SPOTIFY_API = "https://api.spotify.com"

# ACTIVE_DEVICE = {}
# DEVICES = []

playlist_info ={}
playlist_id = ''
# data = []
playlist_data = []
user_id = ""

# Lambda function for checking user
check_user = lambda : "Spotify Connected" if (userTypeInfo() == "premium") else ("Connect Premium" if (userTypeInfo() == "open") else "Connect Spotify")



# class OpenPlaylistsCommand(sublime_plugin.TextCommand):
#     def input(self, args):
#         infoMsg = "Music Time: Playlists opened"
#         print(infoMsg)
#         return PlaylistInputHandler()

#     def run(self, edit, playlists_tree):
#         self.view.insert(edit, 0, playlists_tree)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# class OpenSongsCommand(sublime_plugin.TextCommand):
#     def input(self, args):
#         return SongInputHandler()

#     def run(self, edit, songs_tree):
#         self.view.insert(edit, 0, songs_tree)
#         if playlist_id == None:
#             playThisSong(ACTIVE_DEVICE.get('device_id'), songs_tree)
#         else:
#             playSongFromPlaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,songs_tree)
#         print("+"*20,songs_tree)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# class PlaylistInputHandler(sublime_plugin.ListInputHandler):
#     def __init__(self):
#         super(sublime_plugin.ListInputHandler, self).__init__()

#     def name(self):
#         return "playlists_tree"

#     def initial_text(self):
#         return None

#     def placeholder(self):
#         return "Select a playlist"

#     def list_items(self):
#         return getPlaylists()

#     def confirm(self, value):
#         global current_playlist_name
#         global playlist_id
#         current_playlist_name = value
#         playlist_id = playlist_info.get(current_playlist_name)
#         print("current_playlist_name:",current_playlist_name,"\nPlaylist_id",playlist_id)

#     def next_input(self, args):
#         return SongInputHandler()

# class SongInputHandler(sublime_plugin.ListInputHandler):
#     def __init__(self):
#         super(sublime_plugin.ListInputHandler, self).__init__()

#     def name(self):
#         # print(SongInputHandler.name(self))
#         return "songs_tree"

#     def placeholder(self):
#         return "Select a song"

#     def list_items(self):
#         global current_playlist_name
#         return getSongsInPlaylist(current_playlist_name)

#     def confirm(self, value):
#         global current_song
#         current_song = value
#         print(current_song)
#         if playlist_id == None:
#             print('#'*10,'playlist_id == None SongInputHandler')
#             playThisSong(ACTIVE_DEVICE.get('device_id'), current_song)
#         else:
#             print('#'*10,'else == None SongInputHandler')
#             playSongFromPlaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,current_song)
#         print("="*20,current_song)


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
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror",e)

    sorted_playlist = dict(sorted(playlist_info.items(), key=lambda playlist_info: playlist_info[0]))
    print(sorted_playlist)


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
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror",e)
    for k,v in playlist_info.items():
      playlist_data.append({'id':v, 'name':k ,'songs':getTracks(v)})
    playlist_data.append({'id':'000','name':'Liked songs', 'songs':getLikedSongs()})
    print("GOT playlist data :\n",playlist_data)


# # Play song from playlist without playlist_id
# def playThisSong(currentDeviceId, track_id):
#     if isMac() == True and userTypeInfo() == "non-premium":
#         script = '''
#         osascript -e 'tell application "Spotify" to play track "spotify:track:{}"'
#         '''.format(track_id) 
#         os.system(script)
#         print("Played from desktop")

#     else:    
#         headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#         data = {}
#         try:
#             print("track_id",track_id)
#             data = {"uris":["spotify:track:" + track_id]}
#             payload = json.dumps(data)
#             playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
#             plays = requests.put(playstr, headers=headers, data=payload)
#             print(plays.text)
#         except Exception as e:
#             print("playThisSong",e)
#     currentTrackInfo()


# # Play song from playlist using playlist_id and track_id
# def playSongFromPlaylist(currentDeviceId, playlistid, track_id):
#     global playlist_id
#     playlist_id = playlistid
#     if isMac() == True and userTypeInfo() == "non-premium":
#         script = '''
#         osascript -e 'tell application "Spotify" to play track "spotify:track:{}" in context "spotify:playlist:{}"'
#         '''.format(track_id,playlist_id) 
#         os.system(script)
#         print("Played from desktop")
#         pass

#     else:
#         headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#         playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
#         data = {}
#         try:
#             data["context_uri"] = "spotify:playlist:"+ playlist_id
#             data['offset'] =  {"uri": "spotify:track:"+ track_id}
#             payload = json.dumps(data)
#             plays = requests.put(playstr, headers=headers, data=payload)
#             print(plays.text)
#         except Exception as e:
#             print("playSongFromPlaylist",e)
#     currentTrackInfo()

# # Play control in main menu
# class PlaySong(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             self.view.show_popup(myToolTip())
#             playSong()
#         except Exception as E:
#             print("play",E)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)

# # Pause control in main menu
# class PauseSong(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             # self.view.show_popup(myToolTip())
#             pauseSong()
#         except Exception as E:
#             print("pause",E)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)

# # Next control in main menu
# class NextSong(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             # self.view.show_popup(myToolTip())
#             nextSong()
#         except Exception as E:
#             print("next",E)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)

# # Previous control in main menu
# class PrevSong(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             # self.view.show_popup(myToolTip())
#             previousSong()
#         except Exception as E:
#             print("prev",E)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


def myToolTip():
    header = "<h3>Music Time</h3>"
    # connected = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">{}</a></p>'.format(check_user())
    connected = '<p><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20"><b>{}</b></p>'.format(check_user())
    listen_on = '<p><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20"><b>Listening on </b><i>{}</i></p>'.format(ACTIVE_DEVICE.get('name'))
    available_on = '<p><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20"><b>Available on </b><i>{}</i></p>'.format(','.join(DEVICES))
    # no_device_msg = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">No device found</a></p>'

    if len(ACTIVE_DEVICE.values()) == 0:
        body = "<body>" + header + connected + available_on + "</body>"
    # elif len(DEVICES) == 0:
    #     body = "<body>" + header + connected + no_device_msg + "</body>"
    else:
        body = "<body>" + header + connected + listen_on + "</body>"

    return body

# class ConnectionStatus(sublime_plugin.TextCommand):
#     def run(self, edit):
#         print("ConnectionStatus :",DEVICES) 
#         self.view.show_popup(myToolTip(), max_width=300, max_height=1000)
#     def navigate(self,href):
#         if href == 'show':
#             pass
#         else:
#             pass


# # Refresh playlist option in main menu
# class RefreshPlaylist(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             getUserPlaylists()
#         except Exception as E:
#             print("Music Time: RefreshPlaylist:",E)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# class SortPlaylist(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             getSortedUserPlaylists()
#         except Exception as e:
#             print("Music Time: SortPlaylist",e)

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# # open musictime.txt/html file
# class LaunchMusicTimeMetrics(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             getMusicTimedashboard()
#         except Exception as E:
#             print("LaunchMusicTimeMetrics:",E)
#         pass

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)

# # Launch web dashboard .../music
# class SeeWebAnalytics(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             seeWebAnalytics()
#         except Exception as E:
#             print("SeeWebAnalytics:",E)
#         pass

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# # Generate AI playlist 
# class GenerateAIPlaylist(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             generateAIplaylist()
#         except Exception as E:
#             print("RefreshPlaylist:",E)
#         pass

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)

# # Refresh AI playlist 
# class RefreshAIPlaylist(sublime_plugin.TextCommand):
#     def run(self, edit):
#         try:
#             refreshAIplaylist()
#         except Exception as E:
#             print("RefreshPlaylist:",E)
#         pass

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# # Song's Controls: Play
# def playSong():
#     getActiveDeviceInfo()
#     # print("isMac",isMac(),'|',userTypeInfo())
#     if isMac() == True and userTypeInfo() == "non-premium": 
#         playPlayer()
#         currentTrackInfo()
#         print("desktop player Working")
#     else:
#         headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#         # print("headers",headers)
#         # print(getActiveDeviceInfo())
#         playstr = SPOTIFY_API + "/v1/me/player/play?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()#currentDeviceId
#         plays = requests.put(playstr, headers=headers)
#         # print(plays.status_code)
#         print("Web player Working | Playing :", plays.status_code, "|",plays.text)
#         currentTrackInfo()

# # Song's Controls: Pause
# def pauseSong():
#     getActiveDeviceInfo()
#     # print("isMac",isMac(),'|',userTypeInfo())
#     if isMac() == True and userTypeInfo() == "non-premium":
#         print(isMac())
#         pausePlayer()
#         currentTrackInfo()
#         print("desktop player Working")
#     else:
#         headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#         pausestr = SPOTIFY_API + "/v1/me/player/pause?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()#currentDeviceId
#         pause = requests.put(pausestr, headers=headers)
#         print("Web player Working | Paused ...", pause.status_code, "|",pause.text)
#         currentTrackInfo()

# # Song's Controls: Next
# def nextSong():
#     getActiveDeviceInfo()
#     # print("isMac",isMac(),'|',userTypeInfo())
#     if isMac() == True and userTypeInfo() == "non-premium":
#         nextTrack()
#         currentTrackInfo()
#         print("desktop player Working")
#     else:
#         headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#         nxtstr = SPOTIFY_API + "/v1/me/player/next?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()#currentDeviceId
#         nxt = requests.post(nxtstr, headers=headers)
#         print("Web player Working | Next ...", nxt.status_code, "|",nxt.text)
#         currentTrackInfo()

# # Song's Controls: Previous
# def previousSong():
#     getActiveDeviceInfo()
#     # print("isMac",isMac(),'|',userTypeInfo())
#     if isMac() == True and userTypeInfo() == "non-premium":
#         previousTrack()
#         currentTrackInfo()
#         print("desktop player Working")
#     else:
#         headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#         prevstr = SPOTIFY_API + "/v1/me/player/previous?" + ACTIVE_DEVICE.get('device_id')
#         prev = requests.post(prevstr, headers=headers)
#         print("Web player Working | previous ...", prev.status_code, "|",prev.text)
#         # showStatus("▶️ "+currentTrackInfo()[0])# if currentTrackInfo()[1] is True else print("Paused",currentTrackInfo()[0])
#         currentTrackInfo()

# # Launch Spotify player
# def startPlayer():
#     args = "open -a Spotify"
#     os.system(args)

# # Song's Controls: Play from Desktop
# def playPlayer():
#     play = '''
#     osascript -e 'tell application "Spotify" to play'
#     '''
#     os.system(play)


# # Song's Controls: Pause from Desktop
# def pausePlayer():
#     pause = '''
#     osascript -e 'tell application "Spotify" to pause'  
#     '''
#     os.system(pause)
#     # args = { "osascript", "-e", "tell application \""+ playerName + "\" to pause" }
#     # return runCommand(args, None)

# # Song's Controls: Previous from Desktop
# def previousTrack():
#     prev = '''
#     osascript -e 'tell application "Spotify" to play (previous track)'
#     ''' 
#     os.system(prev)

# # Song's Controls: Next from Desktop
# def nextTrack():
#     nxt = '''
#     osascript -e 'tell application "Spotify" to play (next track)'
#     '''
#     os.system(nxt)

# # Fetch Active device  and Devices(all device including inactive devices)
# def getActiveDeviceInfo():
#     # print("{}".format(getItem('spotify_access_token')))
#     # global currentDeviceId
#     headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#     get_device_url = SPOTIFY_API + "/v1/me/player/devices"
#     getdevs = requests.get(get_device_url, headers=headers)
    
#     devices = getdevs.json()
#     #print(devices)
#     try:
#         if devices['devices'] == [] and userTypeInfo() == "premium":
#             url = "https://open.spotify.com/"
#             webbrowser.open(url)
#             print("Music Time: No active device found. Opening Spotify player")
#         else:
#             for i in devices:
#                 for j in range(len(devices['devices'])):
#                     DEVICES = []
#                     #get devices name list to display in tree view
#                     DEVICES.append(devices['devices'][j]['name'])    
                
#                     if devices['devices'][j]['is_active'] == True:
#                         ACTIVE_DEVICE['device_id'] = devices['devices'][j]['id']
#                         ACTIVE_DEVICE['name'] = devices['devices'][j]['name']
#                         print("Music Time: Active device found > ",ACTIVE_DEVICE['name'])
        
#             DEVICES.append(devices['devices'][j]['name'])
#             print("ACTIVE_DEVICE",ACTIVE_DEVICE)
#             print("DEVICES :",DEVICES)
#             print("Music Time: Number of connected devices: ",len(DEVICES))
#             # print("ACTIVE_DEVICE",ACTIVE_DEVICE)
                    
#     except Exception as E:
#         print("Music Time: getActiveDeviceInfo" ,E)

#     refreshDeviceStatus()
    

# def currentTrackInfo():
#     trackstate = ''
#     trackinfo =''
#     # try:
#     if isMac() == True and userTypeInfo() == "non-premium":
#         '''For MAC user get info from desktop player'''
#         # startPlayer()
#         try:
#             trackstate = getSpotifyTrackState()
#             trackinfo = getTrackInfo()["name"]
#         # getTrackInfo {'duration': '268210', 'state': 'playing', 'name': 'Dhaga Dhaga', \
#         #'artist': 'harsh wavre', 'genre': '', 'type': 'spotify', 'id': 'spotify:track:79TKZDxCWEonklGmC5WbDC'}
#             if trackstate == "playing":
#                 showStatus("Now Playing "+str(trackinfo)+" on "+ ACTIVE_DEVICE.get('name'))
#                 # print("Playing "+trackinfo)
#             else:
#                 showStatus("Paused "+str(trackinfo)+" on "+ ACTIVE_DEVICE.get('name'))
#                 # print("Paused "+trackinfo)
#         except Exception as e:
#             print("Music time: player not found",e)
#             showStatus("Connect Premium")

#         # print("BEFORE",currentTrackInfo)
#         # refreshStatusBar()
#         # print("After",currentTrackInfo)

#     else:
#         try:
#             headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
#             trackstr = SPOTIFY_API + "/v1/me/player/currently-playing?" + ACTIVE_DEVICE.get('device_id')#getActiveDeviceInfo()
#             track = requests.get(trackstr, headers=headers)

#             if track.status_code == 200:
#                 trackinfo = track.json()['item']['name']
#                 trackstate = track.json()['is_playing']
#                 # print(trackinfo,"|",trackstate)
#                 if trackstate == True:
#                     showStatus("Now Playing "+str(trackinfo)+" on "+ACTIVE_DEVICE.get('name'))
#                     # print("Playing "+trackinfo)
#                 else:
#                     showStatus("Paused "+str(trackinfo)+" on "+ACTIVE_DEVICE.get('name'))
#                     # print("Paused "+trackinfo)

#             else:
#                 # showStatus("Loading . . . ")
#                 showStatus("No Active device found. Please open Spotify player and play the music ")
#                 try:
#                     refreshSpotifyToken()
#                     currentTrackInfo()
#                 except KeyError:
#                     showStatus("Connect Spotify")

#         except Exception as e:
#             print('Music Time: currentTrackInfo',e)
#             showStatus("No Active device found. Please open Spotify player and play the music ")
#             pass
#     refreshStatusBar()
    

# # Continuous refresh statusbar
# def refreshStatusBar():
#     try:
#         t = Timer(10, currentTrackInfo) 
#         t.start()
#         # schedule.every(5).seconds.do(currentTrackInfo())
#         # while True:
#         #     schedule.run_pending()
#     except Exception as E:
#         print("Music Time: refreshStatusBar",E)
#         showStatus("No device found . . . ")
#         # showStatus("Connect Spotify")
#         pass

# # Continuous refresh devices
# def refreshDeviceStatus():
#     try:
#         t = Timer(60, getActiveDeviceInfo)
#         t.start()
#         # schedule.every(5).seconds.do(currentTrackInfo())
#         # while True:
#         #     schedule.run_pending()
#     except Exception as E:
#         print("Music Time: refreshStatusBar",E)
#         showStatus("No device found . . . ")
#         # showStatus("Connect Spotify")
#         pass



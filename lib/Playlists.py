import sublime_plugin
import sublime
from threading import Thread, Timer, Event
from .SoftwareUtil import *
from .SoftwareHttp import *
from ..Software import *
import requests
import webbrowser
# from .schedule import *


ACTIVE_DEVICE = {}
DEVICES = []

playlist_info ={}
# user_id = "j1dz6tgj6n8bphkeaafgnjuvs"
# user_id = ""
playlist_id = ''
data = []

# Lambda function for checking user
check_user = lambda : "Spotify Connected" if (UserInfo() == "premium") else ("Connect Premium" if (UserInfo() == "open") else "Connect Spotify")

# global variables
current_playlist_name = "Running"
current_song = "Diane Young"

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
        if playlist_id == None:
            playThissong(ACTIVE_DEVICE.get('device_id'), songs_tree)
        else:
            playSongfromplaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,songs_tree)
        print("+"*20,songs_tree)

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
        return get_playlists()

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
        return get_songs_in_playlist(current_playlist_name)

    def confirm(self, value):
        global current_song
        current_song = value
        print(current_song)
        if playlist_id == None:
            print('#'*10,'playlist_id == None SongInputHandler')
            playThissong(ACTIVE_DEVICE.get('device_id'), current_song)
        else:
            print('#'*10,'else == None SongInputHandler')
            playSongfromplaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,current_song)
        print("="*20,current_song)


def get_playlists():
    playlists = []
    for playlist in data:
        playlists.append(playlist.get("name"))
    print('playlists',playlists)
    return playlists

def get_songs_in_playlist(playlist_name):
    global data
    for playlist in data:
        if playlist.get("name")==playlist_name:
            return playlist.get("songs")

# fetch liked songs tracks
def getlikedsongs():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    playlist_track = "https://api.spotify.com/v1/me/tracks"
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
def getuserPlaylistinfo(user_id):
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    playlist_track = "https://api.spotify.com/v1/users/"+user_id+"/playlists"
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
        print("getuserPlaylistinfo err",e)
        
    return playlist


# get tracks data using playlist id
def gettracks(playlist_id):
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    playlist_track = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
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
    user_id = Userme().get('id')
    print("user_id: ",user_id)
    global data
    data = []
    '''
    playlist data should be in this form
    data = [{"id": 1, "name": "Running", "songs": [('Tokyo Drifting (with Denzel Curry)', '3AHqaOkEFKZ6zEHdiplIv7'),
                                               ('Alan Silvestri', '0pHcFONMGTN8g18jbz6lJu')]}]
    '''
    try:
        playlist_info = getuserPlaylistinfo(user_id)
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror",e)

    sorted_playlist = dict(sorted(playlist_info.items(), key=lambda playlist_info: playlist_info[0]))
    print(sorted_playlist)


    for k,v in sorted_playlist.items():
      data.append({'id':v, 'name':k ,'songs':gettracks(v)})
    data.append({'id':'000','name':'Liked songs', 'songs':getlikedsongs()})
    print("GOT playlist data :\n",data)


# Populate playlist data include playlists name/ids and tracks name/ids
def getUserPlaylists():
    global playlist_info
    user_id = Userme().get('id')
    print("user_id: ",user_id)
    global data
    data = []
    '''
    playlist data should be in this form
    data = [{"id": 1, "name": "Running", "songs": [('Tokyo Drifting (with Denzel Curry)', '3AHqaOkEFKZ6zEHdiplIv7'),
                                               ('Alan Silvestri', '0pHcFONMGTN8g18jbz6lJu')]}]
    '''
    try:
        playlist_info = getuserPlaylistinfo(user_id)
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror",e)
    for k,v in playlist_info.items():
      data.append({'id':v, 'name':k ,'songs':gettracks(v)})
    data.append({'id':'000','name':'Liked songs', 'songs':getlikedsongs()})
    print("GOT playlist data :\n",data)


# Play song from playlist without playlist_id
def playThissong(currentDeviceId, track_id):
    if isMac() == True and UserInfo() == "non-premium":
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
            playstr = "https://api.spotify.com/v1/me/player/play?device_id=" + currentDeviceId
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playThissong",e)


# Play song from playlist using playlist_id and track_id
def playSongfromplaylist(currentDeviceId, playlistid, track_id):
    global playlist_id
    playlist_id = playlistid
    if isMac() == True and UserInfo() == "non-premium":
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}" in context "spotify:playlist:{}"'
        '''.format(track_id,playlist_id) 
        os.system(script)
        print("Played from desktop")
        pass

    else:
        headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
        playstr = "https://api.spotify.com/v1/me/player/play?device_id=" + currentDeviceId
        data = {}
        try:
            data["context_uri"] = "spotify:playlist:"+ playlist_id
            data['offset'] =  {"uri": "spotify:track:"+ track_id}
            payload = json.dumps(data)
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playSongfromplaylist",e)

# Play control in main menu
class PlaySong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            self.view.show_popup(myTooltip())
            playsong()
        except Exception as E:
            print("play",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Pause control in main menu
class PauseSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myTooltip())
            pausesong()
        except Exception as E:
            print("pause",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Next control in main menu
class NextSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myTooltip())
            nextsong()
        except Exception as E:
            print("next",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Previous control in main menu
class PrevSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myTooltip())
            prevsong()
        except Exception as E:
            print("prev",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


def myTooltip():
    global DEVICES
    # print('myTooltip()',ACTIVE_DEVICE)
    # print('myTooltip()',DEVICES)
    header = "<h3>MUSIC TIME</h3>"
    connected = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">{}</a></p>'.format(check_user())
    listen_on = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">Listening on {}</a></p>'.format(ACTIVE_DEVICE.get('name'))
    available_on = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">Available on {}</a></p>'.format(','.join(DEVICES))
    # no_device_msg = '<p><a href="show"><img src="res://Packages/swdc-sublime-music-time/spotify-icons-logos/spotify-icons-logos/icons/01_RGB/02_PNG/Spotify_Icon_RGB_Green.png" height="20" width="20">No device found</a></p>'


    if len(ACTIVE_DEVICE.values()) == 0:
        body = "<body>" + header + connected + available_on + "</body>"
    # elif len(DEVICES) == 0:
    #     body = "<body>" + header + connected + no_device_msg + "</body>"
    else:
        body = "<body>" + header + connected + listen_on + "</body>"

    return body

class ConnectionStatus(sublime_plugin.TextCommand):
    def run(self, edit):
        print("ConnectionStatus :",DEVICES) 
        self.view.show_popup(myTooltip(), max_width=300, max_height=1000)
    def navigate(self,href):
        if href == 'show':
            pass
        else:
            pass

        
# class OpenSpotify(sublime_plugin.TextCommand):
#     def run(self, edit):
#         if isMac() == True:
#             os.system("open -a spotify")
#         else:
#             webbrowser.open("https://open.spotify.com/")

# Refresh playlist option in main menu
class RefreshPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            getUserPlaylists()
        except Exception as E:
            print("Music Time: RefreshPlaylist:",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class SortPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            getSortedUserPlaylists()
        except Exception as e:
            print("Music Time: SortPlaylist",e)
        

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# open musictime.txt/html file
class LaunchMusicTimeMetrics(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            getMusicTimedashboard()
        except Exception as E:
            print("LaunchMusicTimeMetrics:",E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Launch web dashboard .../music
class SeeWebAnalytics(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            musictimedash()
        except Exception as E:
            print("SeeWebAnalytics:",E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# class GenRefresh(sublime_plugin.TextCommand):
#     def run(self, edit):
#         pass

#     def is_enabled(self):
#         return (getValue("logged_on", True) is True)


# Generate AI playlist 
class GenerateAIPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            generateAIplaylist()
        except Exception as E:
            print("RefreshPlaylist:",E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Refresh AI playlist 
class RefreshAIPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            refreshAIplaylist()
        except Exception as E:
            print("RefreshPlaylist:",E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Song's Controls: Play
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

# Song's Controls: Pause
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

# Song's Controls: Next
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

# Song's Controls: Previous
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

# Fetch Active device  and Devices(all device including inactive devices)
def getActivedevice():
    # print("{}".format(getItem('spotify_access_token')))
    # global currentDeviceId
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    getdevs = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
    
    devices = getdevs.json()
    #print(devices)
    try:
        if devices['devices'] == [] and UserInfo() == "premium":
            url = "https://open.spotify.com/"
            webbrowser.open(url)
            print("Music Time: No active device found. Opening Spotify player")
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
            print("ACTIVE_DEVICE",ACTIVE_DEVICE)
            print("DEVICES :",DEVICES)
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

# Continuous refresh statusbar
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

# Continuous refresh devices
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



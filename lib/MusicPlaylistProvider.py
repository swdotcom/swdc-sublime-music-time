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

from ..Constants import *
from .SoftwareUtil import *
from .SoftwareHttp import *
from ..Software import *
from .SoftwareMusic import *
# from .MusicCommandManager import *
from .MusicControlManager import *
from .PlayerManager import *


# global variables
current_playlist_name = ""
current_song = ""  # Current track id

AI_PLAYLIST_ID = ""
AI_PLAYLIST_NAME = "My AI Top 40"

playlist_info = {}
playlist_id = ''

playlist_data = []
spotifyUserId = ""
playlist_names = []

sortby = "time" # or "az"


class OpenPlaylistsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        infoMsg = "Music Time: Playlists opened"
        # print(infoMsg)
        return PlaylistInputHandler()

    def run(self, edit, playlists_tree):
        self.view.insert(edit, 0, playlists_tree)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class OpenSongsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        return SongInputHandler()

    def run(self, edit, songs_tree):
        # print('first',songs_tree)
        self.view.insert(edit, 0, songs_tree)
        # print('second',songs_tree)

        print("current_song",current_song)
        if playlist_id == None:
            # try:
            #     openTrackInWeb(playlist_id, current_song)
            # except Exception as e:
            #     print("OpenSongsCommand:run:openTrackInWeb", e)
            # getActiveDeviceInfo()
            playThisSong(ACTIVE_DEVICE.get('device_id'), songs_tree)
        else:
            # try:
            #     openTrackInWeb(playlist_id, current_song)
            # except Exception as e:
            #     print("OpenSongsCommand:run:openTrackInWeb", e)
            # getActiveDeviceInfo()
            playSongFromPlaylist(ACTIVE_DEVICE.get(
                'device_id'), playlist_id, songs_tree)
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
        print("current_playlist_name:", current_playlist_name,
              "\nPlaylist_id", playlist_id)

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
        print("SongInputHandler:list_items", current_playlist_name)
        if len(current_playlist_name) > 0:
            return getSongsInPlaylist(current_playlist_name)
        else:
            message_dialog = sublime.message_dialog(
                "Songs not found. Please Use \nTools > Music Time > My Playlists > Open Playlist")
            current_window = sublime.active_window()
            current_window.run_command("hide_overlay")
            # print("NO SONG found")

    def confirm(self, value):
        global current_song
        current_song = value
        print("current_song", current_song)

        if playlist_id == None:
            print('#'*10, 'playlist_id == None SongInputHandler')
            # try:
            #     openTrackInWeb(playlist_id, current_song)
            # except Exception as TypeError: #e
            #     print("SongInputHandler:confirm:openTrackInWeb", e)
            #     message_dialog = sublime.message_dialog("Song not found")
            # getActiveDeviceInfo()
            # active_device = getSpotifyActiveDevice()

            # if active_device == {}:
            #     current_window = sublime.active_window()
            #     current_window.run_command("select_player")
            playThisSong(ACTIVE_DEVICE.get('device_id'), current_song)
        else:
            # try:
            #     openTrackInWeb(playlist_id, current_song)
            # except Exception as e:
            #     print("SongInputHandler:confirm:openTrackInWeb", e)
            # active_device = getSpotifyActiveDevice()

            # if active_device == {}:
            #     current_window = sublime.active_window()
            #     current_window.run_command("select_player")
            # getActiveDeviceInfo()
            print('#'*10, 'else == None SongInputHandler')
            playSongFromPlaylist(ACTIVE_DEVICE.get(
                'device_id'), playlist_id, current_song)


def getPlaylists():
    playlists = []
    for playlist in playlist_data:
        playlists.append(playlist.get("name"))
    print('playlists', playlists)
    return playlists


def getSongsInPlaylist(playlist_name):
    global playlist_data
    for playlist in playlist_data:
        if playlist.get("name") == playlist_name:
            return playlist.get("songs")


# Play song from playlist without playlist_id
def playThisSong(currentDeviceId, track_id):
    global ACTIVE_DEVICE

    # print("active_device",active_device)

    # current_window = sublime.active_window()
    # current_window.run_command("select_player")
    if isMac() == True and userTypeInfo() == "non-premium":
        if currentDeviceId is None:
            openDesktopPlayer()

        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}"'
        '''.format(track_id)
        os.system(script)
        print("Played from desktop")

    else:
        headers = {"Authorization": "Bearer {}".format(
            getItem('spotify_access_token'))}
        print(Liked_songs_ids) 
        uris_list = []
        for song_id in Liked_songs_ids:
            uris_list.append("spotify:track:"+song_id)
        print("uris_list",uris_list)

        track_index = uris_list.index("spotify:track:" + track_id)
        print("track_index",track_index)
        '''
        {"uris": ["spotify:track:1rZwgdUwUYBqEphd4CXynL", "spotify:track:6Q8mqjuz8xqdoUjhZQDfY7",
                  "spotify:track:1aDklx1GaBqHFowCzz63wU", "spotify:track:4oaU0fMSg3n9kqOwmLPVhH",
                  "spotify:track:4WZizdGrBVSZCES0q2XDwu", "spotify:track:0l1i3nJ4aDMk0inxnvzYTz"],
                  "offset": {"position": 2}}
        '''
        data = {}
        try:
            print("track_id", track_id)
            # data = {"uris": ["spotify:track:" + track_id]}
            data = { "uris": uris_list, "offset": {"position": track_index} }# {"position": 5}
            payload = json.dumps(data)
            print("payload",payload)
            print("currentDeviceId",currentDeviceId)

            if (currentDeviceId != ''.join([i for i in getSpotifyDevice() if ['device_id'] == currentDeviceId])) or currentDeviceId is None:
                msg = sublime.yes_no_cancel_dialog("Launch a Spotify device", "Web player", "Desktop player")

                if msg is 1:
                    webbrowser.open("https://open.spotify.com/")
                    # time.sleep(5)
                elif msg is 2:
                    launchDesktopPlayer()

                else:
                    current_window = sublime.active_window()
                    current_window.run_command("hide_overlay")

                time.sleep(4)
                device_id = getSpotifyDevice()[0]['device_id']
                transferPlayback(device_id)
                time.sleep(1)
                active_device = getSpotifyActiveDevice()
                print("active_device",active_device)
                ACTIVE_DEVICE['device_id'] = device_id

                playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + active_device.get('device_id')
            elif currentDeviceId is not None and ACTIVE_DEVICE.get('device_id') is None:#getSpotifyActiveDevice().get('device_id') is None:
                transferPlayback(currentDeviceId)
                playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
            else:
                playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
            
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playThisSong", e)
    currentTrackInfo()


# Play song from playlist using playlist_id and track_id
def playSongFromPlaylist(currentDeviceId, playlistid, track_id):
    global ACTIVE_DEVICE
    global playlist_id
    playlist_id = playlistid
    if isMac() == True and userTypeInfo() == "non-premium":
        if currentDeviceId is None:
            openDesktopPlayer()
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}" in context "spotify:playlist:{}"'
        '''.format(track_id, playlist_id)
        os.system(script)
        print("Played from desktop")
        pass

    else:
        headers = {"Authorization": "Bearer {}".format(
            getItem('spotify_access_token'))}

        if (currentDeviceId != ''.join([i for i in getSpotifyDevice() if ['device_id'] == currentDeviceId])) or currentDeviceId is None:
            msg = sublime.yes_no_cancel_dialog("Launch a Spotify device", "Web player", "Desktop player")

            if msg is 1:
                webbrowser.open("https://open.spotify.com/")
            elif msg is 2:
                launchDesktopPlayer()
                # set_timeout_async(launchDesktopPlayer(),4000)
            else:
                current_window = sublime.active_window()
                current_window.run_command("hide_overlay") 
            time.sleep(4)
            print("spotifydevices",getSpotifyDevice())
            device_id = getSpotifyDevice()[0]['device_id']
            transferPlayback(device_id)
            time.sleep(1)
            active_device = getSpotifyActiveDevice()
            print("active_device",active_device)
            ACTIVE_DEVICE['device_id'] = device_id
            
            playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + active_device.get('device_id') #currentDeviceId
        # elif currentDeviceId is not None and ACTIVE_DEVICE.get('device_id') is None:#getSpotifyActiveDevice().get('device_id') is None:
        #     transferPlayback(currentDeviceId)
        #     playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
        else:
            playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
        data = {}
        try:
            data["context_uri"] = "spotify:playlist:" + playlist_id
            data['offset'] = {"uri": "spotify:track:" + track_id}
            payload = json.dumps(data)
            print("playSongFromPlaylist", payload)

            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playSongFromPlaylist", e)
    currentTrackInfo()


# fetch liked songs tracks
def getLikedSongs():
    global Liked_songs_ids
    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/me/tracks"
    tracklist = requests.get(playlist_track, headers=headers)
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
        print("Liked_songs_ids",Liked_songs_ids)
    else:
        tracks = []
#             tracks = dict(zip(names,ids))
    return list(tracks)


# GET playlist name and ids ro view
def getUserPlaylistInfo(spotifyUserId):
    global playlist_names
    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/users/" + spotifyUserId + "/playlists"
    playlist = requests.get(playlist_track, headers=headers)
    try:
        if playlist.status_code == 200:
            playlistname = playlist.json()
            names = []
            ids = []
            playlist = {}
            playlist_names = []
            for i in playlistname['items']:

                names.append(i['name'])
                ids.append(i['id'])
                playlist = dict(zip(names, ids))

        playlist_names = list(names)
        print("In def playlist_names",playlist_names)
    except Exception as e:
        print("getUserPlaylistInfo err", e)

    return playlist


# get tracks data using playlist id
def getTracks(playlist_id):
    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/playlists/" + playlist_id + "/tracks"
    tracklist = requests.get(playlist_track, headers=headers)
    if tracklist.status_code == 200:
        track_list = tracklist.json()
        ids = []
        names = []
        tracks = {}
        for i in track_list['items']:
            ids.append(i['track']['id'])
            names.append(i['track']['name'])
            tracks = tuple(zip(names, ids))
    else:
        tracks = list('No song found', "")

    return list(tracks)


# Populate playlist data include playlists name/ids and tracks name/ids
def getUserPlaylists():
    global playlist_info
    spotifyUserId = userMeInfo().get('id')
    print("spotifyUserId: ", spotifyUserId)
    global playlist_data
    '''
    playlist data should be in this form
    data = [{"id": 1, "name": "Running", "songs": [('Tokyo Drifting (with Denzel Curry)', '3AHqaOkEFKZ6zEHdiplIv7'),
                                               ('Alan Silvestri', '0pHcFONMGTN8g18jbz6lJu')]}]
    '''
    try:
        playlist_info = getUserPlaylistInfo(spotifyUserId)
        print("List of Playlists: ", playlist_info) 
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror", e)

    if sortby == "time":
        # Sort by latest
        # playlist_names = list(playlist_info.keys())
        sortPlaylistByLatest()
        print("sortby:sortPlaylistByLatest:",sortby)

    else:
        # sort by A-Z
        playlist_data = []
        for k, v in playlist_info.items():
            if "Software" in k:
                playlist_data.append({'id': v, 'name': k, 'playlistTypeId': 1 ,'songs': getTracks(v)})
                # print("got software",k," ",v)

            elif v == AI_PLAYLIST_ID or k == AI_PLAYLIST_NAME:
                playlist_data.append({'id': v, 'name': k, 'playlistTypeId': 2 ,'songs': getTracks(v)})
                # print("got AI playlist",k," ",v)

            else:
                playlist_data.append({'id': v, 'name': k, 'playlistTypeId': 4,'songs': getTracks(v)})
                # print("got user playlist",k," ",v)
        
        liked_songs = getLikedSongs()
        if liked_songs != []:
            playlist_data.append({'id': '000', 'name': 'Liked songs', 'playlistTypeId': 3, 'songs': liked_songs})
            print("got liked songs")
        print("No liked songs")
        print("No of playlist :",len(playlist_data))
        try:
            sortPlaylistByAz()
        except Exception as e:
            print("sortPlaylistByAz",e)
        print("sortby:sortPlaylistByAz:",sortby)
    

# Sort by latest code
def sortPlaylistByLatest():
    global playlist_data
    global playlist_names
    global sortby
    sortby = "time"

    print("got inside loop: playlist_names",playlist_names)
    sec_one = [] # Software top 40 and AI playlist

    sec_three = [] # user playlist
    for k in playlist_names:
        if k == "Software Top 40":
            sec_one.append(k)
        elif k == "My AI Top 40":
            sec_one.append(k)
        else:
            sec_three.append(k)

    if len(sec_one) == 2:    
        # Swapping (1)Software top 40 (2)AI playlist
        sec_one[0],sec_one[1] = sec_one[1],sec_one[0]
    
    liked_songs = getLikedSongs()
    if liked_songs != []:
        sec_two = ["Liked songs"] # Liked songs
        # Final list with (1)Software top 40 (2)AI playlist (3)Liked songs (4)user playlist
        final_list = sec_one + sec_two + sec_three
    else:
        final_list = sec_one + sec_three


    playlist_data = []
    for i in final_list:
        
        if i == "Software Top 40":
    #         playlist_data[0] = {'id':playlist_info.get(i),'name':i,'playlistTypeId': 1,'songs': getTracks(playlist_info.get(i))}
            playlist_data.append({'id':playlist_info.get(i),'name':i,'playlistTypeId': 1,'songs': getTracks(playlist_info.get(i))})
        elif i == "My AI Top 40" or i == AI_PLAYLIST_NAME:
    #         playlist_data[1] = {'id':playlist_info.get(i),'name':i,'playlistTypeId': 1,'songs': getTracks(playlist_info.get(i))}
            playlist_data.append({'id':playlist_info.get(i),'name':i,'playlistTypeId': 2,'songs': getTracks(playlist_info.get(i))})
        elif i == "Liked songs":
    #         playlist_data[2] = {'id':playlist_info.get(i),'name':i,'playlistTypeId': 3,'songs': getLikedSongs()}
            playlist_data.append({'id':playlist_info.get(i),'name':i,'playlistTypeId': 3,'songs': liked_songs})
        else:
            playlist_data.append({'id':playlist_info.get(i),'name':i,'playlistTypeId': 4,'songs': getTracks(playlist_info.get(i))})
            
    # final_playlist = sec_one + sec_three
    for k in playlist_data:
        print(k['name'],"|",k['playlistTypeId'])


# Sort by A-Z code
def sortPlaylistByAz():
    global playlist_data
    global sortby
    sortby = "az"

    # section 1 for Software top 40, My AI, Likedsongs
    playlist_section_one = []
    playlist_section_two = []
    for i in playlist_data:
        if i['playlistTypeId'] < 4:
            playlist_section_one.append(i)
        else:
            if i['playlistTypeId'] == 4:
                playlist_section_two.append(i)

    playlist_section_one = sorted(playlist_section_one, key = lambda i: i['playlistTypeId'])

    # sorting by playlist name # c = sorted(s, key=lambda c: (c.lower(), c.islower()))
    playlist_section_two = sorted(playlist_section_two, key = lambda i:(i['name'].lower(),i['name'].islower()))
    # playlist_section_two = sorted(playlist_section_two, key = lambda i: i['name'])

    # Final sorted playlist in A-z
    playlist_data = playlist_section_one + playlist_section_two
    print("sortby",sortby)
    for i in playlist_data:
        print(i['name'],"|",i['playlistTypeId'])
    # print(playlist_data)
    # return AZSortedplaylist


# Check AI playlist exist or not
def checkAIPlaylistid():
    global AI_PLAYLIST_ID
    global AI_PLAYLIST_NAME
    # global playlist_info
    spotifyUserId = userMeInfo().get('id')

    # Check for ai_playlist in software backend
    url = "https://api.software.com" + "/music/playlist/generated"
    # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE0Nzc1LCJpYXQiOjE1NjgwMDg1Mjh9.h-2i2SRK3kWSojBkJ3JXUztWFdErUotAz9wk7JHw1H4"
    jwt = getItem("jwt")
    headers0 = {'content-type': 'application/json', 'Authorization': jwt}
    get_ai_playlistid = requests.get(url, headers=headers0)
    # print("get_ai_playlistid:",get_ai_playlistid.text)
    if get_ai_playlistid.status_code == 200:
        get_ai_playlistid_data = get_ai_playlistid.json()
        print("get_ai_playlistid_data\n", get_ai_playlistid_data)
        if len(get_ai_playlistid_data) > 0:
            backend_ai_playlistid = get_ai_playlistid_data[0]['playlist_id']
            print("backend_ai_playlistid : ",backend_ai_playlistid)

            playlist_info = {}
            playlist_info = getUserPlaylistInfo(spotifyUserId)
            print("checkAIPlaylistid >> playlist_info : ", playlist_info)

            # if playlist id in backend then check whether it exist in user playlist or not
            check_playlistid = []  # key = Playlist_name , value = Playlist_id
            check_playlistid = [key for key, value in playlist_info.items() if value == backend_ai_playlistid]

            if len(check_playlistid) == 0:
                print("Ai playlist not found")
                # Delete backend ai playlistid
                delete_ai_playlist_url = "https://api.software.com/music/playlist/generated/" + \
                    backend_ai_playlistid
                jwt = getItem("jwt")
                # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE0Nzc1LCJpYXQiOjE1NjgwMDg1Mjh9.h-2i2SRK3kWSojBkJ3JXUztWFdErUotAz9wk7JHw1H4"
                headers0 = {'content-type': 'application/json',
                            'Authorization': jwt}
                delete_ai_playlistid = requests.delete(
                    delete_ai_playlist_url, headers=headers0)
                if delete_ai_playlistid.status_code == 200:
                    print("Deleted ai playlistid: ", delete_ai_playlistid.text)
                    # Enable Generate AI button
                    setValue("ai_playlist", False)
                    print("setValue(ai_playlist, False)")
                    print("Deleted old one. Generate new one")
                else:
                    print("unable to delete playlistid",
                          delete_ai_playlistid.text)
                    pass

            else:
                print("found AI playlist", check_playlistid)
                # Assign to global variable
                AI_PLAYLIST_NAME = check_playlistid[0]
                AI_PLAYLIST_ID = backend_ai_playlistid
                print("AI_PLAYLIST_ID :", AI_PLAYLIST_ID)
                # Enable Refresh AI button
                setValue("ai_playlist", True)

        else:

            AI_PLAYLIST_ID = ""
            # Enable Generate AI button
            print(getValue("ai_playlist", False))
            setValue("ai_playlist", False)
            print("AI playlist not found in backend. Generate new one")
            pass
    else:
        print("AI Playlist not checked. Try later")


# Generate My AI Playlist
def generateMyAIPlaylist():
    global AI_PLAYLIST_ID
    spotifyUserId = userMeInfo().get('id')
    create_playlist_url = "https://api.spotify.com/v1/users/" + \
        spotifyUserId + "/playlists"
    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    data = {"name": AI_PLAYLIST_NAME, "public": True, "description": ""}
    json_data = json.dumps(data)
    print("json_data :", json_data,"\nheaders :",headers,"\ncreate_playlist_url :",create_playlist_url)
    create_my_ai_playlist = requests.post(
        create_playlist_url, headers=headers, data=json_data)
    print("create_my_ai_playlist :", create_my_ai_playlist.text)

    if create_my_ai_playlist.status_code >= 200:
        # print("create_my_ai_playlist :", create_my_ai_playlist)
        response = create_my_ai_playlist.json()
        AI_PLAYLIST_ID = response['id']

        update_playlist_url = "https://api.software.com/music/playlist/generated"
        jwt = getItem("jwt")
        # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE0Nzc1LCJpYXQiOjE1NjgwMDg1Mjh9.h-2i2SRK3kWSojBkJ3JXUztWFdErUotAz9wk7JHw1H4"
        headers0 = {'content-type': 'application/json', 'Authorization': jwt}
        data = {"playlist_id": AI_PLAYLIST_ID,
                "playlistTypeId": 1, "name": AI_PLAYLIST_NAME}
        json_data = json.dumps(data)
        update_playlist = requests.post(
            update_playlist_url, headers=headers0, data=json_data)

        if update_playlist.status_code >= 200:
            print("update_playlist id to software backend :", update_playlist)
            software_recommend = "https://api.software.com/music/recommendations?limit=40"
            jwt = getItem("jwt")
            # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE0Nzc1LCJpYXQiOjE1NjgwMDg1Mjh9.h-2i2SRK3kWSojBkJ3JXUztWFdErUotAz9wk7JHw1H4"
            # headers0 = {'content-type': 'application/json', 'Authorization': jwt}
            get_recommends = requests.get(software_recommend, headers=headers0)

            if get_recommends.status_code >= 200:
                print("get_recommends :\n", get_recommends)
                recommends_song_list = get_recommends.json()
                uris_list = []
                for i in range(len(recommends_song_list)):
                    uris_list.append(recommends_song_list[i]['uri'])

                send_uris_url = "https://api.spotify.com/v1/playlists/" + AI_PLAYLIST_ID + "/tracks"
                # headers = {"Authorization": "Bearer {}".format(access_token)}
                uris_data = {"uris": uris_list, "position": 0}
                json_data = json.dumps(uris_data)
                post_uris = requests.post(
                    send_uris_url, headers=headers, data=json_data)
                if post_uris.status_code >= 200:
                    print("post_uris", post_uris)
                    setValue("ai_playlist", True)
                    message_dialog = sublime.message_dialog("AI playlist Generated !")

                else:
                    print("post_uris failed", post_uris)
                    pass
            else:
                print("get_recommends failed", get_recommends)
                pass
        else:
            print("update_playlist", update_playlist.text)
            pass
    else:
        print("create_my_ai_playlist", create_my_ai_playlist.text)
        pass


# Refresh MY AI Playlist
def refreshMyAIPlaylist():
    # get track uris list
    software_recommend = "https://api.software.com/music/recommendations?limit=40"
    jwt = getItem("jwt")
    # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE0Nzc1LCJpYXQiOjE1NjgwMDg1Mjh9.h-2i2SRK3kWSojBkJ3JXUztWFdErUotAz9wk7JHw1H4"
    headers0 = {'content-type': 'application/json', 'Authorization': jwt}
    get_recommends = requests.get(software_recommend, headers=headers0)

    if get_recommends.status_code >= 200:
        recommends_song_list = get_recommends.json()
        uris_list = []
        for i in range(len(recommends_song_list)):
            uris_list.append(recommends_song_list[i]['uri'])

        # wipe out the old track uris
        refresh_backend_url = "https://api.spotify.com" + \
            "/v1/playlists/" + AI_PLAYLIST_ID + "/tracks"
        headers = {"Authorization": "Bearer {}".format(
            getItem('spotify_access_token'))}
        uris_data = {"uris": uris_list}
        json_data = json.dumps(uris_data)
        wipe_uris = requests.put(
            refresh_backend_url, headers=headers, data=json_data)

        if wipe_uris.status_code >= 200:
            # print("wipe_uris", wipe_uris)
            software_recommend = "https://api.software.com/music/recommendations?limit=40"
            jwt = getItem("jwt")
            # jwt = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE0Nzc1LCJpYXQiOjE1NjgwMDg1Mjh9.h-2i2SRK3kWSojBkJ3JXUztWFdErUotAz9wk7JHw1H4"
            # headers0 = {'content-type': 'application/json', 'Authorization': jwt}
            get_recommends = requests.get(software_recommend, headers=headers0)

            if get_recommends.status_code >= 200:
                recommends_song_list = get_recommends.json()
                uris_list = []
                for i in range(len(recommends_song_list)):
                    uris_list.append(recommends_song_list[i]['uri'])

                send_uris_url = "https://api.spotify.com/v1/playlists/" + AI_PLAYLIST_ID + "/tracks"
                uris_data = {"uris": uris_list, "position": 0}
                json_data = json.dumps(uris_data)
                post_uris = requests.post(
                    send_uris_url, headers=headers, data=json_data)

                if post_uris.status_code >= 200:
                    print("AI playlist refreshed !")
                    setValue("ai_playlist", True)
                    message_dialog = sublime.message_dialog("AI playlist Refreshed !")
                else:
                    print("Unable to to refresh\n", post_uris)
                    pass

            else:
                print("Unable to get recommendation tracks", get_recommends)
                pass
        else:
            print("Unable to wipe out uris\n", wipe_uris)
            pass

    else:
        print("Unable to wipe uris\n", get_recommends.text)
        pass


def launchDesktopPlayer():
    try:
        if isMac is True:
            launch = subprocess.Popen(["open", "-a", "spotify"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            user = os.path.expanduser('~')
            spotify_path = os.path.join(user , r"AppData\Roaming\Spotify\Spotify.exe")
            launch = subprocess.Popen(spotify_path, shell=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print("launchDesktopPlayer",e)

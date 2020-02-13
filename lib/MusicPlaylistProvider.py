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


# global variables
current_playlist_name = ""
current_song = ""  # Current track id

AI_PLAYLIST_ID = ""
AI_PLAYLIST_NAME = "My AI Top 40"

playlist_info = {}
playlist_id = ''

playlist_data = []
spotifyUserId = ""


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

        if playlist_id == None:
            try:
                openTrackInWeb(playlist_id, current_song)
            except Exception as e:
                print("OpenSongsCommand:run:openTrackInWeb", e)
            getActiveDeviceInfo()
            playThisSong(ACTIVE_DEVICE.get('device_id'), songs_tree)
        else:
            try:
                openTrackInWeb(playlist_id, current_song)
            except Exception as e:
                print("OpenSongsCommand:run:openTrackInWeb", e)
            getActiveDeviceInfo()
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
            # print("NO SONG found")

    def confirm(self, value):
        global current_song
        current_song = value
        print("current_song", current_song)

        if playlist_id == None:
            print('#'*10, 'playlist_id == None SongInputHandler')
            try:
                openTrackInWeb(playlist_id, current_song)
            except Exception as e:
                print("SongInputHandler:confirm:openTrackInWeb", e)
            getActiveDeviceInfo()
            playThisSong(ACTIVE_DEVICE.get('device_id'), current_song)
        else:
            try:
                openTrackInWeb(playlist_id, current_song)
            except Exception as e:
                print("SongInputHandler:confirm:openTrackInWeb", e)
            getActiveDeviceInfo()
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
    if isMac() == True and userTypeInfo() == "non-premium":
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}"'
        '''.format(track_id)
        os.system(script)
        print("Played from desktop")

    else:
        headers = {"Authorization": "Bearer {}".format(
            getItem('spotify_access_token'))}
        data = {}
        try:
            print("track_id", track_id)
            data = {"uris": ["spotify:track:" + track_id]}
            payload = json.dumps(data)
            playstr = SPOTIFY_API + "/v1/me/player/play?device_id=" + currentDeviceId
            plays = requests.put(playstr, headers=headers, data=payload)
            print(plays.text)
        except Exception as e:
            print("playThisSong", e)
    currentTrackInfo()


# Play song from playlist using playlist_id and track_id
def playSongFromPlaylist(currentDeviceId, playlistid, track_id):
    global playlist_id
    playlist_id = playlistid
    if isMac() == True and userTypeInfo() == "non-premium":
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}" in context "spotify:playlist:{}"'
        '''.format(track_id, playlist_id)
        os.system(script)
        print("Played from desktop")
        pass

    else:
        headers = {"Authorization": "Bearer {}".format(
            getItem('spotify_access_token'))}
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
    else:
        tracks = list('No song found',)
#             tracks = dict(zip(names,ids))
    return list(tracks)


# GET playlist name and ids ro view
def getUserPlaylistInfo(spotifyUserId):
    headers = {"Authorization": "Bearer {}".format(
        getItem('spotify_access_token'))}
    playlist_track = SPOTIFY_API + "/v1/users/" + spotifyUserId + "/playlists"
    playlist = requests.get(playlist_track, headers=headers)
    try:
        if playlist.status_code == 200:
            playlistname = playlist.json()
            names = []
            ids = []
            playlist = []
            for i in playlistname['items']:
                names.append(i['name'])
                ids.append(i['id'])
                playlist = dict(zip(names, ids))
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
def getSortedUserPlaylists():
    # global playlist_info
    spotifyUserId = userMeInfo().get('id')
    print("spotifyUserId: ", spotifyUserId)
    global playlist_data
    playlist_data = []
    '''
    playlist data should be in this form
    data = [{"id": 1, "name": "Playlist_name","track_list": [
            ('Tokyo Drifting', '3AHqaOkEFKZ6zEHdiplIv7'),
            ('Alan Silvestri', '0pHcFONMGTN8g18jbz6lJu')] } ]
    '''
    try:
        playlist_info = getUserPlaylistInfo(spotifyUserId)
    except Exception as e:
        print("Music Time: getuserPlaylistinfoerror", e)

    sorted_playlist = dict(
        sorted(playlist_info.items(), key=lambda playlist_info: playlist_info[0]))
    print(sorted_playlist)

    for k, v in sorted_playlist.items():
        playlist_data.append({'id': v, 'name': k, 'songs': getTracks(v)})
    playlist_data.append(
        {'id': '000', 'name': 'Liked songs', 'songs': getLikedSongs()})
    print("GOT playlist data :\n", playlist_data)


# Populate playlist data include playlists name/ids and tracks name/ids
def getUserPlaylists():
    global playlist_info
    spotifyUserId = userMeInfo().get('id')
    print("spotifyUserId: ", spotifyUserId)
    global playlist_data
    playlist_data = []
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
    for k, v in playlist_info.items():
        playlist_data.append({'id': v, 'name': k, 'songs': getTracks(v)})
    playlist_data.append(
        {'id': '000', 'name': 'Liked songs', 'songs': getLikedSongs()})
    print("GOT playlist data :\n", playlist_data)
    # message_dialog = sublime.message_dialog("Playlists Refreshed !")



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

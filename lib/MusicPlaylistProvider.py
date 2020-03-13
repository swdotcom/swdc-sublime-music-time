'''
 MusicPlaylistProvider.py will have all of the code to set up,
 refresh the UI, manage actions like getting, adding tracks to,
 and creating playlists.
'''
import sublime
import sublime_plugin
from threading import Thread, Timer, Event
import webbrowser

from ..Constants import *
from .SoftwareUtil import *
from .SoftwareHttp import *
from ..Software import *
from .SoftwareMusic import *
from .MusicControlManager import *
from .PlayerManager import *
from .SocialShareManager import *


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

sortby = "time"  # or "az"


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
        global ACTIVE_DEVICE

        print("ACTIVE_DEVICE", ACTIVE_DEVICE)
        # print('first',songs_tree)
        self.view.insert(edit, 0, songs_tree)
        # print('second',songs_tree)

        print("current_song", current_song)
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
            listoftracks = getSongsInPlaylist(current_playlist_name)
            if listoftracks == []:
                return [("It's a bit empty here...","")]
                # msg = "a bit empty here"
                # message_dialog = sublime.message_dialog("This playlist is a bit empty here.")
            else:
                return listoftracks
        else:
            message_dialog = sublime.message_dialog(
                "Songs not found. Please Use \nTools > Music Time > My Playlists > Open Playlist")
            current_window = sublime.active_window()
            current_window.run_command("hide_overlay")
            # return [("Songs not found. Please Use \nTools > Music Time > My Playlists > Open Playlist","")]
            # print("NO SONG found")

    def confirm(self, value):
        global current_song
        current_song = value
        print("current_song", current_song)

        if len(current_song) != 0:
            if playlist_id == None:
                print('#'*10, 'playlist_id == None SongInputHandler')
                playThisSong(ACTIVE_DEVICE.get('device_id'), current_song)
            else:
                print('#'*10, 'else == None SongInputHandler')
                playSongFromPlaylist(ACTIVE_DEVICE.get(
                    'device_id'), playlist_id, current_song)
        else:
            pass
            # sublime.message_dialog("Can't play the track.")



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
            print('playlist.get("songs")',playlist.get("songs"))
            return playlist.get("songs")


# Play song from playlist without playlist_id
def playThisSong(currentDeviceId, track_id):
    global ACTIVE_DEVICE

    if isMac() == True and userTypeInfo() == "non-premium":
        if currentDeviceId is None:
            # openDesktopPlayer()
            launchDesktopPlayer()

        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}"'
        '''.format(track_id)
        os.system(script)
        print("Played from desktop")

    else:

        print(Liked_songs_ids)
        uris_list = []
        for song_id in Liked_songs_ids:
            uris_list.append("spotify:track:"+song_id)
        print("uris_list", uris_list)

        track_index = uris_list.index("spotify:track:" + track_id)
        print("track_index", track_index)
        '''
        {"uris": ["spotify:track:1rZwgdUwUYBqEphd4CXynL", "spotify:track:6Q8mqjuz8xqdoUjhZQDfY7",
                  "spotify:track:1aDklx1GaBqHFowCzz63wU", "spotify:track:4oaU0fMSg3n9kqOwmLPVhH",
                  "spotify:track:4WZizdGrBVSZCES0q2XDwu", "spotify:track:0l1i3nJ4aDMk0inxnvzYTz"],
                  "offset": {"position": 2}}
        0TZjSoLZcKZGaFEv1ytOqb
        '''
        data = {}
        try:
            print("track_id", track_id)
            # data = {"uris": ["spotify:track:" + track_id]}
            data = {"uris": uris_list, "offset": {
                "position": track_index}}  # {"position": 5}
            payload = json.dumps(data)
            print("payload", payload)
            print("currentDeviceId", currentDeviceId)

            if ACTIVE_DEVICE == {}:

                msg = sublime.yes_no_cancel_dialog(
                    "Launch a Spotify device", "Web player", "Desktop player")

                if msg is 1:
                    webbrowser.open("https://open.spotify.com/")
                    time.sleep(3)
                    try:
                        devices = getSpotifyDevice()
                        print("Launch Web Player:devices", devices)

                        device_id = getWebPlayerId(devices)
                        print("Launch Web Player:device_id", device_id)

                        ACTIVE_DEVICE = {}
                        ACTIVE_DEVICE['device_id'] = device_id
                        print(ACTIVE_DEVICE)
                        transferPlayback(device_id)
                        currentDeviceId = device_id
                        time.sleep(1)
                    except Exception as e:
                        print("Launch Web Player Error", e)
                elif msg is 2:
                    launchDesktopPlayer()
                    time.sleep(5)
                    try:
                        devices = getSpotifyDevice()
                        print("Launch Web Player:devices", devices)

                        device_id = getNonWebPlayerId(devices)
                        print("Launch Web Player:device_id", device_id)

                        ACTIVE_DEVICE = {}
                        ACTIVE_DEVICE['device_id'] = device_id
                        print(ACTIVE_DEVICE)
                        transferPlayback(device_id)
                        currentDeviceId = device_id
                        time.sleep(1)
                    except Exception as e:
                        print("Launch Desktop Player Error", e)
                else:
                    pass

            api = "/v1/me/player/play?device_id=" + currentDeviceId
            plays = requestSpotify("PUT", api, payload, getItem('spotify_access_token'))
            print(plays)
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
            # openDesktopPlayer()
            launchDesktopPlayer()
        script = '''
        osascript -e 'tell application "Spotify" to play track "spotify:track:{}" in context "spotify:playlist:{}"'
        '''.format(track_id, playlist_id)
        os.system(script)
        print("Played from desktop")
        pass

    else:

        if currentDeviceId == None:

            msg = sublime.yes_no_cancel_dialog(
                "Launch a Spotify device", "Web player", "Desktop player")

            if msg is 1:
                webbrowser.open("https://open.spotify.com/")
                time.sleep(3)
                try:
                    devices = getSpotifyDevice()
                    print("Launch Web Player:devices", devices)

                    device_id = getWebPlayerId(devices)
                    print("Launch Web Player:device_id", device_id)

                    ACTIVE_DEVICE = {}
                    ACTIVE_DEVICE['device_id'] = device_id
                    print(ACTIVE_DEVICE)
                    transferPlayback(device_id)
                    currentDeviceId = device_id
                    time.sleep(3)
                except Exception as e:
                    print("Launch Web Player", e)
            elif msg is 2:
                launchDesktopPlayer()
                time.sleep(5)
                try:
                    devices = getSpotifyDevice()
                    print("Launch Web Player:devices", devices)

                    device_id = getNonWebPlayerId(devices)
                    print("Launch Web Player:device_id", device_id)

                    ACTIVE_DEVICE = {}
                    ACTIVE_DEVICE['device_id'] = device_id
                    print(ACTIVE_DEVICE)
                    transferPlayback(device_id)
                    currentDeviceId = device_id
                    time.sleep(3)
                except Exception as e:
                    print("Launch Desktop Player Error", e)
            else:
                pass

        print("device",playstr)
        data = {}
        try:
            data["context_uri"] = "spotify:playlist:" + playlist_id
            data['offset'] = {"uri": "spotify:track:" + track_id}
            payload = json.dumps(data)
            print("playSongFromPlaylist", payload)

            api = "/v1/me/player/play?device_id=" + currentDeviceId
            plays = requestSpotify("PUT", api, payload, getItem('spotify_access_token'))
            print(plays)
        except Exception as e:
            print("playSongFromPlaylist", e)
    currentTrackInfo()


# fetch liked songs tracks
def getLikedSongs():
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
            names.append(i['track']['name'])
            tracks = tuple(zip(names, ids))
        Liked_songs_ids = ids
        print("Liked_songs_ids", Liked_songs_ids)
    else:
        tracks = []
#             tracks = dict(zip(names,ids))
    return list(tracks)


# GET playlist name and ids ro view
def getUserPlaylistInfo(spotifyUserId):
    global playlist_names

    api = "/v1/users/" + spotifyUserId + "/playlists"
    playlist = requestSpotify("GET", api, None, getItem('spotify_access_token'))
    try:
        if playlist["status"] == 200:
            # playlistname = playlist.json()
            names = []
            ids = []
            playlist = {}
            playlist_names = []
            for i in playlist['items']:

                names.append(i['name'])
                ids.append(i['id'])
                playlist = dict(zip(names, ids))

        playlist_names = list(names)
        print("In def playlist_names", playlist_names)
    except Exception as e:
        print("getUserPlaylistInfo err", e)

    return playlist


# get tracks data using playlist id
def getTracks(playlist_id):

    api = "/v1/playlists/" + playlist_id + "/tracks"
    tracklist = requestSpotify("GET", api, None, getItem('spotify_access_token'))
    if tracklist["status"] == 200:
        # track_list = tracklist.json()
        ids = []
        names = []
        tracks = {}
        for i in tracklist['items']:
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
        print("sortby:sortPlaylistByLatest:", sortby)

    else:
        # sort by A-Z
        playlist_data = []
        for k, v in playlist_info.items():
            if "Software" in k:
                playlist_data.append(
                    {'id': v, 'name': k, 'playlistTypeId': 1, 'songs': getTracks(v)})
                # print("got software",k," ",v)

            elif v == AI_PLAYLIST_ID or k == AI_PLAYLIST_NAME:
                playlist_data.append(
                    {'id': v, 'name': k, 'playlistTypeId': 2, 'songs': getTracks(v)})
                # print("got AI playlist",k," ",v)

            else:
                playlist_data.append(
                    {'id': v, 'name': k, 'playlistTypeId': 4, 'songs': getTracks(v)})
                # print("got user playlist",k," ",v)

        liked_songs = getLikedSongs()
        if liked_songs != []:
            playlist_data.append(
                {'id': '000', 'name': 'Liked songs', 'playlistTypeId': 3, 'songs': liked_songs})
            print("got liked songs")
        print("No liked songs")
        print("No of playlist :", len(playlist_data))
        try:
            sortPlaylistByAz()
        except Exception as e:
            print("sortPlaylistByAz", e)
        print("sortby:sortPlaylistByAz:", sortby)


# Sort by latest code
def sortPlaylistByLatest():
    global playlist_data
    global playlist_names
    global sortby
    sortby = "time"

    print("got inside loop: playlist_names", playlist_names)
    sec_one = []  # Software top 40 and AI playlist

    sec_three = []  # user playlist
    for k in playlist_names:
        if k == "Software Top 40":
            sec_one.append(k)
        elif k == "My AI Top 40":
            sec_one.append(k)
        else:
            sec_three.append(k)

    if len(sec_one) == 2:
        # Swapping (1)Software top 40 (2)AI playlist
        sec_one[0], sec_one[1] = sec_one[1], sec_one[0]

    liked_songs = getLikedSongs()
    if liked_songs != []:
        sec_two = ["Liked songs"]  # Liked songs
        # Final list with (1)Software top 40 (2)AI playlist (3)Liked songs (4)user playlist
        final_list = sec_one + sec_two + sec_three
    else:
        final_list = sec_one + sec_three

    playlist_data = []
    for i in final_list:

        if i == "Software Top 40":
            #         playlist_data[0] = {'id':playlist_info.get(i),'name':i,'playlistTypeId': 1,'songs': getTracks(playlist_info.get(i))}
            playlist_data.append({'id': playlist_info.get(
                i), 'name': i, 'playlistTypeId': 1, 'songs': getTracks(playlist_info.get(i))})
        elif i == "My AI Top 40" or i == AI_PLAYLIST_NAME:
            #         playlist_data[1] = {'id':playlist_info.get(i),'name':i,'playlistTypeId': 1,'songs': getTracks(playlist_info.get(i))}
            playlist_data.append({'id': playlist_info.get(
                i), 'name': i, 'playlistTypeId': 2, 'songs': getTracks(playlist_info.get(i))})
        elif i == "Liked songs":
            #         playlist_data[2] = {'id':playlist_info.get(i),'name':i,'playlistTypeId': 3,'songs': getLikedSongs()}
            playlist_data.append({'id': playlist_info.get(
                i), 'name': i, 'playlistTypeId': 3, 'songs': liked_songs})
        else:
            playlist_data.append({'id': playlist_info.get(
                i), 'name': i, 'playlistTypeId': 4, 'songs': getTracks(playlist_info.get(i))})

    # final_playlist = sec_one + sec_three
    for k in playlist_data:
        print(k['name'], "|", k['playlistTypeId'])


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

    playlist_section_one = sorted(
        playlist_section_one, key=lambda i: i['playlistTypeId'])

    # sorting by playlist name # c = sorted(s, key=lambda c: (c.lower(), c.islower()))
    playlist_section_two = sorted(playlist_section_two, key=lambda i: (
        i['name'].lower(), i['name'].islower()))
    # playlist_section_two = sorted(playlist_section_two, key = lambda i: i['name'])

    # Final sorted playlist in A-z
    playlist_data = playlist_section_one + playlist_section_two
    print("sortby", sortby)
    for i in playlist_data:
        print(i['name'], "|", i['playlistTypeId'])
    # print(playlist_data)
    # return AZSortedplaylist


# Check AI playlist exist or not
def checkAIPlaylistid():
    global AI_PLAYLIST_ID
    global AI_PLAYLIST_NAME
    # global playlist_info
    spotifyUserId = userMeInfo().get('id')

    # Check for ai_playlist in software backend
    api = "/music/playlist/generated"
    get_ai_playlistid = requestIt("GET", api, None, getItem("jwt"), True)
    print("get_ai_playlistid: %s" % get_ai_playlistid)
    if get_ai_playlistid is not None and get_ai_playlistid["status"] == 200:
        # get_ai_playlistid_data = get_ai_playlistid.json()
        print("get_ai_playlistid_data\n", get_ai_playlistid)
        if len(get_ai_playlistid) > 0:
            backend_ai_playlistid = get_ai_playlistid[0]['playlist_id']
            print("backend_ai_playlistid : ", backend_ai_playlistid)

            playlist_info = {}
            playlist_info = getUserPlaylistInfo(spotifyUserId)
            print("checkAIPlaylistid >> playlist_info : ", playlist_info)

            # if playlist id in backend then check whether it exist in user playlist or not
            check_playlistid = []  # key = Playlist_name , value = Playlist_id
            check_playlistid = [
                key for key, value in playlist_info.items() if value == backend_ai_playlistid]

            if len(check_playlistid) == 0:
                print("Ai playlist not found")
                # Delete backend ai playlistid
                api = "/music/playlist/generated/" + backend_ai_playlistid
                delete_ai_playlistid = requestIt("DELETE", api, None, getItem("jwt"), True)
                if delete_ai_playlistid is not None and delete_ai_playlistid["status"] == 200:
                    # print("Deleted ai playlistid: ", delete_ai_playlistid)
                    # Enable Generate AI button
                    setValue("ai_playlist", False)
                    print("setValue(ai_playlist, False)")
                    print("Deleted old one. Generate new one")
                else:
                    print("unable to delete playlistid",
                          delete_ai_playlistid)
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

    data = {"name": AI_PLAYLIST_NAME, "public": True, "description": ""}
    json_data = json.dumps(data)
    print("json_data :", json_data, "\nheaders :", headers,
          "\ncreate_playlist_url :", create_playlist_url)

    api = "/v1/users/" + spotifyUserId + "/playlists"
    create_my_ai_playlist = requestSpotify("POST", api, json_data, getItem('spotify_access_token'))
    print("create_my_ai_playlist : %s", create_my_ai_playlist)

    if create_my_ai_playlist["status"] >= 200:
        # print("create_my_ai_playlist :", create_my_ai_playlist)
        # response = create_my_ai_playlist.json()
        AI_PLAYLIST_ID = create_my_ai_playlist['id']

        data = {"playlist_id": AI_PLAYLIST_ID,
                "playlistTypeId": 1, "name": AI_PLAYLIST_NAME}
        json_data = json.dumps(data)

        api = "/music/playlist/generated"
        update_playlist = requestIt("POST", api, json_data, getItem("jwt"), True)

        if update_playlist is not None and update_playlist["status"] >= 200:
            print("update_playlist id to software backend :", update_playlist)

            api = "/music/recommendations?limit=40"
            get_recommends = requestIt("GET", api, None, getItem("jwt"), True)

            if get_recommends is not None and get_recommends["status"] >= 200:
                print("get_recommends :\n", get_recommends)
                # recommends_song_list = get_recommends.json()
                uris_list = []
                for i in range(len(get_recommends)):
                    uris_list.append(get_recommends[i]['uri'])

                # headers = {"Authorization": "Bearer {}".format(access_token)}
                uris_data = {"uris": uris_list, "position": 0}
                json_data = json.dumps(uris_data)

                api = "/v1/playlists/" + AI_PLAYLIST_ID + "/tracks"
                post_uris = requestIt("POST", api, json_data, getItem("jwt"), True)

                if post_uris is not None and post_uris["status"] >= 200:
                    print("post_uris", post_uris)
                    setValue("ai_playlist", True)
                    message_dialog = sublime.message_dialog(
                        "AI playlist Generated !")

                else:
                    print("post_uris failed", post_uris)
                    pass
            else:
                print("get_recommends failed", get_recommends)
                pass
        else:
            print("update_playlist", update_playlist)
            pass
    else:
        print("create_my_ai_playlist", create_my_ai_playlist)
        pass


# Refresh MY AI Playlist
def refreshMyAIPlaylist():
    # get track uris list
    software_recommend = SOFTWARE_API + "/music/recommendations?limit=40"

    api = "/music/recommendations?limit=40"
    get_recommends = requestIt("GET", api, None, getItem("jwt"), True)

    print("get_recommends: %s" % get_recommends)
    if get_recommends is not None and get_recommends["status"] >= 200:
        # recommends_song_list = get_recommends.json()
        uris_list = []
        for i in range(len(get_recommends)):
            uris_list.append(get_recommends[i]['uri'])

        # wipe out the old track uris
        uris_data = {"uris": uris_list}
        json_data = json.dumps(uris_data)

        api = "/v1/playlists/" + AI_PLAYLIST_ID + "/tracks"
        wipe_uris = requestSpotify("PUT", api, json_data, getItem('spotify_access_token'))

        if wipe_uris["status"] >= 200:
            # print("wipe_uris", wipe_uris)

            api = "/music/recommendations?limit=40"
            get_recommends = requestIt("GET", api, None, getItem("jwt"), True)

            if get_recommends is not None and get_recommends["status"] >= 200:
                # recommends_song_list = get_recommends.json()
                uris_list = []
                for i in range(len(get_recommends)):
                    uris_list.append(get_recommends[i]['uri'])

                uris_data = {"uris": uris_list, "position": 0}
                json_data = json.dumps(uris_data)

                api = "/v1/playlists/" + AI_PLAYLIST_ID + "/tracks"
                post_uris = requestIt("POST", api, json_data, getItem("jwt"), True)
                if post_uris is not None and post_uris["status"] >= 200:
                    print("AI playlist refreshed !")
                    setValue("ai_playlist", True)
                    message_dialog = sublime.message_dialog(
                        "AI playlist Refreshed !")
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
        print("Unable to wipe uris\n", get_recommends)
        pass


class CreatePlaylist(sublime_plugin.WindowCommand):
    def run(self):
        default_text = "NewPlaylist" + datetime.datetime.now().strftime("%Y%m%d%w-%H%M%S")
        self.window.show_input_panel(
            "Enter a playlist name:", default_text, self.on_done, self.on_change, None)

    def on_done(self, providedname):
        print("providedname", providedname)
        newplaylistid = CreateNewPlaylist(providedname)
        if len(newplaylistid) == 22:
            print("playlist created !")
            current_song_id, current_song_name = getSpotifyTrackId()
            print("current_song_id", current_song_id)
            addTrackToPlaylist(current_song_id, newplaylistid, providedname)

    def on_change(self, providedname):
        if len(providedname) == 0:
            sublime.message_dialog("Please Enter valid a name.")
        elif len(providedname) == 1 and providedname.isspace():
            sublime.message_dialog("Please Enter valid a name.")
        else:
            pass


def CreateNewPlaylist(playlistname):
    spotifyUserId = userMeInfo().get('id')

    # "public": True, "description": ""
    json_data = json.dumps({"name": playlistname, })
    print("json_data :", json_data, "\nheaders :", headers,
          "\ncreate_playlist_url :", create_playlist_url)

    api = "/v1/users/" + spotifyUserId + "/playlists"
    create_playlist = requestSpotify("POST", api, json_data, getItem('spotify_access_token'))
    # create_playlist_response = create_playlist.json()
    if create_playlist["status"] >= 200:
        # response = create_playlist.json()
        new_playlist_id = create_playlist['id']
        return new_playlist_id
    else:
        print("UNABLE", create_playlist)
        return ""


class CreateAddPlaylist(sublime_plugin.WindowCommand):

    def run(self):
        # print("playlist_data",playlist_data)
        # items = [i['name'] for i in playlist_data]
        item_list = [i['name'] for i in playlist_data if (i['name'] not in ['My AI Top 40','Software Top 40','Liked songs'])]
        playlist_items = ['New playlist'] + item_list
        # playlist_items = [('New playlist','')] + [(i['name'],i['id']) for i in playlist_data]
        self.window.show_quick_panel(
            playlist_items, lambda id: self.on_done(id, playlist_items))

    def on_done(self, id, playlist_items):
        if id >= 0 and playlist_items[id] == "New playlist":
            # Invoke a function because Item 2 was selected
            print("Create a new playlist selected", playlist_items[id])
            # spotifyUserId = userMeInfo().get('id')
            # print("spotifyUserId",spotifyUserId)
            # print("playlist_info",playlist_info)
            current_window = sublime.active_window()
            current_window.run_command("create_playlist")
            pass
        elif id >= 0 and playlist_items[id] in [i['name'] for i in playlist_data]:
            print("Adding track to existing playlist")
            playlist_name = playlist_items[id]
            playlist_id = playlist_info.get(playlist_name)
            current_song_id, current_song_name = getSpotifyTrackId()
            print("playlist name:", playlist_name, " id:",
                  playlist_id, "current_song_id", current_song_id)
            addTrackToPlaylist(current_song_id, playlist_id,playlist_name)
        else:
            current_window = sublime.active_window()
            current_window.run_command("hide_overlay")

    def is_enabled(self): 
        return (getValue("logged_on", True) is True)


def addTrackToPlaylist(trackid, playlistid, play_list_name):
    payload = json.dumps({"uris": ["spotify:track:"+trackid], "position": 0})

    api = "/v1/playlists/"+playlistid+"/tracks"
    resp = requestSpotify("POST", api, payload, getItem('spotify_access_token'))
    if resp["status"] == 201:
        print("success", resp)
        msg = "Track added to "+ '"' +play_list_name+ '"'
        sublime.message_dialog(msg)
        getUserPlaylists()
    else:
        # msg = resp.json()['error']['message']
        msg = resp['error']['message']
        print("failed", msg)
        msg_body = "Unable to add track.\n"+msg
        sublime.message_dialog(msg_body)


def launchDesktopPlayer():
    
    if isMac() is True:
        launch = subprocess.Popen(
            ["open", "-a", "spotify"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    else:
        user = os.path.expanduser('~')
        spotify_path = os.path.join(
            user, r"AppData\Roaming\Spotify\Spotify.exe")
        launch = subprocess.Popen(spotify_path, shell=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    err_msg = launch.communicate()[1].decode("utf-8") 
    print("launchDesktopPlayer", err_msg)
    if len(err_msg) == 0:
        print("Desktop player opened")
    else:
        if "The system cannot find the path specified" in err_msg:
            msg_body = "Unable to launch Desktop player\n" + "Desktop player not found"
        else:
            msg_body = "Unable to launch Desktop player" + err_msg
        sublime.error_message(msg_body)
        msg = sublime.ok_cancel_dialog("Launching Web player ...", "Ok")
        if msg is True:
            webbrowser.open("https://open.spotify.com/")
            print("Launching Web player ...")
        else:
            pass  



import sublime_plugin
import sublime

from .SoftwareHttp import *
from .SoftwareUtil import *
from ..Software import *
from .SoftwareMusic import *
from .PlayerManager import *


# recommendation_data
recommendation_data = []
mood_list = ['Happy', 'Energetic', 'Danceable',
             'Instrumental', 'Familiar', 'Quiet music']

genre_list = ['Acoustic', 'Afrobeat', 'Alt rock', 'Alternative', 'Ambient', 'Anime',
              'Black metal', 'Bluegrass', 'Blues', 'Bossanova', 'Brazil', 'Breakbeat',
              'British', 'Cantopop', 'Chicago house', 'Children', 'Chill', 'Classical',
              'Club', 'Comedy', 'Country', 'Dance', 'Dancehall', 'Death metal', 'Deep house',
              'Detroit techno', 'Disco', 'Disney', 'Drum and bass', 'Dub', 'Dubstep',
              'Edm', 'Electro', 'Electronic', 'Emo', 'Folk', 'Forro', 'French', 'Funk',
              'Garage', 'German', 'Gospel', 'Goth', 'Grindcore', 'Groove', 'Grunge',
              'Guitar', 'Happy', 'Hard rock', 'Hardcore', 'Hardstyle', 'Heavy-metal',
              'Hip-hop', 'Hip hop', 'Holidays', 'Honky tonk', 'House', 'Idm', 'Indian',
              'Indie', 'Indie pop', 'Industrial', 'Iranian', 'J dance', 'J idol', 'J pop',
              'J rock', 'Jazz', 'K pop', 'Kids', 'Latin', 'Latino', 'Malay', 'Mandopop',
              'Metal', 'Metal misc', 'Metalcore', 'Minimal techno', 'Movies', 'Mpb',
              'New age', 'New release', 'Opera', 'Pagode', 'Party', 'Philippines opm',
              'Piano', 'Pop', 'Pop film', 'Post dubstep', 'Power pop', 'Progressive house',
              'Psych rock', 'Punk', 'Punk-rock', 'R n b', 'Rainy day', 'Reggae', 'Reggaeton',
              'Road trip', 'Rock', 'Rock n roll', 'Rockabilly', 'Romance', 'Sad', 'Salsa',
              'Samba', 'Sertanejo', 'Show tunes', 'Singer-songwriter', 'Ska', 'Sleep', 'Songwriter',
              'Soul', 'Soundtracks', 'Spanish', 'Study', 'Summer', 'Swedish', 'Synth-pop',
              'Tango', 'Techno', 'Trance', 'Trip hop', 'Turkish', 'Work out', 'World-music']

filter_type = ""
current_track = ""


class OpenMoodlist(sublime_plugin.TextCommand):
    def input(self, args):
        infoMsg = "Mood list opened"
        print(infoMsg)
        return MoodlistInputHandler()

    def run(self, edit, typelist):
        self.view.insert(edit, 0, typelist)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class OpenGenrelist(sublime_plugin.TextCommand):
    def input(self, args):
        infoMsg = "Genre list opened"
        print(infoMsg)
        return GenrelistInputHandler()

    def run(self, edit, typelist):
        self.view.insert(edit, 0, typelist)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class Opentracks(sublime_plugin.TextCommand):
    def input(self, args):
        return SongsInputHandler()

    def run(self, edit, tracklist):
        self.view.insert(edit, 0, tracklist)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class MoodlistInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        super(sublime_plugin.ListInputHandler, self).__init__()

    def name(self):
        return "typelist"

    def initial_text(self):
        return None

    def placeholder(self):
        return "Select a mood"

    def list_items(self):
        return getMoodlist()

    def confirm(self, value):
        global filter_type
        filter_type = value
        print(filter_type)

    def next_input(self, args):
        return SongsInputHandler()


class GenrelistInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        super(sublime_plugin.ListInputHandler, self).__init__()

    def name(self):
        return "typelist"

    def initial_text(self):
        return None

    def placeholder(self):
        return "Select a genre"

    def list_items(self):
        return getGenrelist()

    def confirm(self, value):
        global filter_type
        filter_type = value
        print("filter type select:",filter_type)

    def next_input(self, args):
        return SongsInputHandler()


class SongsInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self):
        super(sublime_plugin.ListInputHandler, self).__init__()

    def name(self):
        return "tracklist"

    def placeholder(self):
        return "Select a song"

    def list_items(self):
        global filter_type
        global recommendation_data
        # print("recommendation_data", recommendation_data,"\nlen of recommendation_data")
        
        if filter_type == "":
            return [("Songs not found. Please try another mood or genre","")]

        else:
            print("global filter_type received:",filter_type)
            # print("recommendation_data :",recommendation_data)
            if recommendation_data == []:
                print("first time called")
                tracks = getTracksBySelection(filter_type)
                recommendation_data = [filter_type, tracks]
                print("len recommendation_data", len(recommendation_data[1]))
                recommended_tracks = recommendation_data[1]
                # return recommended_tracks

            elif recommendation_data[0] == filter_type:
                print("same type")
                print("len recommendation_data", len(recommendation_data[1]))
                recommended_tracks = recommendation_data[1]
                # return recommendation_data[1]

            else:
            # elif recommendation_data[0] != filter_type:
                print("new filter type deteted")
                tracks = getTracksBySelection(filter_type)
                recommendation_data = [filter_type, tracks]
                print("len recommendation_data", len(recommendation_data[1]))
                recommended_tracks = recommendation_data[1]
                # return recommendation_data[1]

        if recommendation_data[1] and recommendation_data[1] == []:
            recommended_tracks = [("Songs not found. Please try another mood or genre","")]

        return recommended_tracks


    def confirm(self, value):
        global current_track
        global ACTIVE_DEVICE
        current_track = value
        print("current_track_id", current_track)
        if len(current_track) != 0: 

            playRecommendationTrack(ACTIVE_DEVICE.get('device_id'), current_track)
        else:
            pass
            # sublime.message_dialog("Can't play the track.")


def getMoodlist():
    global recommendation_data
    moodlist = ['Happy', 'Energetic', 'Danceable',
                'Instrumental', 'Familiar', 'Quiet music']
    return moodlist


def getGenrelist():
    global recommendation_data
    # global genre_list
    return genre_list


def getTracksBySelection(selectedtype):
    # global filter_type
    global recommendation_data

    recommendation_data = []
    recommendation_data = getRecommendationsTracks(selectedtype)
    if len(recommendation_data) == 0:
        return [("Songs not found. Please try another mood or genre","")]
    else:
        return recommendation_data


def moodChoice(argument):
    switcher = {"Happy": ["&min_valence=0.7&target_valence=1"],
                "Energetic": ["&min_energy=0.7&target_energy=1"],
                "Danceable": ["&min_danceability=0.7&target_danceability=1"],
                "Instrumental": ["&min_instrumentalness=0.0&target_instrumentalness=0.1"],
                "Familiar": [],
                "Quiet music": ["&max_loudness=-5&target_loudness=-10"],
                }

    return switcher.get(argument, "nothing")
 

def getSeedTracks():
    api = "/v1/me/tracks"
    tracklist = requestSpotify("GET", api)
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
        tracks = ('err',)
#             tracks = dict(zip(names,ids))
#     else:
#         tracks ={}

    return list(tracks)


def getRecommendationsTracks(value):
    api = "/v1/recommendations?"
    limit = 100
    market = ""
    min_popularity = 20
    target_popularity = 90
    seed_tracks = [j for i, j in dict(getSeedTracks()).items()]
    print("seed_tracks", seed_tracks)

    if len(seed_tracks) == 0:
        print("True")
        # seed_tracks == ''.join(["0vPZjeaM0cfbxZJntcD4iy"])
        final_seed_track = "0vPZjeaM0cfbxZJntcD4iy"
    else:
        if len(seed_tracks) > 5:
            print("More than 5")
            seed_tracks = ','.join(seed_tracks[:5])
            print("seed_tracks2", seed_tracks)
            final_seed_track = seed_tracks
        else:
            print("less than 5")
            seed_tracks = ','.join(seed_tracks)
            print("seed_tracks3", seed_tracks)
            final_seed_track = seed_tracks

    # final_seed_track = seed_tracks
    print(final_seed_track)

    if value in ['Happy', 'Energetic', 'Danceable', 'Instrumental', 'Familiar', 'Quiet music']:
        print("from moods")
        api = api+"limit="+str(limit)+"&min_popularity="+str(min_popularity)+"&target_popularity="+str(
            target_popularity)+"&seed_tracks=" + final_seed_track + "".join(moodChoice(value))
    else:
        print("from genres")
        api = api+"limit="+str(limit)+"&min_popularity="+str(
            min_popularity)+"&target_popularity="+str(target_popularity)+"&seed_genres=" + value.lower()

    print("final api", api)

    response = requestSpotify("GET", api)
    if response.status_code == 200:
        json_response = response.json()
        print("No. of tracks: ", len(json_response['tracks']))

        tracks = []
        for i, j in enumerate(json_response['tracks']):
            tracks.append((j['name'], j['id']))
    else:
        print(response.text)
        return []

    return tracks


def playRecommendationTrack(currentDeviceId, track_id):
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

        uris_list = []
        c = 0
        for i in recommendation_data[1]:
            uris_list.append("spotify:track:"+i[1])
            c = c+1
            if len(uris_list) == 50:
                break

        print("uris_list", uris_list)

        track_index = uris_list.index("spotify:track:" + track_id)
        print("track_index", track_index)
        '''
        {"uris": ["spotify:track:1rZwgdUwUYBqEphd4CXynL", "spotify:track:6Q8mqjuz8xqdoUjhZQDfY7",
                  "spotify:track:1aDklx1GaBqHFowCzz63wU", "spotify:track:4oaU0fMSg3n9kqOwmLPVhH",
                  "spotify:track:4WZizdGrBVSZCES0q2XDwu", "spotify:track:0l1i3nJ4aDMk0inxnvzYTz"],
                  "offset": {"position": 2}}
        '''
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
                    time.sleep(3)
                except Exception as e:
                    print("Launch Web Player Error", e)
            elif msg is 2:
                launchDesktopPlayer()
                time.sleep(3)
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

        data = {}
        try:
            print("track_id", track_id)
            # data = {"uris": ["spotify:track:" + track_id]}
            data = {"uris": uris_list, "offset": {
                "position": track_index}}  # {"position": 5}
            payload = json.dumps(data)
            print("payload", payload)
            print("currentDeviceId", currentDeviceId)

            api = "/v1/me/player/play?device_id=" + currentDeviceId
            plays = requestSpotify("PUT", api, payload)
            print(plays.text)
        except Exception as e:
            print("playThisSong", e)
    currentTrackInfo()

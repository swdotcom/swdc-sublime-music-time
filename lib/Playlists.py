import sublime_plugin
import sublime

# mock data
data = [
	{"id": 1, "name": "Running", "songs": ["Diane Young", "Ottoman", "This Life"]},
	{"id": 2, "name": "Working", "songs": ["How Long", "Jerusalem, New York, Berlin", "Harmony Hall"]},
	{"id": 3, "name": "Fun", "songs": ["A-Punk", "Step", "Sunflower"]}
]

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

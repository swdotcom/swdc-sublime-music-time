'''
 All available commands listed here 
'''
import sublime_plugin
import sublime
from threading import Thread, Timer, Event
# from ..Software import *
# from .SoftwareUtil import *
# from .SoftwareHttp import *
# from .SoftwareMusic import *
# from .Playlists import *
from .MusicControlManager import *
import requests
import webbrowser



# Report an issue on github
class SubmitIssueGithub(sublime_plugin.TextCommand):
    def run(self, edit):
        github_url = "https://github.com/swdotcom/music-time-sublime/issues"
        webbrowser.open(github_url)

# Submit feedback
class SubmitFeedback(sublime_plugin.TextCommand):
    def run(self, edit):
        mailto = "mailto:cody@software.com"
        webbrowser.open(mailto, new = 1)
        pass

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
            seeWebAnalytics()
        except Exception as E:
            print("SeeWebAnalytics:",E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


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
            playThisSong(ACTIVE_DEVICE.get('device_id'), songs_tree)
        else:
            playSongFromPlaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,songs_tree)
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
        if playlist_id == None:
            print('#'*10,'playlist_id == None SongInputHandler')
            playThisSong(ACTIVE_DEVICE.get('device_id'), current_song)
        else:
            print('#'*10,'else == None SongInputHandler')
            playSongFromPlaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,current_song)
        print("="*20,current_song)
        

# Play control in main menu
class PlaySong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            self.view.show_popup(myToolTip())
            playSong()
        except Exception as E:
            print("play",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Pause control in main menu
class PauseSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myToolTip())
            pauseSong()
        except Exception as E:
            print("pause",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Next control in main menu
class NextSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myToolTip())
            nextSong()
        except Exception as E:
            print("next",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Previous control in main menu
class PrevSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myToolTip())
            previousSong()
        except Exception as E:
            print("prev",E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Open Playlist
class OpenPlaylistsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        infoMsg = "Music Time: Playlists opened"
        print(infoMsg)
        return PlaylistInputHandler()

    def run(self, edit, playlists_tree):
        self.view.insert(edit, 0, playlists_tree)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Open Song list
class OpenSongsCommand(sublime_plugin.TextCommand):
    def input(self, args):
        return SongInputHandler()

    def run(self, edit, songs_tree):
        try:
            self.view.insert(edit, 0, songs_tree)
            if playlist_id == None:
                playThissong(ACTIVE_DEVICE.get('device_id'), songs_tree)
            elif playlist_id != None:
                playSongfromplaylist(ACTIVE_DEVICE.get('device_id'), playlist_id,songs_tree)
                print("+"*20,songs_tree)
            else:
                pass
                print("No song track found")
        except Exception as e:
            print("No song track found")

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


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


class DeviceStatus(sublime_plugin.TextCommand):
    def run(self, edit):
        # print("ConnectionStatus :",DEVICES) 
        self.view.show_popup(myToolTip(),) # max_width=300, max_height=1000
    def navigate(self,href):
        if href == 'show':
            pass
        else:
            pass

            
# Slack connectivtiy
class ConnectSlack(sublime_plugin.TextCommand):
    def run(self, edit):
        infoMsg = "Development in Progess."
        clickAction = sublime.ok_cancel_dialog(infoMsg, "OK")
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is False)


class DisconnectSlack(sublime_plugin.TextCommand):
    def run(self, edit):
        infoMsg = "Slack Disconnected"
        clickAction = sublime.ok_cancel_dialog(infoMsg, "OK")
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)
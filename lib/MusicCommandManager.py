'''
 All available commands listed here 
'''
import sublime_plugin
import sublime
import requests
from threading import Thread, Timer, Event
import webbrowser

# from ..Software import *
# from .SoftwareUtil import *
# from .SoftwareHttp import *
# from .SoftwareMusic import *
# from .MusicPlaylistProvider import *
from ..Constants import *
from .MusicControlManager import *


# Report an issue on github
class SubmitIssueGithub(sublime_plugin.TextCommand):
    def run(self, edit):
        webbrowser.open(ST3_GITHUB_URL)
        pass


# Submit feedback
class SubmitFeedback(sublime_plugin.TextCommand):
    def run(self, edit):
        webbrowser.open(FEEDBACK_MAIL_ID, new=1)
        pass


# open musictime.txt/html file
class LaunchMusicTimeMetrics(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            getMusicTimedashboard()
        except Exception as E:
            print("LaunchMusicTimeMetrics:", E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Launch web dashboard .../music


class SeeWebAnalytics(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            seeWebAnalytics()
        except Exception as E:
            print("SeeWebAnalytics:", E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Play control in main menu
class PlaySong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            self.view.show_popup(myToolTip())
            playSong()
        except Exception as E:
            print("play", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Pause control in main menu
class PauseSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            self.view.show_popup(myToolTip())
            pauseSong()
        except Exception as E:
            print("pause", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Next control in main menu
class NextSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            self.view.show_popup(myToolTip())
            nextSong()
        except Exception as E:
            print("next", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Previous control in main menu
class PrevSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            self.view.show_popup(myToolTip())
            previousSong()
        except Exception as E:
            print("prev", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Refresh playlist option in main menu
class RefreshPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            getUserPlaylists()
        except Exception as E:
            print("Music Time: RefreshPlaylist:", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class SortPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            getSortedUserPlaylists()
        except Exception as e:
            print("Music Time: SortPlaylist", e)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Generate AI playlist
class GenerateAIPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            generateAIplaylist()
        except Exception as E:
            print("RefreshPlaylist:", E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

# Refresh AI playlist


class RefreshAIPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            refreshAIplaylist()
        except Exception as E:
            print("RefreshPlaylist:", E)
        pass

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class ConnectionStatus(sublime_plugin.TextCommand):
    def run(self, edit):
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

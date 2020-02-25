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
from .MusicPlaylistProvider import *
from ..Constants import *
from .MusicControlManager import *
from .SlackConnectionManager import *



# Open Readme file 
class ReadmePleaseCommand(sublime_plugin.WindowCommand):
    def description(self):
        """Quick access to packages README."""

    def run(self):
        # Static values
        info = ['swdc-sublime-music-time', 'README.md',
                'Packages/swdc-sublime-music-time/README.md']
        sublime.active_window().run_command("open_file", {
            "file": "${packages}/%s/%s" % (info[0], info[1])})


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
            # self.view.show_popup(myToolTip())
            playSong()
        except Exception as E:
            print("play", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Pause control in main menu
class PauseSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myToolTip())
            pauseSong()
        except Exception as E:
            print("pause", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Next control in main menu
class NextSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myToolTip())
            nextSong()
        except Exception as E:
            print("next", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Previous control in main menu
class PrevSong(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # self.view.show_popup(myToolTip())
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
            checkAIPlaylistid()
            message_dialog = sublime.message_dialog("Playlists Refreshed !")
        except Exception as E:
            print("Music Time: RefreshPlaylist:", E)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class SortAz(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            sortPlaylistByAz()
            message_dialog = sublime.message_dialog("Playlists Sorted by A-Z !")
        except Exception as e:
            print("Music Time: sortPlaylistByAz", e)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)

class SortLatest(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            sortPlaylistByLatest()
            message_dialog = sublime.message_dialog("Playlists Sorted by Latest !")
        except Exception as e:
            print("Music Time: sortPlaylistbyLatest", e)

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


class RefreshAiPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        print("Music Time: Refreshing My AI Playlist !")
        try:
            refreshMyAIPlaylist()
            getUserPlaylists()
        except Exception as E:
            print("RefreshPlaylist:", E)
        pass

    def is_enabled(self):
        logged_on = getValue("logged_on", True)
        # ai_playlist = getValue("ai_playlist", False)
        try:
            if logged_on is False:
                return False
            else:
                return (getValue("ai_playlist", True) is True)
        except Exception as e:
            print("Refresh AI",e)
            # if logged_on is True and ai_playlist is False:
            #     return False
            # elif logged_on is True and ai_playlist is True:
            #     return True
            # else:
            #     return False


# Command to re-enable Console message
class GenerateAiPlaylist(sublime_plugin.TextCommand):
    def run(self, edit):
        print("Music Time: Generating My AI Playlist !")
        try:
            generateMyAIPlaylist()
            getUserPlaylists()
        except Exception as E:
            print("generateMyAIPlaylist:", E)
        setValue("ai_playlist", True)

    def is_enabled(self):
        logged_on = getValue("logged_on", True)
        # ai_playlist = getValue("ai_playlist", False)
        # print("logged_on",logged_on)
        # print("ai_playlist",ai_playlist)
        try:
            if logged_on is False:
                return False
            else:
                return (getValue("ai_playlist", True) is False)
        except Exception as e:
            print("Generate ai",e)
            # return (getValue("logged_on", True) is True)
            # if logged_on is True and ai_playlist is True:
            #     return False
            # else:
            #     return True

        # if logged_on is True:
        #     return (getValue("ai_playlist", True) is False)


'''
    ai_playlist = getValue("ai_playlist", False)
    if logged_on is True:
        if ai_playlist is True:
            return True
'''

# Generate AI playlist
# class GenerateAIPlaylist(sublime_plugin.TextCommand):
#     def run(self, edit):
#         player = sublime.ok_cancel_dialog("Please open Spotify player", "Ok")
        # try:
        #     generateMyAIPlaylist()
        #     getUserPlaylists()
        # except Exception as E:
        #     print("generateMyAIPlaylist:", E)
        # pass
    
    # def is_enabled(self):
        # return True
            # return (getValue("logged_on", True) is True)
    #     # return (getValue("ai_playlist", True) is False)
    #     logged_on = getValue("logged_on", True)
    #     ai_playlist = getValue("ai_playlist", False)

    #     if logged_on is True and ai_playlist is False:
    #         return True
    #     elif logged_on is True and ai_playlist is True:
    #         return False
    #     elif logged_on is False:
    #         return False 


# Refresh AI playlist
# class RefreshAIPlaylist(sublime_plugin.TextCommand):
    # def run(self, edit):
        # player = sublime.ok_cancel_dialog("Please open Spotify player", "Ok")
        # try:
        #     refreshMyAIPlaylist()
        #     getUserPlaylists()

        # except Exception as E:
        #     print("RefreshPlaylist:", E)
        # pass

    # def is_enabled(self):
    #     pass
    #     return (getValue("ai_playlist", True) is True)
    #     # logged_on = getValue("logged_on", True)
    #     # ai_playlist = getValue("ai_playlist", False)

    #     # if logged_on is True and ai_playlist is False:
    #     #     return False
    #     # elif logged_on is True and ai_playlist is True:
    #     #     return True
    #     # elif logged_on is False:
    #     #     return False 


class ConnectionStatus(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.show_popup(myToolTip(),) # max_width=300, max_height=1000
    
    def navigate(self,href):
        if href == 'show':
            pass
        else:
            pass
            
    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Slack connectivtiy
class ConnectSlack(sublime_plugin.TextCommand):
    def run(self, edit):
        launchConnectSlack()
        getSlackTokens()
        # infoMsg = "Development in Progess."
        # clickAction = sublime.ok_cancel_dialog(infoMsg, "OK")
        pass

    def is_enabled(self):
        return (getValue("slack_loggedon", True) is False)


class DisconnectSlack(sublime_plugin.TextCommand):
    def run(self, edit):
        infoMsg = "Slack Disconnected"
        clickAction = sublime.ok_cancel_dialog(infoMsg, "OK")
        pass

    def is_enabled(self):
        return (getValue("slack_loggedon", True) is True)




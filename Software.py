# Copyright (c) 2019 by Software.com

import datetime
import json
import os
from package_control import events
from queue import Queue
import sublime_plugin
import sublime
import subprocess
import sys
sys.path.append("..")
import time
from threading import Thread, Timer, Event
import webbrowser

from .Constants import *
from .lib.MusicControlManager import *
from .lib.MusicCommandManager import *
from .lib.MusicPlaylistProvider import *
from .lib.SoftwareHttp import *
from .lib.SoftwareUtil import *
from .lib.SoftwareMusic import *
from .lib.SoftwareOffline import *
from .lib.SoftwareSettings import *
from .lib.SocialShareManager import *
from .lib.PlayerManager import *
from .lib.MusicRecommendation import *

ACCESS_TOKEN = ''
REFRESH_TOKEN = ''
EMAIL = ''
user_type = ''
spotifyUserId = ''
slack = False


# payload trigger to store it for later.
def post_json(json_data):
    # save the data to the offline data file
    storePayload(json_data)
    # save the kpm data for music sessions
    storeKpmDataForMusic(json_data)

    PluginData.reset_source_data()


# Background thread used to send data every minute.
class BackgroundWorker():
    def __init__(self, threads_count, target_func):
        self.queue = Queue(maxsize=0)
        self.target_func = target_func
        self.threads = []

        for i in range(threads_count):
            thread = Thread(target=self.worker, daemon=True)
            thread.start()
            self.threads.append(thread)

    def worker(self):
        while True:
            self.target_func(self.queue.get())
            self.queue.task_done()

# kpm payload data structure
class PluginData():
    __slots__ = ('source', 'keystrokes', 'start', 'local_start',
                 'project', 'pluginId', 'version', 'os', 'timezone')
    # the 1st arg is the thread count, the 2nd is the callback target function
    background_worker = BackgroundWorker(1, post_json)
    active_datas = {}
    line_counts = {}
    send_timer = None

    def __init__(self, project):
        self.source = {}
        self.start = 0
        self.local_start = 0
        self.timezone = ''
        self.keystrokes = 0
        self.project = project
        self.pluginId = PLUGIN_ID
        self.version = VERSION
        self.timezone = getTimezone()
        self.os = getOs()

    def json(self):
        # make sure all file end times are set
        dict_data = {key: getattr(self, key, None)
                     for key in self.__slots__}

        return json.dumps(dict_data)

    # send the kpm info
    def send(self):
        # check if it has data
        if PluginData.background_worker and self.hasData():
            PluginData.endUnendedFileEndTimes()
            PluginData.background_worker.queue.put(self.json())

    # check if we have data
    def hasData(self):
        if (self.keystrokes > 0):
            return True
        for fileName in self.source:
            fileInfo = self.source[fileName]
            if (fileInfo.get("close", 0) > 0 or
                fileInfo.get("open", 0) > 0 or
                fileInfo.get("paste", 0) > 0 or
                fileInfo.get("delete", 0) > 0 or
                fileInfo.get("add", 0) > 0 or
                    fileInfo.get("netkeys", 0) > 0):
                return True
        return False

    @staticmethod
    def reset_source_data():
        PluginData.send_timer = None

        for dir in PluginData.active_datas:
            keystrokeCountObj = PluginData.active_datas[dir]

            # get the lines so we can add that back
            for fileName in keystrokeCountObj.source:
                fileInfo = keystrokeCountObj.source[fileName]
                # add the lines for this file so we can re-use again
                PluginData.line_counts[fileName] = fileInfo.get("lines", 0)

            if keystrokeCountObj is not None:
                keystrokeCountObj.source = {}
                keystrokeCountObj.keystrokes = 0
                keystrokeCountObj.project['identifier'] = None
                keystrokeCountObj.timezone = getTimezone()

    @staticmethod
    def create_empty_payload(fileName, projectName):
        project = {}
        project['directory'] = projectName
        project['name'] = projectName
        return_data = PluginData(project)
        PluginData.active_datas[project['directory']] = return_data
        PluginData.get_file_info_and_initialize_if_none(return_data, fileName)
        return return_data

    @staticmethod
    def get_active_data(view):
        return_data = None
        if view is None or view.window() is None:
            return return_data

        fileName = view.file_name()
        if (fileName is None):
            fileName = "Untitled"

        sublime_variables = view.window().extract_variables()
        project = {}

        # set it to none as a default
        projectFolder = 'Unnamed'

        # set the project folder
        if 'folder' in sublime_variables:
            projectFolder = sublime_variables['folder']
        elif 'file_path' in sublime_variables:
            projectFolder = sublime_variables['file_path']

        # if we have a valid project folder, set the project name from it
        if projectFolder != 'Unnamed':
            project['directory'] = projectFolder
            if 'project_name' in sublime_variables:
                project['name'] = sublime_variables['project_name']
            else:
                # use last file name in the folder as the project name
                projectNameIdx = projectFolder.rfind('/')
                if projectNameIdx > -1:
                    projectName = projectFolder[projectNameIdx + 1:]
                    project['name'] = projectName
        else:
            project['directory'] = 'Unnamed'

        old_active_data = None
        if project['directory'] in PluginData.active_datas:
            old_active_data = PluginData.active_datas[project['directory']]

        if old_active_data is None:
            new_active_data = PluginData(project)

            PluginData.active_datas[project['directory']] = new_active_data
            return_data = new_active_data
        else:
            return_data = old_active_data

        fileInfoData = PluginData.get_file_info_and_initialize_if_none(
            return_data, fileName)

        # This activates the 60 second timer. The callback
        # in the Timer sends the data
        if (PluginData.send_timer is None):
            PluginData.send_timer = Timer(DEFAULT_DURATION, return_data.send)
            PluginData.send_timer.start()

        return return_data

    # ...
    @staticmethod
    def get_existing_file_info(fileName):
        fileInfoData = None

        now = round(time.time())
        local_start = getLocalStart()
        # Get the FileInfo object within the KeystrokesCount object
        # based on the specified fileName.
        for dir in PluginData.active_datas:
            keystrokeCountObj = PluginData.active_datas[dir]
            if keystrokeCountObj is not None:
                hasExistingKeystrokeObj = True
                # we have a keystroke count object, get the fileInfo
                if keystrokeCountObj.source is not None and fileName in keystrokeCountObj.source:
                    # set the fileInfoData we'll return the calling def
                    fileInfoData = keystrokeCountObj.source[fileName]
                else:
                    # end the other files end times
                    for fileName in keystrokeCountObj.source:
                        fileInfo = keystrokeCountObj.source[fileName]
                        fileInfo["end"] = now
                        fileInfo["local_end"] = local_start

        return fileInfoData

    # ......
    @staticmethod
    def endUnendedFileEndTimes():
        now = round(time.time())
        local_start = getLocalStart()

        for dir in PluginData.active_datas:
            keystrokeCountObj = PluginData.active_datas[dir]
            if keystrokeCountObj is not None and keystrokeCountObj.source is not None:
                for fileName in keystrokeCountObj.source:
                    fileInfo = keystrokeCountObj.source[fileName]
                    if (fileInfo.get("end", 0) == 0):
                        fileInfo["end"] = now
                        fileInfo["local_end"] = local_start

    @staticmethod
    def send_all_datas():
        for dir in PluginData.active_datas:
            PluginData.active_datas[dir].send()

    @staticmethod
    def update_global_keystroke_count():
        if (len(PluginData.active_datas) > 0):
            for dir in PluginData.active_datas:
                keystrokeCountObj = PluginData.active_datas[dir]
                # print("keystrokeCountObj: %s" % keystrokeCountObj.json())
                updateActiveData(keystrokeCountObj.json())
                break
        else:
            updateActiveData(None)

    # ........
    @staticmethod
    def initialize_file_info(keystrokeCount, fileName):
        if keystrokeCount is None:
            return

        if fileName is None or fileName == '':
            fileName = 'Untitled'

        # create the new FileInfo, which will contain a dictionary
        # of fileName and it's metrics
        fileInfoData = PluginData.get_existing_file_info(fileName)

        now = round(time.time())
        local_start = getLocalStart()

        if keystrokeCount.start == 0:
            keystrokeCount.start = now
            keystrokeCount.local_start = local_start
            keystrokeCount.timezone = getTimezone()

        # "add" = additive keystrokes
        # "netkeys" = add - delete
        # "keys" = add + delete
        # "delete" = delete keystrokes
        if fileInfoData is None:
            fileInfoData = {}
            fileInfoData['paste'] = 0
            fileInfoData['open'] = 0
            fileInfoData['close'] = 0
            fileInfoData['length'] = 0
            fileInfoData['delete'] = 0
            fileInfoData['netkeys'] = 0
            fileInfoData['add'] = 0
            fileInfoData['lines'] = -1
            fileInfoData['linesAdded'] = 0
            fileInfoData['linesRemoved'] = 0
            fileInfoData['syntax'] = ""
            fileInfoData['start'] = now
            fileInfoData['local_start'] = local_start
            fileInfoData['end'] = 0
            fileInfoData['local_end'] = 0
            keystrokeCount.source[fileName] = fileInfoData
        else:
            # update the end and local_end to zero since the file is still getting modified
            fileInfoData['end'] = 0
            fileInfoData['local_end'] = 0

    @staticmethod
    def get_file_info_and_initialize_if_none(keystrokeCount, fileName):
        fileInfoData = PluginData.get_existing_file_info(fileName)
        if fileInfoData is None:
            PluginData.initialize_file_info(keystrokeCount, fileName)
            fileInfoData = PluginData.get_existing_file_info(fileName)

        return fileInfoData

    @staticmethod
    def send_initial_payload():
        fileName = "Untitled"
        active_data = PluginData.create_empty_payload(fileName, "Unnamed")
        PluginData.get_file_info_and_initialize_if_none(active_data, fileName)
        fileInfoData = PluginData.get_existing_file_info(fileName)
        fileInfoData['add'] = 1
        active_data.keystrokes = 1
        PluginData.send_all_datas()

# connect spotify menu
class ConnectSpotify(sublime_plugin.TextCommand):
    def run(self, edit):
        # let the launch spotify logic lazily check if the user has connected or not
        launchSpotifyLoginUrl()

    def is_enabled(self):
        return (getValue("logged_on", True) is False)


# Disconnect spotify
class DisconnectSpotify(sublime_plugin.TextCommand):
    def run(self, edit):
        # disconnect = sublime.yes_no_cancel_dialog("Do want to Disconnect Spotify ?", "Yes", "No")
        # if disconnect == "yes":
        disconnectSpotify()
        setValue("logged_on", False)
        showStatus("Connect Spotify")
        message_dialog = sublime.message_dialog("Disconnected Spotify !")
        showStatus("Connect Spotify")

    def is_enabled(self):
        return (getValue("logged_on", True) is True)


# Runs once instance per view (i.e. tab, or single file window)
class EventListener(sublime_plugin.EventListener):
    def on_load_async(self, view):
        fileName = view.file_name()
        if (fileName is None):
            fileName = "Untitled"

        active_data = PluginData.get_active_data(view)

        # get the file info to increment the open metric
        fileInfoData = PluginData.get_file_info_and_initialize_if_none(
            active_data, fileName)
        if fileInfoData is None:
            return

        fileSize = view.size()
        fileInfoData['length'] = fileSize

        # get the number of lines
        lines = view.rowcol(fileSize)[0] + 1
        fileInfoData['lines'] = lines

        # we have the fileinfo, update the metric
        fileInfoData['open'] += 1
        log('Code Time: opened file %s' % fileName)

        # show last status message
        redispayStatus()

    def on_close(self, view):
        fileName = view.file_name()
        if (fileName is None):
            fileName = "Untitled"

        active_data = PluginData.get_active_data(view)

        # get the file info to increment the close metric
        fileInfoData = PluginData.get_file_info_and_initialize_if_none(
            active_data, fileName)
        if fileInfoData is None:
            return

        fileSize = view.size()
        fileInfoData['length'] = fileSize

        # get the number of lines
        lines = view.rowcol(fileSize)[0] + 1
        fileInfoData['lines'] = lines

        # we have the fileInfo, update the metric
        fileInfoData['close'] += 1
        log('Code Time: closed file %s' % fileName)

        # show last status message
        redispayStatus()

    def on_modified_async(self, view):
        global PROJECT_DIR
        # get active data will create the file info if it doesn't exist
        active_data = PluginData.get_active_data(view)
        if active_data is None:
            return

        # add the count for the file
        fileName = view.file_name()

        fileInfoData = {}

        if (fileName is None):
            fileName = "Untitled"

        fileInfoData = PluginData.get_file_info_and_initialize_if_none(
            active_data, fileName)

        # If file is untitled then log that msg and set file open metrics to 1
        if fileName == "Untitled":
            # log(plugin_name + ": opened file untitled")
            fileInfoData['open'] = 1
        else:
            pass

        if fileInfoData is None:
            return

        fileSize = view.size()

        #lines = 0
        # rowcol gives 0-based line number, need to add one as on editor lines starts from 1
        lines = view.rowcol(fileSize)[0] + 1

        prevLines = fileInfoData['lines']
        if (prevLines == 0):

            if (PluginData.line_counts.get(fileName) is None):
                PluginData.line_counts[fileName] = prevLines

            prevLines = PluginData.line_counts[fileName]
        elif (prevLines > 0):
            fileInfoData['lines'] = prevLines

        lineDiff = 0
        if (prevLines > 0):
            lineDiff = lines - prevLines
            if (lineDiff > 0):
                fileInfoData['linesAdded'] += lineDiff
                log('Code Time: linesAdded incremented')
            elif (lineDiff < 0):
                fileInfoData['linesRemoved'] += abs(lineDiff)
                log('Code Time: linesRemoved incremented')

        fileInfoData['lines'] = lines

        # subtract the current size of the file from what we had before
        # we'll know whether it's a delete, copy+paste, or kpm.
        currLen = fileInfoData['length']

        charCountDiff = 0

        if currLen > 0 or currLen == 0:
            # currLen > 0 only worked for existing file, currlen==0 will work for new file
            charCountDiff = fileSize - currLen

        if (not fileInfoData["syntax"]):
            syntax = view.settings().get('syntax')
            # get the last occurance of the "/" then get the 1st occurance of the .sublime-syntax
            # [language].sublime-syntax
            # Packages/Python/Python.sublime-syntax
            syntax = syntax[syntax.rfind('/') + 1:-len(".sublime-syntax")]
            if (syntax):
                fileInfoData["syntax"] = syntax

        PROJECT_DIR = active_data.project['directory']

        # getResourceInfo is a SoftwareUtil function
        if (active_data.project.get("identifier") is None):
            resourceInfoDict = getResourceInfo(PROJECT_DIR)
            if (resourceInfoDict.get("identifier") is not None):
                active_data.project['identifier'] = resourceInfoDict['identifier']
                active_data.project['resource'] = resourceInfoDict

        fileInfoData['length'] = fileSize

        if lineDiff == 0 and charCountDiff > 8:
            fileInfoData['paste'] += 1
            log('Code Time: pasted incremented')
        elif lineDiff == 0 and charCountDiff == -1:
            fileInfoData['delete'] += 1
            log('Code Time: delete incremented')
        elif lineDiff == 0 and charCountDiff == 1:
            fileInfoData['add'] += 1
            log('Code Time: KPM incremented')

        # increment the overall count
        if (charCountDiff != 0 or lineDiff != 0):
            active_data.keystrokes += 1

        # update the netkeys and the keys
        # "netkeys" = add - delete
        fileInfoData['netkeys'] = fileInfoData['add'] - fileInfoData['delete']

        PluginData.update_global_keystroke_count()

#
# Iniates the plugin tasks once the it's loaded into Sublime.
def plugin_loaded():
    t = Timer(1, initializeUser)
    t.start()


def initializeUser():
    # fileExists = softwareSessionFileExists()
    jwt = getItem("jwt")
    initializedAnonUser = False
    if (jwt is None):
        # create the anon user
        jwt = createAnonymousUser()
        if (jwt is not None):
            initializedAnonUser = True
    initializePlugin(initializedAnonUser)


def initializePlugin(initializedAnonUser):
    PACKAGE_NAME = __name__.split('.')[0]
    log('Music Time: Loaded v%s of package name: %s' % (VERSION, PACKAGE_NAME))
    if (isMusicTime() == False):
        showStatus("Code Time")
    else:
        showStatus("Music Time")

    setItem("sublime_lastUpdateTime", None)

    checkUserState()

    # sendOfflineDataTimer = Timer(10, sendOfflineData)
    # sendOfflineDataTimer.start()

    gatherMusicTimer = Timer(10, gatherMusicInfo)
    gatherMusicTimer.start()


def plugin_unloaded():
    # clean up the background worker
    PluginData.background_worker.queue.join()


def sendInitializedHeartbeat():
    sendHeartbeat("INITIALIZED")

# gather the git commits, repo members, heatbeat ping


# def showOfflinePrompt():
#     infoMsg = "Our service is temporarily unavailable. We will try to reconnect again in 10 minutes. Your status bar will not update at this time."
#     sublime.message_dialog(infoMsg)


def checkUserState():
    global spotifyUserId
    global slack
    try:
        api = "/users/plugin/state"
        resp_data = requestIt("GET", api, None, getItem("jwt"))
        # print("plugin state response: %s" % resp_data)
        if resp_data is not None and resp_data['state'] == "OK":

            for i in range(len(resp_data['user']['auths'])):
                if resp_data['user']['auths'][i]['type'] == "spotify":
                    spotifyUserId = resp_data['user']['auths'][i]['authId']

                if resp_data['user']['auths'][i]['type'] == "slack":
                    setValue("slack_logged_on", True)
                    slack = True
                else:
                    setValue("slack_logged_on", False)
            
            print("spotify user id: %s" % spotifyUserId)
            
            setValue("logged_on", True) 
            showStatus("Spotify Connected")
            # getActiveDeviceInfo()
            # getUserPlaylists()
            try:
                checkAIPlaylistid()
            except Exception as e:
                print("checkAIPlaylistid",e)
                pass
            getUserPlaylists()
            autoRefreshAccessToken()
            # refreshStatusBar()
            print('_'*40)
            print(' * logged_on: True', '\n * Email:', resp_data['email'],"\n * Slack:",slack)
            print('_'*40)
        else:
            setValue("logged_on", False)
            print('logged_on:False')
    except Exception as e:
        print('checkUserState',e)
        print('logged_on:False')
        setValue("logged_on", False)
        pass



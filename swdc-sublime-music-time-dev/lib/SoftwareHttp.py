
# Copyright (c) 2018 by Software.com

import http
import json
import sys
# sys.path.append('../')
import sublime_plugin
import sublime

from ..Software import *
from .SoftwareSettings import *
from .SoftwareUtil import *
# from SoftwareUtil import isMusicTime
# from .MusicCommandManager import *
# from .MusicControlManager import *


USER_AGENT = 'Music Time Sublime Plugin'
lastMsg = ''
windowView = None
plugin = ''


def httpLog(message):
    if (getValue("software_logging_on", True)):
        pass
        # print(message)


def redispayStatus():
    global lastMsg
    showStatus(lastMsg)


def showStatus(msg):
    global lastMsg
    try:
        active_window = sublime.active_window()

        showStatusVal = getValue("show_code_time_status", True)

        if (showStatusVal is False):
            msg = "⏱"
        elif (isMusicTime is True):
            if getValue("logged_on", True) is True:
                msg = "Spotify Connected"
        else:
            pass
            # currenttrackinfo()

        if (active_window is not None):
            for view in active_window.views():
                if (view is not None):
                    view.set_status('software.com', msg)
    except RuntimeError:
        httpLog(msg)


def isResponseOk(response):
    if (response is not None and int(response.status) < 300):
        return True
    return False


def isUnauthenticated(response):
    if (response is not None and int(response.status) == 401):
        return True
    return False

# send the request.


def requestIt(method, api, payload, jwt):

    api_endpoint = getValue("software_api_endpoint", "api.software.com")
    telemetry = getValue("software_telemetry_on", True)

    if (telemetry is False):
        # httpLog("Code Time: telemetry is currently paused. To see your coding data in Software.com, enable software telemetry.")
        return None

    # try to update kpm data.
    try:
        connection = None
        # create the connection
        if ('localhost' in api_endpoint):
            connection = http.client.HTTPConnection(api_endpoint)
        else:
            connection = http.client.HTTPSConnection(api_endpoint)

        headers = {'Content-Type': 'application/json',
                   'User-Agent': USER_AGENT}

        if (jwt is not None):
            headers['Authorization'] = jwt
        elif (method is 'POST' and jwt is None):
            httpLog(
                "Code Time: no auth token available to post kpm data: %s" % payload)
            return None

        # make the request
        if (payload is None):
            payload = {}
            httpLog(
                "Music Time: Requesting [" + method + ": " + api_endpoint + "" + api + "]")
        else:
            httpLog("Music Time: Sending [" + method + ": " + api_endpoint + "" +
                    api + ", headers: " + json.dumps(headers) + "] payload: %s" % payload)

        # send the request
        connection.request(method, api, payload, headers)

        response = connection.getresponse()
        # httpLog("Code Time: " + api_endpoint + "" + api + " Response (%d)" % response.status)
        return response
    except Exception as ex:
        print("Music Time: " + api + " Network error: %s" % ex)
        return None


def isMusicTime():
    plugin = getValue("plugin", "music-time")
    # print(">><<",plugin)
    # plugin = getItem("plugin")
    if plugin == "music-time":
        return True
    else:
        return False

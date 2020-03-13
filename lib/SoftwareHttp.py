# Copyright (c) 2018 by Software.com

import http
import json
import sys
import sublime_plugin
import sublime

from ..Constants import *
from ..Software import *
from .SoftwareSettings import *
from .SoftwareUtil import *


lastMsg = ''
windowView = None
plugin = ''


def httpLog(message):
    if (getValue("software_logging_on", True)):
        print(message)
        pass


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

def refreshSpotifyAccessToken(CLIENT_ID, CLIENT_SECRET):
    payload = {}
    obj = {}

    spotify_refresh_token = getItem("spotify_refresh_token")
    payload['grant_type'] = 'refresh_token'
    payload['refresh_token'] = spotify_refresh_token

    auth_header = base64.b64encode(str(CLIENT_ID + ':' + CLIENT_SECRET).encode('ascii'))
    headers = {'Content-Type': 'application/json','Authorization': 'Basic %s' % auth_header.decode('ascii')}
    api = "https://accounts.spotify.com/api/token"

    return requestSpotify("POST", api, payload)

def requestSpotify(method, api, payload):
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    try:
        connection = http.client.HTTPSConnection(SPOTIFY_API)
        if (payload is None):
            payload = {}
        connection.request(method, api, payload, headers)
        response = connection.getresponse()
        httpLog("Spotify request: " + SPOTIFY_API + "" + api + " Response (%d)" % response.status)
        return json.loads(response.read().decode('utf-8'))
    except Exception as ex:
        print("Music Time: " + api + " Network error: %s" % ex)
        return None

def requestSlack(method, api, payload):
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                     "Authorization": "Bearer {}".format(getItem("slack_access_token"))}
    try:
        connection = http.client.HTTPSConnection(SLACK_API)
        if (payload is None):
            payload = {}
        connection.request(method, api, payload, headers)
        response = connection.getresponse()
        httpLog("Slack request: " + SLACK_API + "" + api + " Response (%d)" % response.status)
        return json.loads(response.read().decode('utf-8'))
    except Exception as ex:
        print("Music Time: " + api + " Network error: %s" % ex)
        return None

# send the request.
def requestIt(method, api, payload, returnJson):

    api_endpoint = getValue("software_api_endpoint", SOFTWARE_API)
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

        jwt = getItem("jwt")
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
        if (returnJson is None or returnJson is True):
            # httpLog("Code Time: " + api_endpoint + "" + api + " Response (%d)" % response.status)
            return json.loads(response.read().decode('utf-8'))
        else:
            return response.read().decode('utf-8')
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

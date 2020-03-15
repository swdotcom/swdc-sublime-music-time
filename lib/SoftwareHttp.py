# Copyright (c) 2018 by Software.com

import http
import json
import sys
import sublime_plugin
import sublime
import six
import base64
import requests

from ..Constants import *
from ..Software import *
from .SoftwareSettings import *


lastMsg = ''
windowView = None
plugin = ''
latest_spotify_access_token = None
latest_spotify_refresh_token = None
client_id = ''
client_secret = ''


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

def refreshSpotifyAccessToken(spotify_client_id, spotify_client_secret, spotify_refresh_token):
    global client_id
    global client_secret
    global latest_spotify_refresh_token

    if (client_id is None or latest_spotify_refresh_token is None):
        client_id = spotify_client_id
        client_secret = spotify_client_secret
        latest_spotify_refresh_token = spotify_refresh_token

    payload = {}
    payload['grant_type'] = 'refresh_token'
    payload['refresh_token'] = spotify_refresh_token
    refresh_token_url = "https://accounts.spotify.com/api/token"

    auth_header = base64.b64encode(six.text_type(
        client_id + ':' + client_secret).encode('ascii'))
    headers = {'Authorization': 'Basic %s' % auth_header.decode('ascii')}
    response = requests.post(
        refresh_token_url, data=payload, headers=headers)

    print("refreshSpotifyAccessToken: response code: %d" % response.status_code)

    if response.status_code != 200:
        print("refreshSpotifyAccessToken: couldn't refresh token: code: %d reason: %s" % (response.status_code, response.reason))
        return None

    token_info = response.json()
    token_info["status"] = response.status_code
    latest_spotify_access_token = token_info["access_token"]
    print("refreshSpotifyAccessToken: refresh token info: %s" % token_info)

    return token_info


def requestSpotify(method, api, payload, spotify_access_token, tries = 0):
    global latest_spotify_access_token
    global client_id
    global client_secret
    global latest_spotify_refresh_token

    if (latest_spotify_access_token is None):
        latest_spotify_access_token = spotify_access_token

    headers = {"Authorization": "Bearer {}".format(latest_spotify_access_token)}
    try:
        api = SPOTIFY_API + "" + api
        resp = executeRequest(method, api, headers, payload)

        print("requestSpotify: reponse for api %s %s" % (api, resp.status_code))

        if (resp.status_code == 429 and tries < 3):
            time.sleep(1)
            tries += 1
            print("requestSpotify: Retry spotify api requst: %s" % api)
            return requestSpotify(method, api, payload, latest_spotify_access_token, tries)
        elif (resp.status_code == 401 and tries < 1):
            # spotify result: {'status': 401, 'error': {'status': 401, 'message': 'Invalid access token'}}
            # refresh the token then call again
            print("requestSpotify: Trying to refresh the access token")
            tries += 1
            refreshSpotifyAccessToken(client_id, client_secret, latest_spotify_refresh_token)
            requestSpotify(method, api, payload, spotify_access_token, tries)

        if (resp is not None):
            jsonData = resp.json()
            jsonData['status'] = resp.status_code
            
            return jsonData
        return resp
    except Exception as ex:
        print("requestSpotify: request error for " + api + ": %s" % ex)
        return None

def requestSlack(method, api, payload, slack_access_token):
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                     "Authorization": "Bearer {}".format(slack_access_token)}
    try:
        api = SLACK_API + "" + api
        resp = executeRequest(method, api, headers, payload)
        if (resp is not None):
            jsonData = resp.json()
            jsonData['status'] = resp.status_code
            print("Slack reponse for api %s %s" % (api, jsonData["status"]))
            return jsonData
        return resp
    except Exception as ex:
        print("Music Time: " + api + " Network error: %s" % ex)
        return None

# send the request.
def requestIt(method, api, payload, jwt, returnJson = True, tries = 0):

    api_endpoint = getValue("software_api_endpoint", SOFTWARE_API)
    telemetry = getValue("software_telemetry_on", True)

    if (telemetry is False):
        # httpLog("Code Time: telemetry is currently paused. To see your coding data in Software.com, enable software telemetry.")
        return None

    # try to update kpm data.
    try:
        headers = {'content-type': 'application/json', 'User-Agent': USER_AGENT}
        if (jwt is not None):
            headers['Authorization'] = jwt

        api = SOFTWARE_API + "" + api
        resp = executeRequest(method, api, headers, payload)

        if (returnJson is None or returnJson is True):
            jsonData = resp.json()
            jsonData['status'] = resp.status_code
            print("APP reponse for api %s %s" % (api, jsonData["status"]))
            return jsonData
        else:
            jsonText = resp.text
            print("app api text respons: %s" % jsonText)
            return jsonText
    except Exception as ex:
        print("Music Time: " + api + " Network error: %s" % ex)
        return None

def executeRequest(method, api, headers, payload):
    try:
        resp = None
        if (method.lower() == "get"):
            resp = requests.get(api, headers=headers)
        elif (method.lower() == "post"):
            resp = requests.post(api, headers=headers, data=payload)
        elif (method.lower() == "put"):
            resp = requests.put(api, headers=headers, data=payload)
        elif (method.lower() == "delete"):
            resp = requests.delete(api, headers=headers)

        return resp
    except Exception as ex:
        print("Music Time: " + api + " Network error: %s" % ex)
        return None

def isMusicTime():
    plugin = getValue("plugin", "music-time")
    # print(">><<",plugin)
    if plugin == "music-time":
        return True
    else:
        return False

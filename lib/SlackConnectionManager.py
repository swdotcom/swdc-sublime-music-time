
import urllib.parse
import webbrowser
import requests

from ..Constants import *
from .SoftwareUtil import *
from .SoftwareSettings import *


def launchConnectSlack():
    jwt = getItem("jwt")
    encodedJwt = urllib.parse.quote(jwt)
    qryStr = "integrate=slack&plugin=musictime&token=" + encodedJwt
    endpoint = "https://api.software.com/auth/slack?"+qryStr
    print("encodedJwt:",encodedJwt,"\nqryStr:",qryStr,"\nendpoint_url:",endpoint)
    webbrowser.open(endpoint)
    refetchUserStatusLazily(10)

# def connectSlack(jwt):
#     encodedJwt = urllib.parse.quote(jwt)
#     qryStr = "integrate=slack&plugin=musictime&token=" + encodedJwt
#     endpoint = "https://api.software.com/auth/slack?"+qryStr
#     webbrowser.open(endpoint)
    
    
# connectSlack(jwt)
def getSlackTokens():

    headers0 = {'content-type': 'application/json', 'Authorization': jwt}
    getauth0 = requests.get('https://api.software.com/users/plugin/state', headers=headers0)
    if getauth0.status_code >= 200: 
        authinfo = getauth0.json()

        for i in range(len(authinfo['user']['auths'])):
            if authinfo['user']['auths'][i]['type'] == "slack":
                print("slack_auths: ",authinfo['user']['auths'][i])
                slack_access_token = authinfo['user']['auths'][i]['access_token']
                setValue("slack_logged_on", True)
                setItem("slack_access_token",slack_access_token)
                print("Music Time: Got slack access token !")
            else:
                setValue("slack_logged_on", False)
                print("Music Time: Unable to connect slack ")
    else:
        print("Music Time: Unable to connect")
        infoMsg = "Please try after some time unable to connect slack at this moment."
        clickAction = sublime.message_dialog(infoMsg)

# print(slack_access_token)

# def checkSlackConnection(resp_data):
    
#     for i in range(len(resp_data['user']['auths'])):
#         if resp_data['user']['auths'][i]['type'] == "slack":
#             setValue("slack_logged_on", True)
#         else:
#             setValue("slack_logged_on", False)

def disconnectSlack():
    jwt = getItem("jwt")
    # print(">>@<<",jwt)
    try:
        headers = {'content-type': 'application/json', 'Authorization': jwt}
        disconnect_spotify_url = SOFTWARE_API + '/auth/slack/disconnect'
        disconnect = requests.put(disconnect_spotify_url, headers=headers)
        if disconnect.status_code == 200:
            print(disconnect.text)
            print("Music Time: Slack Disconnected !")
            setValue("slack_logged_on", False)
        else:
            print("Music Time: Unable to disconnected Slack at this moment.")

    except Exception as e:
        print("Music Time: Disconnection error !\n", e)
        pass


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
                slack_access_token = authinfo['user']['auths'][i]['access_token']

                setItem("slack_access_token",slack_access_token)
                print("Music Time: Got slack access token !")

# print(slack_access_token)
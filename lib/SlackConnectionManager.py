
import urllib.parse
import webbrowser

from ..Constants import *
from .SoftwareUtil import *
from .SoftwareSettings import *
from .SoftwareHttp import *


def launchConnectSlack():
    jwt = getItem("jwt")
    encodedJwt = urllib.parse.quote(jwt)
    qryStr = "integrate=slack&plugin=musictime&token=" + encodedJwt
    endpoint = SOFTWARE_API + "/auth/slack?"+qryStr
    print("encodedJwt:", encodedJwt, "\nqryStr:",
          qryStr, "\nendpoint_url:", endpoint)
    webbrowser.open(endpoint)
    # refetchUserStatusLazily(10)
    time.sleep(20)


# connectSlack(jwt)
def getSlackTokens():
    api = '/users/plugin/state'
    getauth0 = requestIt("GET", api)
    try:
        if getauth0.status_code >= 200:
            authinfo = getauth0.json()
            print("getSlackTokens:authinfo:", authinfo)

            for i in range(len(authinfo['user']['auths'])):
                if authinfo['user']['auths'][i]['type'] == "slack":
                    print("slack_auths: ", authinfo['user']['auths'][i])
                    slack_access_token = authinfo['user']['auths'][i]['access_token']
                    setValue("slack_logged_on", True)
                    setItem("slack_access_token", slack_access_token)
                    print("Music Time: Got slack access token !")

                    # infoMsg = "Unable to connect slack "
                    # clickAction = sublime.message_dialog(infoMsg)
    except Exception as e:
        setValue("slack_logged_on", False)
        # print("Music Time: slack token not found in user auths")
        print("Music Time: Unable to connect")
        infoMsg = "Please try after some time unable to connect slack at this moment."
        clickAction = sublime.message_dialog(infoMsg)


def disconnectSlack():
    try:
        api = '/auth/slack/disconnect'
        disconnect = requestIt("PUT", api)
        if disconnect.status_code == 200:
            # print(disconnect.text)
            print("Music Time: Slack Disconnected !")
            setValue("slack_logged_on", False)
        else:
            print("Music Time: Unable to disconnected Slack at this moment.")

    except Exception as e:
        print("Music Time: Disconnection error !\n", e)
        pass


def getSlackChannels():

    api = "/api/conversations.list"
    get_channels = requestSlack("GET", api)
    if get_channels.status_code == 200:
        channels_data = get_channels.json()
        ids = []
        names = []

        for i in channels_data["channels"]:
            #             print("Id:",i['id'],"|" ,"name:",i['name'])
            ids.append(i['id'])
            names.append(i['name'])
            channel_list = dict(zip(names, ids))
            # slack_channel_names = ids
    return channel_list


def sendSlackMessage(channel_id, track_id):
    track_url = "https://open.spotify.com/track/"+track_id
#     channel_id = "CNAR34A9M"

    txt = "Check out this Song\n" + track_url
    payload_data = {"channel": channel_id, "text": txt}

    api = "/api/chat.postMessage"
    get_channels = requestSlack("POST", api, payload_data)
    if post_msg.status_code == 200:
        print("Music Time: Slack share succeed !\n", post_msg.json())
    else:
        print("Music Time: unable to share on Slack !\n", post_msg.json())



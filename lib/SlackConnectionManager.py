
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
    getauth0 = requestIt("GET", api, None, getItem("jwt"), True)
    try:
        if getauth0 is not None and getauth0["status"] >= 200:
            # authinfo = getauth0.json()
            print("getSlackTokens:authinfo:", getauth0)

            for i in range(len(getauth0['user']['auths'])):
                if getauth0['user']['auths'][i]['type'] == "slack":
                    print("slack_auths: ", getauth0['user']['auths'][i])
                    slack_access_token = getauth0['user']['auths'][i]['access_token']
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
        disconnect = requestIt("PUT", api, None, getItem("jwt"))
        if disconnect is not None and disconnect["status"] == 200:
            # print(disconnect)
            print("Music Time: Slack Disconnected !")
            setValue("slack_logged_on", False)
        else:
            print("Music Time: Unable to disconnected Slack at this moment.")

    except Exception as e:
        print("Music Time: Disconnection error !\n", e)
        pass


def getSlackChannels():

    api = "/api/conversations.list"
    get_channels = requestSlack("GET", api, None, getItem("slack_access_token"))
    if get_channels["status"] == 200:
        # channels_data = get_channels.json()
        ids = []
        names = []

        for i in get_channels["channels"]:
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
    requestSlack("POST", api, payload_data, getItem("slack_access_token"))
    if post_msg["status"] == 200:
        print("Music Time: Slack share succeed !\n", post_msg)
    else:
        print("Music Time: unable to share on Slack !\n", post_msg)



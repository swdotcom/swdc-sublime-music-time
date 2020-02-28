
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
    print("encodedJwt:", encodedJwt, "\nqryStr:",
          qryStr, "\nendpoint_url:", endpoint)
    webbrowser.open(endpoint)
    # refetchUserStatusLazily(10)
    time.sleep(20)


# connectSlack(jwt)
def getSlackTokens():
    jwt = getItem("jwt")
    headers0 = {'content-type': 'application/json', 'Authorization': jwt}
    getauth0 = requests.get(
        'https://api.software.com/users/plugin/state', headers=headers0)
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
    jwt = getItem("jwt")
    # print(">>@<<",jwt)
    try:
        headers = {'content-type': 'application/json', 'Authorization': jwt}
        disconnect_spotify_url = SOFTWARE_API + '/auth/slack/disconnect'
        disconnect = requests.put(disconnect_spotify_url, headers=headers)
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
    url = "https://slack.com/api/conversations.list"
    slack_headers = {"Content-Type": "application/x-www-form-urlencoded",
                     "Authorization": "Bearer {}".format(getItem("slack_access_token"))}

    get_channels = requests.get(url, headers=slack_headers)
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

    post_msg_url = "https://slack.com/api/chat.postMessage"
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": "Bearer {}".format(getItem("slack_access_token"))}

    txt = "Check out this Song\n" + track_url
    payload_data = {"channel": channel_id, "text": txt}
#     payload = json.dumps(payload_data)
    post_msg = requests.post(post_msg_url, headers=headers, data=payload_data)
    if post_msg.status_code == 200:
        print("Music Time: Slack share succeed !\n", post_msg.json())
    else:
        print("Music Time: unable to share on Slack !\n", post_msg.json())

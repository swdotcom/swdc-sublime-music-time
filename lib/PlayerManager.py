from threading import Thread, Timer, Event
import sublime_plugin
import sublime
import copy
import time

from .SoftwareHttp import *
from .SoftwareUtil import *
from ..Software import *
from .MusicPlaylistProvider import *
from .SoftwareMusic import *


active_device = {}
computer_device = {}


def checkSpotifyUser():
    if (userTypeInfo() == "premium"):
        items = [
            ("Launch Web Player", []),
            ("Launch Desktop Player", []),
            ]

    elif (userTypeInfo() == "non-premium"):
        items = [("Launch Desktop Player", []),]

    else:
        items = []
    return items


def getSpotifyDevice():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    get_device_url = "https://api.spotify.com" + "/v1/me/player/devices"
    getdevs = requests.get(get_device_url, headers=headers)
#     print(getdevs.text)
    device_list = []
    
    if getdevs.status_code == 200:
        devices = getdevs.json()['devices']
        
        for i in range(len(devices)):
            device_list.append({"device_name":devices[i]['name'],"device_id":devices[i]['id'],"type":devices[i]['type']})

        
        if len(devices) == 0:
            device_list = []
            print("Device not found")        
        
    return device_list


def getSpotifyActiveDevice():
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    get_device_url = "https://api.spotify.com" + "/v1/me/player/devices"
    getdevs = requests.get(get_device_url, headers=headers)

    active_device = {}#{"device_name":"","device_id":""}
    
    if getdevs.status_code == 200:
        devices = getdevs.json()['devices']
        for i in range(len(devices)):
            if devices[i]['is_active'] == True:
                active_device['device_name'] = devices[i]['name']
                active_device['device_id'] = devices[i]['id']
#                 active_device =  {"device_name":device_name,"device_id":device_id}
            # else:
            #     active_device = {}
    print("getSpotifyActiveDevice:",active_device)
    return active_device


class SelectPlayer(sublime_plugin.WindowCommand):
    def run(self):
        global active_device
        # global playlist_id
        # global current_song
        # print("SelectPlayer:playlist_id",playlist_id,"\n","current_song",current_song)

        device_list = getSpotifyDevice()
        active_device = getSpotifyActiveDevice()

        # if no device available, show generic list
        if device_list == []:
            print("SelectPlayer:run:")
            items = checkSpotifyUser()
            print("items",items)

        # if device are available, show them
        else:
            if userTypeInfo() == "non-premium":
                items = []
                for i in device_list:
                    if i['type'] == "Computer" and "Web Player" not in i['device_name']:
                    # print(i['device_name'], i['device_id'], i['type'])
                        items.append((i['device_name'],[i['device_id']]))

                new_items = []
                if active_device.get('device_id') is not None:
                    print("found active device")
                    active_device_id = active_device.get('device_id')
                    active_device_name = active_device.get('device_name')
                    print(active_device_name)
                    
                    for i in items:
                        # print(i[0])     # get device name in string
                        # print(i[1][0])  # get device id in string
                        if i[1][0] == active_device_id:
                            new_items.append(("Listening on "+i[0],[i[1][0]]))
                        else:
                            new_items.append(("Available on "+i[0],[i[1][0]]))
                            
                    print("new_items before\n",new_items)
                #     is_web = False
                #     is_desktop = False

                else:
                    print("when device is not active")
                    for i in items:
                        new_items.append(("Available on "+i[0],[i[1][0]]))


            else:
                items = []
                for i in device_list:
                    if i['type'] == "Computer":
                    # print(i['device_name'], i['device_id'], i['type'])
                        items.append((i['device_name'],[i['device_id']]))

                new_items = []
                is_web = False
                is_desktop = False

                if active_device.get('device_id') is not None:
                    print("found active device")
                    active_device_id = active_device.get('device_id')
                    active_device_name = active_device.get('device_name')
                    print(active_device_name)
                    
                    for i in items:
                        # print(i[0])     # get device name in string
                        # print(i[1][0])  # get device id in string
                        if i[1][0] == active_device_id:
                            new_items.append(("Listening on "+i[0],[i[1][0]]))
                        else:
                            new_items.append(("Available on "+i[0],[i[1][0]]))
                            
                    print("new_items before\n",new_items)
                #     is_web = False
                #     is_desktop = False

                else:
                    print("when device is not active")
                    for i in items:
                        new_items.append(("Available on "+i[0],[i[1][0]]))
                    
                        
                # Check web/desktop player is avaiable or not
                for i in new_items:
                    if "Web Player" not in i[0]:
                        is_desktop = True
                    else:                 # "Web Player" not in i[0]:
                        is_web = True

                print("web",is_web)
                print("desk",is_desktop)

                if is_web is True and is_desktop is False:         
                    new_items.append(("Launch Desktop Player",[]))

                elif is_web is False and is_desktop is True:
                    new_items.append(("Launch Web Player",[]))

                elif is_web is False and is_desktop is False:
                    new_items = []
                    new_items.append(("Launch Web Player",[]))
                    new_items.append(("Launch Desktop Player",[]))
                else:
                    # elif web is True and desk is True:
                    print("Both exist")
                    pass


            items = new_items
            # print("items update with new items")
            print("final show list\n",items)

        # select from available device
        devices = [key for key, value in items]

        # Trigger the first show panel and pass on the id of the selected item & the items
        self.window.show_quick_panel(devices, lambda id_1: self.on_done(id_1, items))

    def on_done(self, id_1, items):
        global active_device
        active_device = {}
        print("on_done(self, id_1, items)",id_1,items)
        if id_1 >= 0:
            device_ids = items[id_1][1]
            print("device_ids",device_ids)
            print("items[id_1]",items[id_1])
            device = items[id_1][0]
            print("device",items[id_1][0])

            # If there is no device available
            if device_ids == []:
                # when desktop is selected
                if device == "Launch Desktop Player":
                    
                    if isMac() == True:
                        msg = subprocess.Popen(["open", "-a", "spotify"], stdout=subprocess.PIPE)
                    else:
                        result = subprocess.Popen("%APPDATA%/Spotify/Spotify.exe", shell=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    # output,error = result.communicate()
                    print("Launching desktop player ...1")
                    time.sleep(5)
                    devices = getSpotifyDevice()
                    print("Launching desktop player ...2",devices)
                        # print("Launching devices")
                    try:
                        devices = getSpotifyDevice()
                        print("Launch Desktop Player: list of devices",devices)

                        device_id = getNonWebPlayerId(devices)
                        print("Launch non Web Player:device_id",device_id)

                        active_device['device_id'] = device_id
                        print(active_device)
                    except Exception as e:
                        print("Launch Desktop Player Error",e)
                        # If desktop player didn't work. launch Web player
                        print("Desktop player not found. Opening Web player ...Error:")
                        webbrowser.open("https://open.spotify.com/")
                        time.sleep(5)

                        try:
                            devices = getSpotifyDevice()
                            print("Launch Web Player:devices",devices)

                            device_id = getWebPlayerId(devices)
                            print("Launch Web Player:device_id",device_id)

                            active_device['device_id'] = device_id
                            print(active_device)
                        except Exception as e:
                            print("Launch Web Player",e)

                # If user selects web player to launch
                elif device == "Launch Web Player":
                    webbrowser.open("https://open.spotify.com/")
                    time.sleep(5)

                    devices = getSpotifyDevice()
                    print("Launch Web Player:devices",devices)
                    device_id = getWebPlayerId(devices)

                    print("Launch Web Player:device_id",device_id)

                    active_device['device_id'] = device_id
                    print(active_device)

                else:
                    pass
                # time.sleep(5)
                # Get the device id to transfer the playback
                try:
                    transferPlayback(device_id)
                    # time.sleep(2)
                    active_device = getSpotifyActiveDevice()
                    print("Got active_device",active_device)
                except Exception as e:
                    print("transfer device error",e)
            
            else:
                device_id = items[id_1][1][0]
                active_device['device_name'] = device
                active_device['device_id'] = device_id
                transferPlayback(device_id)
                print("active_device",active_device)

        # else: 
        #     print("id_1",id_1)
        #     print("items[id_1]",items[id_1])
    def is_enabled(self):
        return (getValue("logged_on", True) is True)


def transferPlayback(deviceid):
    #https://api.spotify.com/v1/me/player
    transfer_api = "https://api.spotify.com/v1/me/player"
    headers = {"Authorization": "Bearer {}".format(getItem('spotify_access_token'))}
    payload = json.dumps({"device_ids":[deviceid],"play":True})
    print("payload for transfer device:",payload)
    transfer = requests.put(transfer_api, headers = headers , data = payload)
    if transfer.status_code == 204:
        print("playback transferred to device_id",deviceid)
        # time.sleep(5)
    else:
        print(transfer.text)



def getNonWebPlayerId(device_list):
    # print('device list inside getNonWebPlayerId \n',device_list)
    for i in device_list:
        # print('getNonWebPlayerId \n',i)
        if i['type'] == "Computer" and "Web Player" not in i['device_name']:
            # print(i['device_name'])
            deviceid = i['device_id']
            # print("getNonWebPlayerId:",deviceid)    
            return deviceid
    return None


def getWebPlayerId(device_list):    
    for i in device_list:
        if i['type'] == "Computer" and "Web Player" in i['device_name']:
#             print(i['device_name'])
            deviceid = i['device_id']
            # print("getWebPlayerId:",deviceid)
            return deviceid
    return None
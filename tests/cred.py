import requests


def get_credentials():
    get_JWT = requests.get('https://api.software.com/data/apptoken?token=3000')
    jwt = get_JWT.json()['jwt']
    headers = {'content-type': 'application/json','Authorization':jwt}
    get_client_creds = requests.get('https://api.software.com/auth/spotify/clientInfo', headers = headers)
    clientId = get_client_creds.json()['clientId']
    clientSecret = get_client_creds.json()['clientSecret']
    return clientId,clientSecret


def getauthinfo():
    jwt = getItem("jwt")

    headers = {'content-type': 'application/json', 'Authorization': jwt}
    getauth = requests.get(
        'https://api.software.com/auth/spotify/user', headers=headers)
    authinfo = None
    if getauth.status_code == 200:
        try:
            authinfo = getauth.json()
        except Exception as e:
            print("AUTHTOKEN ERROR\n",e)
            
    return authinfo
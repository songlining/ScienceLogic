import requests

host = self.cred_details['cred_host']
username = self.cred_details['cred_user']
password = self.cred_details['cred_pwd']
device_name = self.name
get_devices_url = 'https://arlo.netgear.com/hmsweb/users/devices'

cache = em7_snippets.cache_api(self)
CACHE_KEY_TOKEN = 'ARLO:' + device_name + host + "token"
CACHE_KEY_DEVICES = 'ARLO:' + device_name + host + "devices"

retries = 3

session = requests.Session()

def login(url, username, password):
    resp = session.post(url,
                        data='{"email":"%s","password":"%s"}' % (username, password),
                        headers={"Content-Type": "application/json"})
    if resp and (resp.status_code == 200):
        print "Login success, Resp: %s" % (resp.json())
        token = resp.json()['data']['token']
        print "Login token: %s" % (token)
        cache.cache_result(token, ttl=None, key=CACHE_KEY_TOKEN, commit=True)
    else:
        print "Failed to get login token, resp: %s" % (resp.json())

def rest_call():
    token = cache.get(CACHE_KEY_TOKEN)
    print "token for rest call: %s" % (token)
    resp = session.get(get_devices_url,
                       headers={'Content-Type': 'application/json',"Authorization": token})
    return resp.json()

######### MAIN #########

# check if session token is already in cache
token = cache.get(CACHE_KEY_TOKEN)
if token == None:
    login(host, username, password)

while True:
    j = rest_call()
    print "resp >> %s" % (j)
    if j['success'] == False:
        print "Login failed: %s" % j['data']['reason']
        global retries
        retries = retries - 1
        if retries == 0: 
            print "Too many failed logins, retry in the next internal"
            break
        else:
            login(host, username, password)
    else:
        print "REST call succeeded, writing to cache."
        cache.cache_result(j, ttl=None, key=CACHE_KEY_DEVICES, commit=True)
        break
        

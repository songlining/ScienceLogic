# Standard libraries.

from requests import Request, Session
import json
import datetime
import time
import re
import code

# ScienceLogic libraries.

from content.content_logger import get_content_logger, LOG_INF, LOG_RES, LOG_ERR, LOG_DEFAULT, LOG_ALL
from content.snippet_exception import SnippetException
import silo_common.snippets as em7_snippets

# Globals

api_session = Session()

# Basic functions to work with EM7.

def cred_details(key):
    return self.cred_details[key]

def set_arg(arg,value):
    result_handler[arg] = [(0,value),]

def debug(details):
    print(details)

def app_alert(details):
    self.internal_alerts.append((257,details))

def starting_msec():
    end_secs = int(time.time())
    start_secs = end_secs - int(self.freq * 60)
    return int(start_secs * 1000)

# Details on the orchestrator.

def base_url():
    return "{}/".format(cred_details('curl_url'))

def host():
    return cred_details('curl_url')[8:]

# Work out if a HTTPS proxy is needed for the requests and return the right values.

def proxy():
    proxy = cred_details('curl_proxy_ip')
    if len(proxy) > 0:
        debug("Using the proxy {}".format(proxy))
        proxy_username = cred_details('curl_proxy_acct')
        if len(proxy_username) > 0:
            return { 'https': 'http://{}:{}@{}:{}'.format(proxy_username, cred_details('curl_proxy_passwd'), proxy, cred_details('curl_proxy_port')) }
        else:
            return { 'https': 'http://{}:{}'.format(proxy, cred_details('curl_proxy_port')) }

# Try to login to the API and get a session key.

def login():
    global api_session
    url = "{}j_security_check".format(base_url());
    args = 'j_username={}&j_password={}'.format(cred_details('cred_user'),cred_details('cred_pwd'))
    headers = { 'content-type': 'application/x-www-form-urlencoded' }
    debug("Trying to login via {}".format(url))
    try:
        resp = api_session.post(url, data=args, headers=headers, proxies=proxy(), verify=False)
        debug("HTTP Response Code is {}".format(resp.status_code))
        if resp.status_code == 200 and 'Set-Cookie' in resp.headers:
            return True

    except Exception as ex:
        debug("Login Exception")
        app_alert(str(ex))

    return False


def get_result(path):
    if login():
        debug("Logged in OK")
        url = "{}{}".format(base_url(),path)
        result = api_session.get(url)
        return True, result
    else:
        debug("Problems get_result()")
        return False

########
# Main #
########

try:
    unique_id = this_device.unique_id
    path = 'dataservice/device/interface?deviceId={}'.format(unique_id)
    ok, r = get_result(path)
    # code.interact(local=locals())
    if ok:
        # https://docs.sciencelogic.com/8-14-2/#Web_Content_Dev_and_Integration/Snippet_Dynamic_App_Development/performance_and_config_snippets.htm
        a1 = [];
        a2 = [];
        a3 = [];
        if 'data' in r.json().keys():
            if r.json()['data']:
                for i in r.json()['data']:
                    ifindex = i['ifindex']
                    ifname = i['ifname']
                    if_admin_status = 0 if i['if-admin-status'] == 'Down' else 1
                    if_oper_status = 0 if i['if-oper-status'] == 'Down' else 1
                    a1.append((ifindex, if_admin_status))
                    a2.append((ifindex, if_oper_status))
                    a3.append((ifindex, ifname))
        elif 'error' in r.json().keys():
            app_alert(r.json()['error']['details'])
        result_handler[(this_device.did, 'if_admin_status')] = a1
        result_handler[(this_device.did, 'if_oper_status')] = a2
        result_handler[(this_device.did, 'ifname')] = a3
            
except SnippetException as snippet_err:
    debug("Exception: {}".format(snippet_err))
except TypeError as type_err:
    debug("TypeError: {}".format(type_err))



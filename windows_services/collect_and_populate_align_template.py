from silo_common.snippets.powershell import powershell_winrm
from collections import namedtuple
import pprint

from silo_common.database import local_db
import ConfigParser
import hashlib
import requests
from requests.auth import HTTPBasicAuth

# Start of the dynamic application


######################################################################
# Modify the list below for the interested services, case sensitive.
# All auto start services will be populated into the custom attribute
# if the list is empty
######################################################################
#white_list = []
# A sample
white_list = ['WinRM', 'Dhcp']

######################################################################
# Mapping between Windows services and device templates
######################################################################
service_to_template = {
                       # The mapping below means when we discover a WinRM
                       # service (the key in the map), a device template with 
                       # the name 'WinRM' (the value on the right hand side) 
                       # will be applied to this device. 
                       'WinRM': 'WinRM',
                       'Dhcp': 'Dhcp'
                       }


class localAPI:
    _headers = None
    _httpauth = None
    _host = None
    def __init__(self, dbc, host='https://localhost/'):
        requests.packages.urllib3.disable_warnings()
        #Read the local IP addresses
        config = ConfigParser.ConfigParser()
        config.read('/etc/silo.conf')
        ipaddr = config.get('LOCAL', 'ipaddress')
        # Grab Items to make automatic connection to the API
        api_account = dbc.autofetch_value("SELECT api_internal_account FROM master.system_settings_core")
        mod_id = dbc.autofetch_value("SELECT id FROM master.system_settings_licenses WHERE status=0 AND ip='%s'" % (ipaddr))
        api_string = str(api_account)+'_SILO_API_INTERNAL_'+str(mod_id)
        # The API string is an MD5 that is passed as the authentication header, this does an MD5 hash of the string above
        m = hashlib.md5()
        m.update(api_string)
        md5_api_string = m.hexdigest()
        # This is the format the API header expects
        authentication_info = str(api_account)+','+str(mod_id)+','+md5_api_string
        self._headers = {'content-type': 'application/json'}
        self._httpauth=HTTPBasicAuth(authentication_info, '')
        self._host=host
    def get(self, uri, payload=None):
        return requests.get(self._host+uri, headers=self._headers, auth=self._httpauth, json=payload, verify=False)
    def put(self, uri, payload=None):
        return requests.put(self._host+uri, headers=self._headers, auth=self._httpauth, json=payload, verify=False)
    def post(self, uri, payload=None):
        return requests.post(self._host+uri, headers=self._headers, auth=self._httpauth, json=payload, verify=False)
    def delete(self, uri, payload=None):
        return requests.delete(self._host+uri, headers=self._headers, auth=self._httpauth, json=payload, verify=False)
    def head(self, uri, payload=None):
        return requests.head(self._host+uri, headers=self._headers, auth=self._httpauth, json=payload, verify=False)
    
    # Applying a device template to a device must have a content-type:application/em7-resource-uri
    def apply(self, uri, payload=None):
        return requests.post(self._host+uri, headers={"content-type": "application/em7-resource-uri"}, auth=self._httpauth, data=payload, verify=False)
         
# Convert template name to template id         
def get_template_id(dbc, template_name):
    id = dbc.autofetch_value("SELECT template_id FROM master_dev.template_common where template_name = '{0}'".format(template_name))
    return str(id)

COLLECT_ERROR = 257
app_name = "Microsoft: Windows Services Custom Attribute"

# only select the services that should be started automatically
ps_request = """get-wmiobject -class win32_service -Filter "startmode='auto'"| select-object Name"""
Request = namedtuple('Request', 'req_id key_column request app_id')

dbc = local_db()
api = localAPI(dbc)

try:
    request = Request(-1, 'DisplayName', ps_request, self.app_id)    
    data, error = powershell_winrm(self.did, self.ip, request, self.cred_details, True, None, None, self.logger)
    
    if error is not None and len(error) > 0:
        self.logger.ui_debug("Error: %s" % (error))
        
    elif data is not None:
        # Rearrange
        # First extract the individual dictionaries
        n = data['Name']
    
        # These are the lists that will be plugged into result_handler['oid_name']
        name = []
        
        windows_services = '|'
       
        for key in n.keys():
            tmpl = service_to_template.get(n[key], None)
            self.logger.debug("Service_to_template name: %s -> %s" % (n[key], tmpl))
            if tmpl is not None:
                tid = get_template_id(dbc, tmpl)
                self.logger.ui_debug("Template name to id: %s -> %s" % (tmpl, tid))
                if tid:
                    try:
                        r = api.apply("/api/device/%s" % (self.did), "/api/device_template/%s" % (tid))
                    except Exception, err:
                        self.logger.debug("Error while applying templates to device: %s" % (err))
            # generate the list anyway, to show all the services.
            name.append((key, n[key]))
            if white_list and n[key] in white_list:
                windows_services = windows_services + n[key] + '|'
            elif not white_list:
                windows_services = windows_services + n[key] + '|'
        
        # return the transformed data
        result_handler['Name'] = name
        
        custom_attribute = {'c-windows_services': windows_services}

        result = api.post("/api/device/%s" % self.did, custom_attribute)
     
except Exception, err:
    self.internal_alerts.append((COLLECT_ERROR, "%s [%s] for device %s [%s] IP: %s Error: %s" % (app_name, self.app_id, self.name, self.did, self.ip, err)))
    self.logger.debug("Error: %s" % (err))

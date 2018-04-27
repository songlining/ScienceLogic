host = self.cred_details['cred_host']
device_name = self.name

cache = em7_snippets.cache_api(self)
CACHE_KEY_DEVICES = 'ARLO:' + device_name + host + "devices"

#########################

devices = cache.get(CACHE_KEY_DEVICES)

print "devices >> %s" % (devices)

for d in devices['data']:
    if d["deviceType"] == "basestation":
        name = d["deviceName"]
        id = d["deviceId"]
        fv = d["firmwareVersion"]
        print "name: %s, id: %s, fv: %s" % (name, id, fv) 
        result_handler['name'] = [(0, name),]
        result_handler['id'] = [(0, id),]
        result_handler['firmwareVersion'] = [(0, fv),]

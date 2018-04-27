host = self.cred_details['cred_host']
device_name = root_device.name

cache = em7_snippets.cache_api(self)
CACHE_KEY_DEVICES = 'ARLO:' + device_name + host + "devices"

#########################

print "CACHE KEY: " + CACHE_KEY_DEVICES

devices = cache.get(CACHE_KEY_DEVICES)


name = []
id = []
fv = []

for d in devices['data']:
    if d["deviceType"] == "camera":
        n = d["deviceName"]
        i = d["deviceId"]
        f = d["firmwareVersion"]
        print "name: %s, id: %s, fv: %s" % (n, i, f)
        name.append((i, n)) 
        id.append((i, i))
        fv.append((i, f))

result_handler['name'] = name
result_handler['id'] = id
result_handler['firmwareVersion'] = fv

print result_handler['name']

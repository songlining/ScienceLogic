from silo_utils import silo_api, APIError

device_id = EM7_VALUES['%x']
device_name = EM7_VALUES['%X']
policy_name = EM7_VALUES['%n']


try:
    #logger = em7_snippets.logger(filename = '/data/tmp/action.log')
    api_instance = silo_api()
    if not api_instance:
        raise APIError("Could not open API")

    # get the value in the attribute for the source device
    api_res = api_instance.get('/api/device/{}'.format(device_id))
    attribute_name = 'c-' + attribute_name
    attribute_value = api_res.json().get(attribute_name)
    if attribute_value is None:
        #print "attribute doesn't exist"
        exit()

    # get devices with same attribute name and value
    api_res = api_instance.get('/api/device?limit=200&filter.{}.eq={}'.format(attribute_name, attribute_value))
    device_list = api_res.json().get('result_set')

    # for each device, modify its collection and maintenance state
    for device in device_list:
        URI = device['URI']
        
        # make sure the source device is not affected by this change, otherwise it might not be able to receive resolving events
        did = URI.split('/')[3]
        if (did == device_id):
            continue

        payload = '''{{"active":{{"user-initiated-maintenance":{},"system-disabled":{}}}}}'''.format(enable_maintenance, disable_collection)
        api_res = api_instance.post(URI, payload)
        #print api_res.json()

except APIError as e:
    EM7_RESULT = e


from silo_utils import silo_api, APIError

#device_id = EM7_VALUES['%x']
#device_name = EM7_VALUES['%X']
#policy_name = EM7_VALUES['%n']

device_id = 16
device_name = "R1"
policy_name = "test policy name"

attribute_name = "site"
enable_collection = 0
enable_maintenance = 0

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
        print "attribute doesn't exist"
        exit()

    # get devices with same attribute name and value
    api_res = api_instance.get('/api/device?limit=200&filter.{}.eq={}'.format(attribute_name, attribute_value))
    device_list = api_res.json().get('result_set')

    # for each device, modify its collection and maintenance state
    for device in device_list:
        URI = device['URI']
        print URI
        payload = '''{{"active":{{"user-initiated-maintenance":{},"system-disabled":{}}}}}'''.format(enable_maintenance, enable_collection)
        api_res = api_instance.post(URI, payload)
        # api_res = api_instance.post('/api/device/{}'.format(device_id), '{"active":{"user-initiated-maintenance":{},"system-disabled":{}}}'.format(enable_maintenance, enable_collection))
        print api_res.json()

except APIError as e:
    EM7_RESULT = e


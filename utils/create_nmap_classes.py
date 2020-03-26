from silo_common.database import local_db
import argparse
import getpass
import hashlib

parser = argparse.ArgumentParser(description='This script reads nmap-os-db (download from https://svn.nmap.org/nmap/nmap-os-db) and populate SL1 Device Classes for nmap scanning.')
parser.add_argument('--input', help='Required argument --  file name for nmap-os-db', required=True)
args = vars(parser.parse_args())

input_file = args['input']

dbc = local_db()

class_id = 20000

cpe_registry = []

# class_type is the database field int(10) name, it's called Class ID in the UI
def insert_class (device_class, descript, identifyer_3, class_type, devtype_guid):
    keyvals = {
        'descript': descript,
        'class': device_class,
        'image': '_generic_node.png',
        'identifyer_1': '',
        'identifyer_2': '/nmaprun/host/os/osmatch[1]/osclass[1]/cpe[1]',
        'identifyer_3': identifyer_3,
        'is_snmp': 0,
        'root_device': 0,
        'family': 9,
        'family_guid': '',
        'uptime_id': 1,
        'correlation_type': 0,
        'virtual': 0,
        'process_type': 0,
        'service_type': 0,
        'l3_topo': 0,
        'id2_tabular': 0,
        'weight': 6,
        'pdu_packing': 0,
        'intf_index_change': 0,
        'dashboard_id': '67',
        'devtype_guid': devtype_guid,
        'class_type': class_type,
        'date_edit': ''
    }

    print("Class: {} | Description: {} | identifyer_3: {} | class_type: {} | devtype_guid: {}".format(device_class, descript, identifyer_3, class_type, devtype_guid))
    ret = dbc.autoexec_insert('master.definitions_dev_classes', keyvals)

def process_buffer(buffer):
    global class_id

    cpe = ''
    # look for the first line of CPE
    for line in buffer:
        if line[0:3] == 'CPE':
            cpe = line[4:].strip().strip(' auto')
            break
    # cpe = cpe.replace('/', '\/')
    if cpe == '':
        return

    if cpe not in cpe_registry:
        cpe_registry.append(cpe)
        identifyer_3 = cpe
    else:
        return

    fingerprint = buffer[0][12:].strip()
    descript = fingerprint

    # find the class
    end = buffer[1].find(' |')
    device_class = 'NMAP - ' + buffer[1][6:end].strip()

    hash_object = hashlib.md5(device_class + identifyer_3 + str(class_id))
    devtype_guid = hash_object.hexdigest()

    insert_class(device_class, descript, identifyer_3, class_id, devtype_guid)
    class_id = class_id + 1

with open(input_file, 'r') as f:
    buffer = []
    start = False
    for line in f:
        if line[0] == '#':
            next
        if line[0:11] == 'Fingerprint':
            buffer.append(line)
            start = True
        elif start == True and len(line.strip()) == 0:
            start = False
            process_buffer(buffer)
            buffer = []
        elif start == True:
            buffer.append(line)

# insert_class("Linux", "Linux - General")

from silo_common.database import local_db

dbc = local_db()

query_interfaces = '''
SELECT iface.if_id, iface.Alias
  FROM master_dev.device_interfaces iface
  WHERE iface.Alias != ""
'''

query_itagm = '''
SELECT if_id
  FROM master_dev.device_interface_tags_map
'''

interfaces = dbc.autofetchall_dict(query_interfaces)
itagm = dbc.autofetchall_dict(query_itagm)

tag_if_id_list = []
if_id_to_tag_id = []

for d in itagm:
    tag_if_id_list.append(d["if_id"])

for d in interfaces:
    if d["if_id"] in tag_if_id_list:
        print "Found existing if tag map record: {}, bypassing...".format(d["if_id"])
        next;
    else:
        keyvals = {
            'tag_name': d['Alias']
        }

        # ret: 1 is success, 0 is failed
        ret = dbc.autoexec_insert('master_dev.device_interface_tags', keyvals)
        if ret == 1:
            tag_id = dbc.lastrowid
            if_id_to_tag_id.append({'if_id': d['if_id'], 'tag_id': tag_id})
        else:
            next;

for d in if_id_to_tag_id:
    keyvals = {
        'if_id': d['if_id'],
        'tag_id': d['tag_id']
    }
    ret = dbc.autoexec_insert('master_dev.device_interface_tags_map', keyvals)
    if ret == 1:
        print("inserted to map: {} -> {}").format(d['if_id'], d['tag_id'])

# This file is to perform all SSH related activities
import paramiko
# For testing to be removed
from private import *

# Configs Keys
config_key = ['alg_defs', 'b2bua2', 'cos_defs', 'cos_gred_defs', 'dsp', 'evdo', 'fw_defs', 'intf', 'ip', 'nat_defs',
              'pptp_defs', 'pptp_server', 'time_defs', 'ts_defs', 'file_srv_defs', 'sipua_defs', 'wlr', 'user_mgmt',
              'image_defs', 'local_defs', 'eth_rate', 'vlan_port', 'snmpd_defs']

# SSH login stuff
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip_address, username=username, password=password)

# Dictionary to make from em_valid_configs.conf for all keys
em_config_dic = {}


def get_known_config():
    with open('em_valid_configs.conf') as f:
        for line in f:
            line = line.strip()
            config_entry = line.split('=')
            # print(line)
            # print(config_entry[0])
            em_config_dic[config_entry[0]] = config_entry[1]
            # pp.pprint(em_config_dic)


# Dictionary for config values (loaded from em_dynamic_values.csv) that can be variable Broken down
# TYPE: PARAM_NAME, VALUE_TAG
# TYPE is SIP, VOIP, FW, WAN, WLR, LAN, VLAN, TS, FS, SURV, SNMP
# VALUE_TAG is %CLIENT_LIST_TIMER%, %CUSTOM_DOMAIN%, %DEFAULT_IMPORTANT%, %LLDP_STATUS%, %NET_UNIQUE%, %NOT_IMPORTANT%,
# %SIP_SERVER%, %SNMP_UNIQUE%, %SSH_TUNNEL%, %SURV_UNIQUE%, %TS_UNIQUE%, %VOICE_VLAN%, %WLR_UNIQUE%

value_tag_dic = {'%CLIENT_LIST_TIMER%': "Stale timer for client list.  Read the help file on this.",
                 '%CUSTOM_DOMAIN%': str(custom_domain) + " is your selected custom domain.",
                 '%DEFAULT_IMPORTANT%': "This value should be left as is, unless otherwise told to change.",
                 '%LLDP_STATUS%': "Usually this can be left as is. If causing issue, disable.",
                 '%NET_UNIQUE%': "Unique to local network.  Use the network page to see overview.",
                 '%NOT_IMPORTANT%': "Value can be anything, should not affect CALLP.  Best to leave default.",
                 '%SIP_SERVER%': str(sip_server) + " is the SIP server based off the location you picked.",
                 '%SNMP_UNIQUE%': 'SNMP should be updated correctly with the relevant customer data',
                 '%SSH_TUNNEL%': "If disabled, no SSH tunneling will work.  Enable to allow SSH tunneling",
                 '%SURV_UNIQUE%': "These can be tweaked in certain deployments.  Leave default unless otherwise told.",
                 '%TS_UNIQUE%': "Traffic Shaper can be tweaked in certain deployments.  Leave default unless "
                                "otherwise told.",
                 '%VOICE_VLAN%': "Is your Voice VLAN assinged correctly.  This should be the VLAN your phones are on.",
                 '%WLR_UNIQUE%': "These are the configurations for WLR.  Verify correct settings from these values."}
dynamic_conf_dic = {}


def get_dynamic_dic():
    with open('em_dynamic_values.csv') as f:
        for line in f:
            line = line.strip()
            config_line = line.split(',')
            # print(line)
            # print(config_entry[0])
            dynamic_conf_dic[config_line[1]] = config_line[0], config_line[2]
            # pp.pprint(em_config_dic)


# Dictionary with the EM in testing configs
em_local_dic = {}


def get_em_config():
    for item in config_key:
        stdin, stdout, stderr = ssh.exec_command("cat /etc/config/" + item + ".conf")
        em_config_lines = stdout.readlines()
        for line in em_config_lines:
            line = line.strip()
            line = line.split('=')
            em_local_dic[line[0]] = line[1]
            # pp.pprint(em_local_dic)


# Function to use the em_config_dic keys and see if they are all in the em_local_dic keys
# This will make 3 lists from the keys, 1 the found items and 2 the extra items and 3 the keys that are missing
matching_keys = []
nonmatching_keys = []
missing_keys = []
keys_with_dyn_values = []
discarded_keys = []
final_result_dic = {}


def config_compare_keys():
    for key in em_local_dic.keys():
        # print(key)
        if str(key) in em_config_dic.keys():
            # print("found")
            matching_keys.append(key)
        else:
            # print("not found")
            nonmatching_keys.append(key)
    for key in em_config_dic.keys():
        if not key in matching_keys:
            missing_keys.append(key)


# This function to be called to evaluate the values for keys in the em_config_dic and see if they match the matching
# keys values from em_local_dic.  Also, evaluate if it is a VARIABLE value and ignore (to be handled elsewhere.

def config_value_compare():
    for key, value in em_config_dic.items():
        if key in matching_keys and '%' not in value:
            value_to_compare = em_local_dic[str(key)]
            if value_to_compare in value:
                final_result_dic[key] = {}
                final_result_dic[key]['type'] = 'STATIC'
                final_result_dic[key]['unique_type'] = 'MISC'
                final_result_dic[key]['local_value'] = str(value)
                final_result_dic[key]['correct_value'] = str(value_to_compare)
                final_result_dic[key]['key_definition'] = 'NO DEFINITION YET'
                final_result_dic[key]['test_result'] = 'PASS'
            else:
                final_result_dic[key] = {}
                final_result_dic[key]['type'] = 'STATIC'
                final_result_dic[key]['unique_type'] = 'MISC'
                final_result_dic[key]['local_value'] = str(value)
                final_result_dic[key]['correct_value'] = str(value_to_compare)
                final_result_dic[key]['key_definition'] = 'NO DEFINITION YET'
                final_result_dic[key]['test_result'] = 'FAIL'
                # print(key, value)
        elif key in matching_keys and '%' in value:
            keys_with_dyn_values.append(key)
        else:
            discarded_keys.append(key)


def dynamic_values():
    for key, value in dynamic_conf_dic.items():
        if 'SIP' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'SIP'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'VOIP' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'VOIP'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'FW' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'FW'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'WAN' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'WAN'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'WLR' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'WLR'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'LAN' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'LAN'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'VLAN' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'VLAN'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'TS' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'TS'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'FS' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'FS'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'SURV' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'SURV'
            final_result_dic[key]['local_value'] = em_local_dic.get(key)
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        elif 'SNMP' in value[0]:
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'SNMP'
            final_result_dic[key]['local_value'] = em_local_dic.get(value[0], "NONE")
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = value_tag_dic.get(value[1], "ERR")
            final_result_dic[key]['test_result'] = 'REVIEW MANUALLY'
        else:
            final_result_dic[key] = 'DYNAMIC', "KEY ERROR: NOT FOUND", "N/A", "N/A", "FAIL"
            final_result_dic[key] = {}
            final_result_dic[key]['type'] = 'DYNAMIC'
            final_result_dic[key]['unique_type'] = 'N/A'
            final_result_dic[key]['local_value'] = 'KEY ERROR: NOT FOUND'
            final_result_dic[key]['correct_value'] = 'N/A'
            final_result_dic[key]['key_definition'] = 'N/A'
            final_result_dic[key]['test_result'] = 'UNKNOWN'


# Query our final results for the special tags
# unique_type_var = 'WAN'


# unique_type_tmp_list = []


def get_unique_type(unique_type):
    unique_type_tmp_list = []
    for wanted_keys, wanted_values in final_result_dic.items():
        # print(wanted_keys)
        # print(wanted_values['unique_type'])
        if unique_type in wanted_values['unique_type']:
            unique_type_tmp_list.append([str(wanted_keys), str(wanted_values['local_value'])])
    return unique_type_tmp_list


# print(key)
# print(final_result_dic[key]['unique_type'])
# if final_result_dic[key]["unique_type"] == unique_type:
#    unique_type_dic[key] = final_result_dic[key]['local_value']

# Get data ready for DJANGO
# network_data = get_unique_type(unique_type="WAN")


get_dynamic_dic()
get_known_config()
get_em_config()
config_compare_keys()
config_value_compare()
dynamic_values()

wan_data = get_unique_type(unique_type="WAN")
sip_data = get_unique_type(unique_type="SIP")
voip_data = get_unique_type(unique_type="VOIP")
fw_data = get_unique_type(unique_type="FW")
wlr_data = get_unique_type(unique_type="WLR")
lan_data = get_unique_type(unique_type="LAN")
vlan_data = get_unique_type(unique_type="VLAN")
ts_data = get_unique_type(unique_type="TS")
fs_data = get_unique_type(unique_type="FS")
surv_data = get_unique_type(unique_type="SURV")
snmp_data = get_unique_type(unique_type="SNMP")

print("WAN", wan_data)
print('\n\n\n\n\n\n\n\n')
print("SIP", sip_data)
print('\n\n\n\n\n\n\n\n')
print("VOIP", voip_data)
print('\n\n\n\n\n\n\n\n')
print("FW", fw_data)
print('\n\n\n\n\n\n\n\n')
print("WLR", wlr_data)
print('\n\n\n\n\n\n\n\n')
print("LAN", lan_data)
print('\n\n\n\n\n\n\n\n')
print("VLAN", vlan_data)
print('\n\n\n\n\n\n\n\n')
print("TS", ts_data)
print('\n\n\n\n\n\n\n\n')
print("FS", fs_data)
print('\n\n\n\n\n\n\n\n')
print("SURV", surv_data)
print('\n\n\n\n\n\n\n\n')
print("SNMP", snmp_data)

# get_unique_type(unique_type_var)
# print(get_uiquetypes(unique_type_var))

# print('\n\n\n\n\n\n\n\n')
# print(json.dumps(final_result_dic, indent=4, sort_keys=True))

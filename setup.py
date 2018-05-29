#!/usr/bin/env python3
import sys
import os
import json
import random
import uuid
import re
import time

ROOT_PATH = os.path.dirname(sys.argv[0])
DEFAULT_CONFIG = "{}/config/lower.json".format(ROOT_PATH)
PATTERN_IPv4 = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"
ZONE_TW = "asia-east1-"
ZONE_JP = "asia-northeast1-"
ZONE_L = "abc"
OUTPUT_CONFIG = "vpn-proxy.ovpn"
STARTUP_SCRIPT = ROOT_PATH + "/script/install_vpn.sh"

def usage():
    print("Usage: {} install <openvpn_client_config>".format(sys.argv[0]))
    print("")
    print("openvpn_client_config: Proxy target vpn server config.")
    print("")

def _create_instance(conf, client_conf, uid, name, zone):
    rs = {}
    print("Create instance {}".format(name))
    # Init GCP Instance info
    config_path = '/tmp/' + client_conf
    conf['boot-disk-device-name'] = "gcpjpdisk-{}".format(uid)
    conf['zone'] = zone
    conf['metadata-from-file'] = 'startup_script={}'.format(STARTUP_SCRIPT)
    # Create GCP Instance
    cmd = "gcloud compute instances create {}".format(name)
    for (key, val) in conf.items():
        if type(val) == bool:
            if val:
                cmd += " --{}".format(key)
        else:
            cmd += " --{} {}".format(key, val)
    print("Execute create instance ... ")
    print(">> {}".format(cmd))
    exe = os.system(cmd) 

    time.sleep(30)
    # SCP Client Config into instance
    cmd = "gcloud compute scp {} {}:{} --zone {}".format(
            client_conf, name, config_path, conf['zone'])
    print("SCP Client config into instance ... ")
    print(">> {}".format(cmd))
    exe = os.system(cmd) 
    
    time.sleep(10)
    # Install VPN-PROXY
    restartup = "sudo google_metadata_script_runner --script-type startup"
    cmd = "gcloud compute ssh {} --zone {} --command \"{}\"".format(
            name, zone, restartup)
    print("Install VPN-PROXY ... ")
    print(">> {}".format(cmd))
    exe = os.system(cmd) 
    time.sleep(30)
    # Get VPN-PROXY config
    cmd = "gcloud compute scp {}:{} {} --zone {}".format(
            name, '/tmp/'+OUTPUT_CONFIG, '.', conf['zone'])
    print("Get VPN-PROXY Config ... ")
    print(">> {}".format(cmd))
    exe = os.system(cmd) 
    # Get GCP IP
    index = 4
    if "preemptible" in conf:
        if conf["preemptible"]:
            index = 5
    cmd = "gcloud compute instances list|grep \"%s\"|awk '{print $%s,$%s}'" % \
            (name, index, index+1)
    gcp_ip = os.popen(cmd).read()[:-1]
    rs["internal_ip"] = gcp_ip.split(" ")[0]
    rs["external_ip"] = gcp_ip.split(" ")[1]
    rs["config"] = OUTPUT_CONFIG
    return rs

def _create_instance_jp(conf, remote_conf):
    uid = "".join(random.sample(list(uuid.uuid4().hex), 8))
    name = "gcp-jp-{}".format(uid)
    zone = ZONE_JP + random.sample(list(ZONE_L), 1)[0]
    return _create_instance(conf, remote_conf, uid, name, zone)

def _create_instance_tw(conf, client_conf):
    uid = "".join(random.sample(list(uuid.uuid4().hex), 8))
    name = "gcp-tw-{}".format(uid)
    zone = ZONE_TW + random.sample(list(ZONE_L), 1)[0]
    data = _create_instance(conf, client_conf, uid, name, zone)

    cmd = "sed -i 's/{}/{}/g' {}".format(
            data["internal_ip"], data["external_ip"], data["config"])
    exe = os.system(cmd)
    cmd = "mv {} {}".format(data["config"], name+".ovpn")
    exe = os.system(cmd)
    return "{}/{}".format(os.getcwd(), name+".ovpn")

def install(config=None):
    if config is None:
        print("Error: Must have OpenVPN Client config")
        return False
    if len(config) > 0: 
        if not os.path.isfile(config[0]):
            print("Error: Not Found Config[{}]".format(config[0]))
            return False
        f = open(DEFAULT_CONFIG, 'r')
        conf = json.load(f)
        gcp_jp_data = _create_instance_jp(conf, config[0])
        gcp_tw_data = _create_instance_tw(conf, gcp_jp_data["config"])
        print("VPN-PROXY is Ready. Please download this file:")
        print("\t" + gcp_tw_data)

if len(sys.argv) > 1:
    if sys.argv[1] == "install":
        if len(sys.argv) > 2: 
            install(sys.argv[2:])
        else:
            install()
    else:
        usage()
else:
    usage()



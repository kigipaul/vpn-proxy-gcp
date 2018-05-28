#!/usr/bin/env python3
import sys
import os
import json
import random
import uuid
import re

ROOT_PATH = os.path.dirname(sys.argv[0])
DEFAULT_CONFIG = "{}/config/lower.json".format(ROOT_PATH)
PATTERN_IPv4 = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"
ZONE_TW = "asia-east1-"
ZONE_JP = "asia-northeast1-"
ZONE_L = "abc"

def help():
    print("Usage: {} install [gcp_config]".format(sys.argv[0]))
    print("")
    print("gcp_config: create instance data with config. (Default: {})"\
            .format(DEFAULT_CONFIG))
    print("")

def _create_instanse_jp(conf, client_conf):
    # Create GCP-JP
    uid = "".join(random.sample(list(uuid.uuid4().hex), 8))
    name = "gcp-jp-{}".format(uid)
    conf['boot-disk-device-name'] = "gcpjpdisk-{}".format(uid)
    conf['zone'] = ZONE_JP + random.sample(list(ZONE_L), 1)[0]

    cmd = "gcloud compute instances create {}".format(name)
    for (key, val) in conf.items():
        if type(val) == bool:
            if val:
                cmd += " --{}".format(key)
        else:
            cmd += " --{} {}".format(key, val)
    exe = os.system(cmd) 
    # Get GCP-JP internal IP
    index = 4
    if "" in conf:
        if conf[]:
            index = 5
    cmd = "gcloud compute instances list|grep \"{}\"|awk '{print ${}}'".format(name, index)
    gcp_jp_ip = os.popen(cmd).read()[:-1]
    return gcp_jp_ip

def _create_instanse_tw(conf, gcp_jp_ip):
    # Create GCP-TW
    uid = "".join(random.sample(list(uuid.uuid4().hex), 8))
    name = "gcp-tw-{}".format(uid)
    conf['boot-disk-device-name'] = "gcptwdisk-{}".format(uid)
    conf['zone'] = ZONE_TW + random.sample(list(ZONE_L), 1)[0]

    cmd = "gcloud compute instances create {}".format(name)
    for (key, val) in conf.items():
        cmd += " --{} {}".format(key, val)
    exe = os.system(cmd) 
    # Get GCP-TW external IP
    index = 5
    if "" in conf:
        if conf[]:
            index = 6
    cmd = "gcloud compute instances list|grep \"{}\"|awk '{print $6}'".format(name)
    gcp_tw_ip = os.popen(cmd).read()[:-1]

def install(config=None):
    if config is None:
        config = [DEFAULT_CONFIG]
    if len(config) == 1:  # Create Instances with the same setting
        f = open(config[0], 'r')
        conf = json.load(f)
        gcp_jp_ip = _create_instance_jp(conf, client_conf)
        vpn_dl_path = _create_instance_tw(conf, gcp_jp_ip)

if len(sys.argv) > 1:
    if sys.argv[1] == "install":
        if len(sys.argv) > 2: 
            install(sys.argv[2:])
        else:
            install()
    else:
        help()
else:
    help()



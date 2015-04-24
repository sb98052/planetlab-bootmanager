#!/usr/bin/python
#
# Copyright (c) 2003 Intel Corporation
# All rights reserved.
#
# Copyright (c) 2004-2006 The Trustees of Princeton University
# All rights reserved.
# expected /proc/partitions format

import os
import os.path

from Exceptions import *
import utils
import BootAPI
import ModelOptions

def Run(vars, log):

    """
    Writes out the following configuration files for the node:
    /etc/fstab
    /etc/resolv.conf (if applicable)
    /etc/ssh/ssh_host_key
    /etc/ssh/ssh_host_rsa_key
    /etc/ssh/ssh_host_dsa_key
    
    Expect the following variables from the store:
    VERSION                 the version of the install
    SYSIMG_PATH             the path where the system image will be mounted
                            (always starts with TEMP_PATH)
    PARTITIONS              dictionary of generic part. types (root/swap)
                            and their associated devices.
    PLCONF_DIR              The directory to store the configuration file in
    INTERFACE_SETTINGS  A dictionary of the values from the network
                                configuration file
    Sets the following variables:
    None
    
    """

    log.write( "\n\nStep: Install: Writing configuration files.\n")
    
    # make sure we have the variables we need
    try:
        VERSION = vars["VERSION"]
        if VERSION == "":
            raise ValueError("VERSION")

        SYSIMG_PATH = vars["SYSIMG_PATH"]
        if SYSIMG_PATH == "":
            raise ValueError("SYSIMG_PATH")

        PARTITIONS = vars["PARTITIONS"]
        if PARTITIONS == None:
            raise ValueError("PARTITIONS")

        PLCONF_DIR = vars["PLCONF_DIR"]
        if PLCONF_DIR == "":
            raise ValueError("PLCONF_DIR")

        INTERFACE_SETTINGS = vars["INTERFACE_SETTINGS"]
        if INTERFACE_SETTINGS == "":
            raise ValueError("INTERFACE_SETTINGS")

    except KeyError, var:
        raise BootManagerException("Missing variable in vars: {}\n".format(var))
    except ValueError, var:
        raise BootManagerException("Variable in vars, shouldn't be: {}\n".format(var))

    log.write("Setting local time to UTC\n")
    utils.sysexec_chroot(SYSIMG_PATH,
        "ln -sf /usr/share/zoneinfo/UTC /etc/localtime", log)

    log.write("Creating system directory {}\n".format(PLCONF_DIR))
    if not utils.makedirs("{}/{}".format(SYSIMG_PATH, PLCONF_DIR)):
        log.write("Unable to create directory\n")
        return 0

    log.write("Writing system /etc/fstab\n")
    fstab = file("{}/etc/fstab".format(SYSIMG_PATH), "w")
    fstab.write("{}           none        swap      sw        0 0\n"\
                .format(PARTITIONS["mapper-swap"]))
    fstab.write("{}           /           ext3      defaults  1 1\n"\
                .format(PARTITIONS["mapper-root"]))
    if (vars['ONE_PARTITION'] != '1'):
        if vars['virt'] == 'vs':
            fstab.write("{}           /vservers   ext3      tagxid,defaults  1 2\n"\
                        .format(PARTITIONS["mapper-vservers"]))
        else:
            fstab.write("{}           /vservers   btrfs     defaults  1 2\n"\
                        .format(PARTITIONS["mapper-vservers"]))
    fstab.write("none         /proc       proc      defaults  0 0\n")
    fstab.write("none         /dev/shm    tmpfs     defaults  0 0\n")
    fstab.write("none         /dev/pts    devpts    defaults  0 0\n")
    fstab.close()

    log.write("Writing system /etc/issue\n")
    issue= file("{}/etc/issue".format(SYSIMG_PATH), "w")
    issue.write("PlanetLab Node: \\n\n")
    issue.write("Kernel \\r on an \\m\n")
    issue.write("http://www.planet-lab.org\n\n")
    issue.close()

    if (vars['ONE_PARTITION'] != '1'):
        log.write("Setting up authentication (non-ssh)\n")
        utils.sysexec_chroot(SYSIMG_PATH, "authconfig --nostart --kickstart --enablemd5 " \
                       "--enableshadow", log)
        utils.sysexec("sed -e 's/^root\:\:/root\:*\:/g' " \
                       "{}/etc/shadow > {}/etc/shadow.new".format(SYSIMG_PATH, SYSIMG_PATH), log)
        utils.sysexec_chroot(SYSIMG_PATH, "mv " \
                       "/etc/shadow.new /etc/shadow", log)
        utils.sysexec_chroot(SYSIMG_PATH, "chmod 400 /etc/shadow", log)

    # if we are setup with dhcp, copy the current /etc/resolv.conf into
    # the system image so we can run programs inside that need network access
    method = ""
    try:
        method = vars['INTERFACE_SETTINGS']['method']
    except:
        pass
    
    if method == "dhcp":
        utils.sysexec("cp /etc/resolv.conf {}/etc/".format(SYSIMG_PATH), log)

    log.write("Writing node install version\n")
    utils.makedirs("{}/etc/planetlab".format(SYSIMG_PATH))
    ver = file("{}/etc/planetlab/install_version".format(SYSIMG_PATH), "w")
    ver.write("{}\n".format(VERSION))
    ver.close()

    # for upgrades : do not overwrite already existing keys 
    log.write("Creating ssh host keys\n")
    key_gen_prog = "/usr/bin/ssh-keygen"

    key_specs = [
        ("/etc/ssh/ssh_host_key",     'rsa1', "SSH1 RSA"),
        ("/etc/ssh/ssh_host_rsa_key", 'rsa',  "SSH2 RSA"),
        ("/etc/ssh/ssh_host_dsa_key", 'dsa',  "SSH2 DSA"),
    ]

    for key_file, key_type, label in key_specs:
        abs_file = "{}/{}".format(SYSIMG_PATH, key_file)
        if not os.path.exists(abs_file):
            log.write("Generating {} host key {}\n".format(label, key_file))
            utils.sysexec_chroot(SYSIMG_PATH, "{} -q -t rsa1 -f {} -C '' -N ''"\
                                 .format(key_gen_prog, key_file), log)
            utils.sysexec("chmod 600 {}/{}".format(SYSIMG_PATH, key_file), log)
            utils.sysexec("chmod 644 {}/{}.pub".format(SYSIMG_PATH, key_file), log)

    return 1

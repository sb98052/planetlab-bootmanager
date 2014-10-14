#!/usr/bin/python
#
# Copyright (c) 2003 Intel Corporation
# All rights reserved.
#
# Copyright (c) 2004-2006 The Trustees of Princeton University
# All rights reserved.
# expected /proc/partitions format

import os, string
import traceback

import utils
import urlparse
import httplib

from Exceptions import *
import BootServerRequest
import ModelOptions
import BootAPI
import plnet

class BootAPIWrap:
    def __init__(self, vars):
        self.vars = vars
    def call(self, func, *args):
        return BootAPI.call_api_function(self.vars, func, args)
    def __getattr__(self, func):
        return lambda *args: self.call(func, *args)

class logger:
    def __init__(self, log):
        self._log = log
    def log(self, msg, level=3):
        self._log.write(msg + "\n")
    def verbose(self, msg):
        self.log(msg, 0)

def Run( vars, log ):
    """
    Write out the network configuration for this machine:
    /etc/hosts
    /etc/sysconfig/network-scripts/ifcfg-<ifname>
    /etc/resolv.conf (if applicable)
    /etc/sysconfig/network

    The values to be used for the network settings are to be set in vars
    in the variable 'INTERFACE_SETTINGS', which is a dictionary
    with keys:

     Key               Used by this function
     -----------------------------------------------
     node_id
     node_key
     method            x
     ip                x
     mac               x (optional)
     gateway           x
     network           x
     broadcast         x
     netmask           x
     dns1              x
     dns2              x (optional)
     hostname          x
     domainname        x

    Expect the following variables from the store:
    SYSIMG_PATH             the path where the system image will be mounted
                                (always starts with TEMP_PATH)
    INTERFACES              All the interfaces associated with this node
    INTERFACE_SETTINGS      dictionary 
    Sets the following variables:
    None
    """

    log.write( "\n\nStep: Install: Writing Network Configuration files.\n" )

    try:
        SYSIMG_PATH= vars["SYSIMG_PATH"]
        if SYSIMG_PATH == "":
            raise ValueError, "SYSIMG_PATH"

    except KeyError, var:
        raise BootManagerException, "Missing variable in vars: %s\n" % var
    except ValueError, var:
        raise BootManagerException, "Variable in vars, shouldn't be: %s\n" % var


    try:
        INTERFACE_SETTINGS= vars['INTERFACE_SETTINGS']
    except KeyError, e:
        raise BootManagerException, "No interface settings found in vars."

    try:
        hostname= INTERFACE_SETTINGS['hostname']
        domainname= INTERFACE_SETTINGS['domainname']
        method= INTERFACE_SETTINGS['method']
        ip= INTERFACE_SETTINGS['ip']
        gateway= INTERFACE_SETTINGS['gateway']
        network= INTERFACE_SETTINGS['network']
        netmask= INTERFACE_SETTINGS['netmask']
        dns1= INTERFACE_SETTINGS['dns1']
        mac= INTERFACE_SETTINGS['mac']
    except KeyError, e:
        raise BootManagerException, "Missing value %s in interface settings." % str(e)

    # dns2 is not required to be set
    dns2 = INTERFACE_SETTINGS.get('dns2','')

    # Node Manager needs at least PLC_API_HOST and PLC_BOOT_HOST
    log.write("Writing /etc/planetlab/plc_config\n")
    utils.makedirs("%s/etc/planetlab" % SYSIMG_PATH)
    plc_config = file("%s/etc/planetlab/plc_config" % SYSIMG_PATH, "w")

    api_url = vars['BOOT_API_SERVER']
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(api_url)
    parts = netloc.split(':')
    host = parts[0]
    if len(parts) > 1:
        port = parts[1]
    else:
        port = '80'
    try:
        log.write("getting via https://%s/PlanetLabConf/get_plc_config.php " % host)
        bootserver = httplib.HTTPSConnection(host, int(port))
        bootserver.connect()
        bootserver.request("GET","https://%s/PlanetLabConf/get_plc_config.php" % host)
        plc_config.write("%s" % bootserver.getresponse().read())
        bootserver.close()
        log.write("Done\n")
    except :
        log.write(" .. Failed.  Using old method. -- stack trace follows\n")
        traceback.print_exc(file=log.OutputFile)
        bs= BootServerRequest.BootServerRequest(vars)
        if bs.BOOTSERVER_CERTS:
            print >> plc_config, "PLC_BOOT_HOST='%s'" % bs.BOOTSERVER_CERTS.keys()[0]
        print >> plc_config, "PLC_API_HOST='%s'" % host
        print >> plc_config, "PLC_API_PORT='%s'" % port
        print >> plc_config, "PLC_API_PATH='%s'" % path

    plc_config.close()


    log.write( "Writing /etc/hosts\n" )
    hosts_file= file("%s/etc/hosts" % SYSIMG_PATH, "w" )    
    hosts_file.write( "127.0.0.1       localhost\n" )
    if method == "static":
        hosts_file.write( "%s %s.%s\n" % (ip, hostname, domainname) )
    hosts_file.close()
    hosts_file= None
    
    data =  {'hostname': '%s.%s' % (hostname, domainname),
             'networks': vars['INTERFACES']}
    plnet.InitInterfaces(logger(log), BootAPIWrap(vars), data, SYSIMG_PATH,
                         True, "BootManager")


#!/usr/bin/python
#

import os

from Exceptions import *
import utils
import systeminfo

def run_ansible(ansible_path, ansible_hash, playbook_name, log):
    try:
        if (ansible_hash):
            hash_arg = '-U %s'%ansible_hash
        else:
            hash_arg = ''
        utils.sysexec_noerr('ansible-pull -i hosts %s %s %s' % (ansible_path, hash_arg, playbook_name), log )
    except:
        pass


def Run( vars, log ):
    log.write( "\n\nStep: Running Ansible Hook\n" )
    # make sure we have the variables we need
    try:
        ansible_path = vars["ANSIBLE_PATH"]
        run_level = vars["RUN_LEVEL"]
        try:
            ansible_hash = vars["ANSIBLE_HASH"]
        except KeyError:
            ansible_hash = None

        if (ansible_path):
            run_ansible(ansible_path, ansible_hash, "%s.yml"%run_level, log)
    except KeyError, var:
        log.write( "No Ansible directive. Skipping.\n");
        pass

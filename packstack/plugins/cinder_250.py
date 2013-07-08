"""
Installs and configures Cinder
"""

import os
import uuid
import logging

from packstack.installer import exceptions
from packstack.installer import validators

from packstack.installer import basedefs
from packstack.installer import utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile
from packstack.installer.exceptions import ScriptRuntimeError
from packstack.installer import output_messages

# Controller object will
# be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Cinder configuration")
    paramsList = [
                  {"CMD_OPTION"      : "cinder-host",
                   "USAGE"           : "The IP address of the server on which to install Cinder",
                   "PROMPT"          : "Enter the IP address of the Cinder server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-db-passwd",
                   "USAGE"           : "The password to use for the Cinder to access DB",
                   "PROMPT"          : "Enter the password for the Cinder DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-ks-passwd",
                   "USAGE"           : "The password to use for the Cinder to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Cinder Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-volumes-create",
                   "USAGE"           : ("Create Cinder's volumes group. This should only be done for "
                                        "testing on a proof-of-concept installation of Cinder.  This "
                                        "will create a file-backed volume group and is not suitable "
                                        "for production usage."),
                   "PROMPT"          : ("Should Cinder's volumes group be created (for proof-of-concept "
                                        "installation)?"),
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_CREATE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "CINDER",
                  "DESCRIPTION"           : "Cinder Config parameters",
                  "PRE_CONDITION"         : "CONFIG_CINDER_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    def check_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') ==
                config.get('CONFIG_CINDER_VOLUMES_CREATE', 'n') == 'y')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-volumes-size",
                   "USAGE"           : "Cinder's volumes group size",
                   "PROMPT"          : "Enter Cinder's volumes group size",
                   "OPTION_LIST"     : [],
                   "VALIDATORS" : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "20G",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_SIZE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "CINDERVOLUMECREATE",
                  "DESCRIPTION"           : "Cinder volume create Config parameters",
                  "PRE_CONDITION"         : check_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_CINDER_INSTALL'] != 'y':
        return

    cinder_steps = [
             {'title': 'Adding Cinder Keystone manifest entries', 'functions':[create_keystone_manifest]},
             {'title': 'Installing dependencies for Cinder', 'functions':[install_cinder_deps]},
             {'title': 'Checking if the Cinder server has a cinder-volumes vg', 'functions':[check_cinder_vg]},
             {'title': 'Adding Cinder manifest entries', 'functions':[create_manifest]}
    ]
    controller.addSequence("Installing OpenStack Block Storage (Cinder)", [], [], cinder_steps)

def install_cinder_deps(config):
    server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
    server.append("rpm -q %(package)s || yum install -y %(package)s" % {'package': "lvm2"})
    server.execute()

def check_cinder_vg(config):

    cinders_volume = 'cinder-volumes'

    # Do we have a cinder-volumes vg?
    have_cinders_volume = False
    server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
    server.append('vgdisplay %s' % cinders_volume)
    try:
        server.execute()
        have_cinders_volume = True
    except ScriptRuntimeError:
        pass

    # Configure system LVM settings (snapshot_autoextend)
    server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
    server.append('sed -i -r "s/^ *snapshot_autoextend_threshold +=.*/'
                  '    snapshot_autoextend_threshold = 80/" '
                  '/etc/lvm/lvm.conf')
    server.append('sed -i -r "s/^ *snapshot_autoextend_percent +=.*/'
                  '    snapshot_autoextend_percent = 20/" '
                  '/etc/lvm/lvm.conf')
    try:
        server.execute()
    except ScriptRuntimeError:
        logging.info("Warning: Unable to set system LVM settings.")


    if controller.CONF["CONFIG_CINDER_VOLUMES_CREATE"] != "y":
        if not have_cinders_volume:
            raise exceptions.MissingRequirements("The cinder server should"
                " contain a cinder-volumes volume group")
    else:
        if have_cinders_volume:
            controller.MESSAGES.append(
                output_messages.INFO_CINDER_VOLUMES_EXISTS)
            return

        server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
        server.append('systemctl')
        try:
            server.execute()
            rst_cmd = 'systemctl restart openstack-cinder-volume.service'
        except ScriptRuntimeError:
            rst_cmd = 'service openstack-cinder-volume restart'

        server.clear()
        logging.info("A new cinder volumes group will be created")
        err = "Cinder's volume group '%s' could not be created" % \
                            cinders_volume

        cinders_volume_path = '/var/lib/cinder'
        server.append('mkdir -p  %s' % cinders_volume_path)
        logging.debug("Volume's path: %s" % cinders_volume_path)

        cinders_volume_path = os.path.join(cinders_volume_path, cinders_volume)
        server.append('dd if=/dev/zero of=%s bs=1 count=0 seek=%s' % \
            (cinders_volume_path,
             controller.CONF['CONFIG_CINDER_VOLUMES_SIZE']))
        server.append('LOFI=$(losetup --show -f  %s)' % cinders_volume_path)
        server.append('pvcreate $LOFI')
        server.append('vgcreate %s $LOFI' % cinders_volume)

        # Add the loop device on boot
        server.append('grep %(volume)s /etc/rc.d/rc.local || '
                      'echo "losetup -f %(path)s && '
                            'vgchange -a y %(volume)s && '
                            '%(restart_cmd)s" '
                      '>> /etc/rc.d/rc.local' %
                      {'volume': cinders_volume, 'restart_cmd': rst_cmd,
                       'path': cinders_volume_path})
        server.append('grep "#!" /etc/rc.d/rc.local || '
                      'sed -i \'1i#!/bin/sh\' /etc/rc.d/rc.local')
        server.append('chmod +x /etc/rc.d/rc.local')

        # Let's make sure it exists
        server.append('vgdisplay %s' % cinders_volume)

        try:
            server.execute()
        except ScriptRuntimeError:
            # Release loop device if cinder's volume creation
            # fails.
            try:
                logging.debug("Release loop device, volume creation failed")
                server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
                server.append('losetup -d $(losetup -j %s | cut -d : -f 1)' %
                               cinders_volume_path
                )
                server.execute()
            except:
                pass

            raise exceptions.MissingRequirements(err)


def create_keystone_manifest(config):
    manifestfile = "%s_keystone.pp" % controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_cinder.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config):
    manifestfile = "%s_cinder.pp" % controller.CONF['CONFIG_CINDER_HOST']
    manifestdata = getManifestTemplate("cinder.pp")
    appendManifestFile(manifestfile, manifestdata)

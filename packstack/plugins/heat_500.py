"""
Installs and configures heat
"""

import uuid
import logging
import os

from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.ospluginutils import (getManifestTemplate,
                                             manifestfiles,
                                             appendManifestFile)

controller = None

# Plugin name
PLUGIN_NAME = "OS-HEAT"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Heat configuration")
    parameters = [
        {"CMD_OPTION"      : "heat-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat service'),
         "PROMPT"          : 'Enter the IP address of the Heat server',
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-api-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat API service'),
         "PROMPT"          : 'Enter the IP address of the Heat API server',
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_API_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-api-cfn-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat Cloud Formation API service'),
         "PROMPT"          : 'Enter the IP address of the Heat Cloud Formation API server',
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_API_CFN_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-api-cloudwatch-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat Cloud Watch API service'),
         "PROMPT"          : 'Enter the IP address of the Heat CloudWatch API server',
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_API_CLOUDWATCH_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-engine-host",
         "USAGE"           : ('The IP address of the server on which '
                              'to install Heat Cloud Watch API service'),
         "PROMPT"          : 'Enter the IP address of the Heat CloudWatch API server',
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_ssh],
         "DEFAULT_VALUE"   : utils.get_localhost_ip(),
         "MASK_INPUT"      : False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME"       : "CONFIG_HEAT_ENGINE_HOST",
         "USE_DEFAULT"     : False,
         "NEED_CONFIRM"    : False,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-mysql-password",
	       "USAGE"	         : 'The password used by Heat user to authenticate against MySQL',
         "PROMPT"          : "Enter the password for the Heat MySQL user",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_DB_PW",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False },

        {"CMD_OPTION"      : "heat-ks-passwd",
         "USAGE"           : "The password to use for the Heat to authenticate with Keystone",
         "PROMPT"          : "Enter the password for the Heat Keystone access",
         "OPTION_LIST"     : [],
         "VALIDATORS"      : [validators.validate_not_empty],
         "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
         "MASK_INPUT"      : True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME"       : "CONFIG_HEAT_KS_PW",
         "USE_DEFAULT"     : True,
         "NEED_CONFIRM"    : True,
         "CONDITION"       : False },
        ]

    group = {"GROUP_NAME"          : "Heat",
             "DESCRIPTION"         : "Heat Config parameters",
             "PRE_CONDITION"       : "CONFIG_HEAT_INSTALL",
             "PRE_CONDITION_MATCH" : "y",
             "POST_CONDITION"      : False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, parameters)


def initSequences(controller):
    if controller.CONF['CONFIG_HEAT_INSTALL'] != 'y':
        return
    steps = [#{'title': 'Doing something before puppet applies manifest',
             # 'function': [prestep]},
             {'title': 'Adding Heat manifest entries',
              'functions': [createmanifest]}]
    controller.addSequence("Installing Heat", [], [], steps)


def createmanifest(config):
    manifestfile = "%s_heat.pp" % controller.CONF['CONFIG_HEAT_HOST']
    manifestdata = getManifestTemplate("heat.pp")
    appendManifestFile(manifestfile, manifestdata, marker='heat')


def prestep(config):
    # You can do whatever you need on heat host before manifest
    # application using:
    # server = utils.ScriptRunner(config['CONFIG_HEAT_HOST'])
    # server.append('some bash command here')
    # ret_code, stdoutdata = server.execute()
    #
    # Analogicaly you can create some poststep function and add it to
    # initSequences
    return

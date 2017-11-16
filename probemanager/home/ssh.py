import subprocess
from django.conf import settings
import logging
from home.utils import decrypt
import os


logger = logging.getLogger(__name__)


def execute(server, commands, become=False):
    result = dict()
    # commands is a dict {'name of command': command}
    for command_name, command in commands.items():
        if become:
            logger.info("OK0")
            if server.ansible_become:
                logger.info("OK1")
                if server.ansible_become_pass is not None:
                    logger.info("OK2")
                    command = " echo '" + decrypt(server.ansible_become_pass).decode('ascii') + \
                              "' | " + server.ansible_become_method + " -S " + \
                              command
                else:
                    command = server.ansible_become_method + " " + command
        command_ssh = 'ssh -o StrictHostKeyChecking=no -p ' + \
                      str(server.ansible_remote_port) + ' -i ' + \
                      settings.MEDIA_ROOT + "/" + \
                      server.ansible_ssh_private_key_file.file.name + ' ' + \
                      server.ansible_remote_user + '@' + \
                      server.host + ' "' + command + ' "'
        logger.info("command_ssh " + command_ssh)
        exitcode, output = subprocess.getstatusoutput(command_ssh)
        logger.info("OK4")
        if exitcode != 0:
            logger.info("OK5")
            raise Exception("Command Failed",
                            "Command: " + command_name +
                            " Exitcode: " + str(exitcode) +
                            " Message: " + str(output)
                            )
        else:
            logger.info("OK6")
            result[command_name] = output
    return result


def execute_copy(server, src, dest, owner=None, group=None, mode=None):
    result = dict()
    command_scp = 'scp -o StrictHostKeyChecking=no -P ' + \
                  str(server.ansible_remote_port) + ' -i ' + \
                  settings.MEDIA_ROOT + "/" + \
                  server.ansible_ssh_private_key_file.file.name + ' ' + \
                  src + ' ' + \
                  server.ansible_remote_user + '@' + \
                  server.host + ':' + dest
    if server.ansible_become:
        command_scp = 'scp -o StrictHostKeyChecking=no -P ' + \
                      str(server.ansible_remote_port) + ' -i ' + \
                      settings.MEDIA_ROOT + "/" + \
                      server.ansible_ssh_private_key_file.file.name + ' ' + \
                      src + ' ' + \
                      server.ansible_remote_user + '@' + \
                      server.host + ':' + os.path.basename(dest)
        exitcode, output = subprocess.getstatusoutput(command_scp)
        if exitcode != 0:
            raise Exception("Command scp Failed",
                            " Exitcode: " + str(exitcode) +
                            " Message: " + str(output)
                            )
        else:
            result['copy'] = output
        commands = {"mv": "mv " + os.path.basename(dest) + " " + dest}
        result['mv'] = execute(server, commands, become=True)['mv']
    else:
        exitcode, output = subprocess.getstatusoutput(command_scp)
        if exitcode != 0:
            raise Exception("Command scp Failed",
                            " Exitcode: " + str(exitcode) +
                            " Message: " + str(output)
                            )
        else:
            result['copy'] = output
    return result
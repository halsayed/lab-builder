from calm.dsl.builtins import basic_cred, CalmTask, action, CalmVariable
from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import read_provider_spec, ref
from calm.dsl.builtins import AhvVmDisk, AhvVmNic
from calm.dsl.builtins import AhvVmGC, AhvVmResources, AhvVm

import inspect
import logging
import os
import sys
import uuid

from jinja2 import Template


def create_provider_spec_from_template(filename, **kwargs):

    with open(filename) as f:
        spec_template = Template(f.read())

    temp_file_name = 'tmp/{}'.format(str(uuid.uuid4()))
    with open(temp_file_name, 'w') as f:
        f.write(spec_template.render(**kwargs))

    return temp_file_name


WIN = basic_cred('administrator', 'nutanix/4u', name='WIN', default=True)


class RemoteDesktopVM(Service):
    """Remote Desktop VM service"""
    pass


class RemoteDesktopPackage(Package):
    """Remote Desktop Package"""

    services = [ref(RemoteDesktopVM)]


class RemoteDesktopVMS(Substrate):
    """Remote Desktop Substrate"""

    # provider_spec = read_provider_spec('templates/windows_vm.yaml')
    provider_spec = read_provider_spec(create_provider_spec_from_template('templates/windows_vm.yaml',
                                                                          gc_file='templates/remote_desktop.xml'))
    readiness_probe = {
        'disabled': True,
        'delay_secs': '0',
        'connection_type': 'POWERSHELL',
        'connection_port': 5985,
        'credential': ref(WIN)
    }
    os_type = 'Windows'

    @action
    def __pre_create__(self):
        CalmTask.SetVariable.escript(name='set lab network', filename='scripts/set_network_uuid.py',
                                     variables=['LAB_NETWORK', 'EXTERNAL_NETWORK'])


class RemoteDesktopDeployment(Deployment):
    """Remote Desktop Deployment"""

    packages = [ref(RemoteDesktopPackage)]
    substrate = ref(RemoteDesktopVMS)


class AHV(Profile):
    """AHV defualt profile"""

    deployments = [RemoteDesktopDeployment]
    LOCAL_IP = CalmVariable.Simple.string('192.168.0.200')


class LabBlueprint(Blueprint):
    """MCSA-240 Blueprint"""

    credentials = [WIN]
    services = [RemoteDesktopVM]
    packages = [RemoteDesktopPackage]
    substrates = [RemoteDesktopVMS]
    profiles = [AHV]


def main():
    print(LabBlueprint.json_dumps(pprint=True))


if __name__ == '__main__':
    main()
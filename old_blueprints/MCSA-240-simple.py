from calm.dsl.builtins import basic_cred, CalmTask, action, CalmVariable
from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import read_provider_spec, ref
from calm.dsl.builtins import AhvVmDisk, AhvVmNic
from calm.dsl.builtins import AhvVmGC, AhvVmResources, AhvVm


WIN = basic_cred('administrator', 'nutanix/4u', name='WIN', default=True)


# class RemoteDesktopVmResources(AhvVmResources):
#
#     memory = 4
#     vCPUs = 2
#     cores_per_vCPU = 1
#     disks = [AhvVmDisk.Disk.Scsi.cloneFromImageService('Windows 2016', bootable=True)]
#     nics = [AhvVmNic.DirectNic.ingress('PUBLIC'), AhvVmNic.DirectNic.ingress('@@{MY_NET}@@')]
#     guest_customization = AhvVmGC.Sysprep.PreparedScript(filename='guest_custom/remote_desktop.xml')
#
#
# class RemoteDesktopVm(AhvVm):
#     resources = RemoteDesktopVmResources


class RemoteDesktopDeployment(SimpleDeployment):
    provider_spec = read_provider_spec('templates/windows_vm.yaml')
    # provider_spec = RemoteDesktopVm
    readiness_probe = {
        'disabled': True,
        'delay_secs': '0',
        'connection_type': 'POWERSHELL',
        'connection_port': 5985,
        'credentials': ref(WIN)
    }
    os_type = 'Windows'

    @action
    def __pre_create__(self):
        CalmTask.SetVariable.escript(name='set lab network', filename='scripts/set_network_uuid.py', variables=['MY_NET'])


class LabBlueprint(SimpleBlueprint):
    credentials = [WIN]
    deployments = [RemoteDesktopDeployment]
    LOCAL_IP = CalmVariable.Simple.string('192.168.0.200')


def main():
    print(LabBlueprint.json_dumps(pprint=True))


if __name__ == '__main__':
    main()
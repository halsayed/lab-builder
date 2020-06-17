from calm.dsl.builtins import basic_cred
from calm.dsl.builtins import SimpleBlueprint, SimpleDeployment
from calm.dsl.builtins import AhvVmDisk, AhvVmNic, AhvVmGC, AhvVmResources, AhvVm, read_provider_spec
from calm.dsl.builtins import CalmVariable, ref

LAB_DEFAULT = basic_cred('centos', 'nutanix/4u', name='LAB_DEFAULT', default=True)
DOMAIN_ADMIN = basic_cred('administrator@tvtc.lab', 'nx2Tech911!', name='DOMAIN_ADMIN', default=False)
PC_ACCOUNT = basic_cred('admin', 'nx2Tech911!', name='PC_ACCOUNT', default=False)


# class CentosVmResource(AhvVmResources):
#
#     memory = 4
#     vCPUs = 2
#     cores_per_vCPU = 1
#     disks = [AhvVmDisk.Disk.Scsi.cloneFromImageService('centos-8', bootable=True)]
#     nics = [AhvVmNic.NormalNic.ingress('External')]
#     # nics[0]['subnet_reference']['name'] = 'External'
#     # nics[0]['subnet_reference']['uuid'] = 'd4c10abe-e8b2-483f-bb84-a4e7157f919c'
#     guest_customization = AhvVmGC.CloudInit(
#         config = {
#             'password': 'nutanix/4u',
#             'ssh_pwauth': True,
#             'chpasswd': { 'expire': False }
#         }
#     )
#
#
# class CentosVm(AhvVm):
#     resources = CentosVmResource


class LabDeployment(SimpleDeployment):
    # provider_spec = CentosVm
    provider_spec = read_provider_spec('templates/spec-centos-8.yaml')
    os_type = 'Linux'
    readiness_probe = {
        'disabled': True,
        'delay_secs': '0',
        'connection_type': 'SSH',
        'connection_port': 22,
        # 'credential': ref(LAB_DEFAULT)
    }


class MCSA(SimpleBlueprint):
    credentials = [LAB_DEFAULT]
    deployments = [LabDeployment]


def main():
    print(MCSA.json_dumps(pprint=True))


if __name__ == '__main__':
    main()

from calm.dsl.builtins import basic_cred, CalmTask, action
from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import AhvVmDisk, AhvVmNic
from calm.dsl.builtins import AhvVmGC, AhvVmResources, AhvVm


LOCAL_CENTOS = basic_cred('centos', 'nutanix/4u', name='LOCAL_CENTOS', default=True)


class CentosVmResources(AhvVmResources):

    memory = 4
    vCPUs = 2
    cores_per_vCPU = 1
    disks = [AhvVmDisk.Disk.Scsi.cloneFromImageService('CentOS 8', bootable=True)]
    nics = [AhvVmNic.DirectNic.ingress("PUBLIC")]
    guest_customization = AhvVmGC.CloudInit(
        config={
            'password': 'nutanix/4u',
            'ssh_pwauth': True,
            'chpasswd': { 'expire': False }
        }
    )


class CentosVm(AhvVm):
    resources = CentosVmResources


class ApacheDeployment(SimpleDeployment):
    # provider_spec = read_provider_spec('vm_spec.yaml')
    provider_spec = CentosVm
    os_type = 'Linux'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='Update CentOS', script='sudo yum -y --quiet update')
        CalmTask.Exec.ssh(name='Install apache', filename='scripts/installApache.sh')


class ApacheBlueprint(SimpleBlueprint):
    credentials = [LOCAL_CENTOS]
    deployments = [ApacheDeployment]


def main():
    print(ApacheBlueprint.json_dumps(pprint=True))


if __name__ == '__main__':
    main()
from calm.dsl.builtins import basic_cred, CalmTask, action, CalmVariable
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import read_provider_spec, ref, read_local_file

local_password = read_local_file('local_password')
domain_password = read_local_file('domain_password')
LAB_DEFAULT = basic_cred('administrator', local_password, name='LAB_DEFAULT', default=True)
DOMAIN_ADMIN = basic_cred('administrator@lab.demo', domain_password, name='DOMAIN_ADMIN', default=False)


# ================================================================================
# ==== Remote Desktop VM with dual nics                                       ====
# ================================================================================
class RemoteVM(Service):
    """Remote Desktop VM service"""

    OWNER = CalmVariable.Simple('', runtime=False)
    DIRECTORY_UUID = CalmVariable.Simple('', runtime=False)

    @action
    def __create__(self):
        CalmTask.SetVariable.escript(filename='scripts/get_vm_owner_username.py', name='get owner username',
                                     variables=['OWNER'])
        CalmTask.SetVariable.escript(name='get directory uuid', filename='scripts/get_directory_uuid.py',
                                     variables=['DIRECTORY_UUID'])
        CalmTask.Exec.powershell(filename='scripts/join_domain.ps1', name='join domain', cred=LAB_DEFAULT)
        CalmTask.Delay(delay_seconds=60, name='wait for domain')
        CalmTask.Exec.powershell(script='Add-LocalGroupMember -Group "Administrators" -Member @@{OWNER}@@',
                                 name='add owner to local admin', cred=DOMAIN_ADMIN)
        CalmTask.Exec.escript(filename='scripts/set_prism_owner.py', name='set prism owner')


class RemotePackage(Package):
    """Remote Desktop Package"""

    services = [ref(RemoteVM)]


class RemoteVMS(Substrate):
    """Remote Desktop Substrate"""

    provider_spec = read_provider_spec('templates/remote_desktop_vm.yaml')

    readiness_probe = {
        'disabled': True,
        'connection_type': 'POWERSHELL',
        'connection_port': 5985,
        'credential': ref(LAB_DEFAULT)
    }
    os_type = 'Windows'

    @action
    def __pre_create__(self):
        CalmTask.SetVariable.escript(name='set lab network', filename='scripts/set_network_uuid.py',
                                     variables=['LAB_NETWORK', 'EXTERNAL_NETWORK'])


class RemoteDeployment(Deployment):
    """Remote Desktop Deployment"""

    packages = [ref(RemotePackage)]
    substrate = ref(RemoteVMS)
    min_replicas = '@@{COUNT}@@'


# ================================================================================
# ==== Lab VMs                                                                ====
# ================================================================================

# DC1 Components
class DC1VM(Service):
    """DC1 VM service"""
    pass


class DC1Package(Package):
    """DC1 Package"""

    services = [ref(DC1VM)]


class DC1VMS(Substrate):
    """DC1 Substrate"""

    provider_spec = read_provider_spec('templates/mcsa-20-41-DC1.yaml')

    readiness_probe = {
        'disabled': True,
        'connection_type': 'POWERSHELL',
        'connection_port': 5985,
        'credential': ref(LAB_DEFAULT)
    }
    os_type = 'Windows'

    @action
    def __pre_create__(self):
        CalmTask.SetVariable.escript(name='set lab network', filename='scripts/set_network_uuid.py',
                                     variables=['LAB_NETWORK'])


class DC1Deployment(Deployment):
    """DC1 Deployment"""

    packages = [ref(DC1Package)]
    substrate = ref(DC1VMS)
    min_replicas = '@@{COUNT}@@'


# SRV1 Components
class SRV1VM(Service):
    """SRV1 VM service"""
    pass


class SRV1Package(Package):
    """SRV1 Package"""

    services = [ref(SRV1VM)]


class SRV1VMS(Substrate):
    """SRV1 Substrate"""

    provider_spec = read_provider_spec('templates/mcsa-20-41-SRV1.yaml')

    readiness_probe = {
        'disabled': True,
        'connection_type': 'POWERSHELL',
        'connection_port': 5985,
        'credential': ref(LAB_DEFAULT)
    }
    os_type = 'Windows'

    @action
    def __pre_create__(self):
        CalmTask.SetVariable.escript(name='set lab network', filename='scripts/set_network_uuid.py',
                                     variables=['LAB_NETWORK'])


class SRV1Deployment(Deployment):
    """SRV1 Deployment"""

    packages = [ref(SRV1Package)]
    substrate = ref(SRV1VMS)
    min_replicas = '@@{COUNT}@@'

# ================================================================================
# ==== Common blueprint components                                            ====
# ================================================================================


class AHV(Profile):
    """AHV defualt profile"""

    deployments = [RemoteDeployment, DC1Deployment, SRV1Deployment]
    LAB_IP_PREFIX = CalmVariable.Simple.string('192.168', runtime=True)
    DOMAIN_NAME = CalmVariable.Simple.string('lab.demo', runtime=True, label='University Domain')
    LIST = CalmVariable.Simple.multiline('', runtime=True, label='Students List')
    COUNT = CalmVariable.WithOptions.Predefined.int(list(map(str, range(1, 21))), default='1', runtime=True,
                                                    label='Lab Seat Count')
    EXTERNAL_NETWORK = CalmVariable.Simple.string('', runtime=False, is_hidden=True)
    LAB_NETWORK = CalmVariable.Simple.string('', runtime=False, is_hidden=True)
    DIRECTORY_UUID = CalmVariable.Simple.string('', runtime=False, is_hidden=True)


class MCSA(Blueprint):
    """MCSA20-410 Blueprint"""

    credentials = [LAB_DEFAULT, DOMAIN_ADMIN]
    services = [RemoteVM, DC1VM, SRV1VM]
    packages = [RemotePackage, DC1Package, SRV1Package]
    substrates = [RemoteVMS, DC1VMS, SRV1VMS]
    profiles = [AHV]


def main():
    print(MCSA.json_dumps(pprint=True))


if __name__ == '__main__':
    main()

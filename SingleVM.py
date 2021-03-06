from calm.dsl.builtins import basic_cred, CalmTask, action, CalmVariable
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import read_provider_spec, ref, read_local_file


local_password = read_local_file('local_password')
domain_password = read_local_file('domain_password')
LAB_DEFAULT = basic_cred('administrator', local_password, name='LAB_DEFAULT', default=True)
DOMAIN_ADMIN = basic_cred('administrator@lab.demo', domain_password, name='DOMAIN_ADMIN', default=False)


# ================================================================================
# ==== Remote Desktop VM with single nic and joined to domain                 ====
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

    provider_spec = read_provider_spec('templates/singleVM_1nic_domain.yaml')

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
                                     variables=['EXTERNAL_NETWORK'])




class RemoteDeployment(Deployment):
    """Remote Desktop Deployment"""

    packages = [ref(RemotePackage)]
    substrate = ref(RemoteVMS)
    min_replicas = '@@{COUNT}@@'


# ================================================================================
# ==== Common blueprint components                                            ====
# ================================================================================


class AHV(Profile):
    """AHV defualt profile"""

    deployments = [RemoteDeployment]
    DOMAIN_NAME = CalmVariable.Simple.string('lab.demo', runtime=True, label='University Domain')
    LIST = CalmVariable.Simple.multiline('', runtime=True, label='Students List')
    COUNT = CalmVariable.WithOptions.Predefined.int(list(map(str, range(1, 21))), default='1', runtime=True,
                                                    label='Lab Seat Count')
    EXTERNAL_NETWORK = CalmVariable.Simple.string('', runtime=False, is_hidden=True)
    DIRECTORY_UUID = CalmVariable.Simple.string('', runtime=False, is_hidden=True)


class SingleVM(Blueprint):
    """Single VM, 1 nic card and joined to domain Blueprint"""

    credentials = [LAB_DEFAULT, DOMAIN_ADMIN]
    services = [RemoteVM]
    packages = [RemotePackage]
    substrates = [RemoteVMS]
    profiles = [AHV]


def main():
    print(SingleVM.json_dumps(pprint=True))


if __name__ == '__main__':
    main()

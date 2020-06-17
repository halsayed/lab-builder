

# api call function
# ================================================================
def http_request(api_endpoint, payload='', method='POST'):
    jwt = '@@{calm_jwt}@@'
    pc_address = '127.0.0.1'
    pc_port = '9440'

    url = "https://{}:{}/api/nutanix/v3/{}".format(
        pc_address,
        pc_port,
        api_endpoint
    )

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(jwt)
    }

    if len(payload) > 0:
        payload = json.dumps(payload)

    resp = urlreq(
        url,
        verb=method,
        params=payload,
        headers=headers,
        verify=False
    )

    if resp.ok:
        return json.loads(resp.content)
    else:
        print('Error in API call')
        exit(1)


def get_user_uuid(username, directory_uuid=None):
    api_endpoint = 'users/list'
    payload = { 'kind': 'user',
                'filter': 'username=={}'.format(username)}
    users = http_request(api_endpoint, payload)
    for user in users['entities']:
        if user['spec']['resources']['directory_service_user']['user_principal_name'] == username:
            return {'username': username, 'uuid': user['metadata']['uuid']}

    # if user not found and directory set then create the user
    if directory_uuid:
        payload = {
            'api_version': '3.1.0',
            'metadata': {
                'kind': 'user'
            },
            'spec': {
                'resources': {
                    'directory_service_user': {
                        'user_principal_name': username,
                        'directory_service_reference': {
                            'kind': 'directory_service',
                            'uuid': directory_uuid
                        }
                    }
                }
            }
        }
        api_endpoint = 'users'
        new_user = http_request(api_endpoint, payload)
        return {'username': username, 'uuid': new_user['metadata']['uuid']}


def update_vm_owner(owner, uuid):
    api_endpoint = 'vms/{}'.format(uuid)

    # get VM info
    vm = http_request(api_endpoint, method='GET')

    # update the VM with the owner info
    del(vm['status'])
    del(vm['metadata']['last_update_time'])
    vm['metadata']['owner_reference']['name'] = owner['username']
    vm['metadata']['owner_reference']['uuid'] = owner['uuid']
    http_request(api_endpoint, payload=vm, method='PUT')


owner_username = '@@{OWNER}@@'
directory_uuid = '@@{DIRECTORY_UUID}@@'
owner_object = get_user_uuid(owner_username)
vm_uuid = '@@{id}@@'
update_vm_owner(owner_object, vm_uuid)




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


current_external_network = '@@{EXTERNAL_NETWORK}@@'
if not current_external_network:
    project_name = '@@{calm_project_name}@@'
    result = http_request('projects/list', {'kind': 'project'})

    network_list = []
    default_network_uuid = None
    for project in result['entities']:
        if project['spec']['name'] == project_name:
            network_list = project['spec']['resources']['subnet_reference_list']
            default_network_uuid = project['spec']['resources']['default_subnet_reference']['uuid']

    lab_network = {}
    external_network = {}
    for network in network_list:
        if network['uuid'] == default_network_uuid:
            lab_network = network
        else:
            external_network = network

    print('LAB_NETWORK={}'.format(json.dumps(lab_network)))
    print('EXTERNAL_NETWORK={}'.format(json.dumps(external_network)))

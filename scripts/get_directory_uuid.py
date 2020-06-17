

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


def get_directory_uuid(domain_name):
    api_endpoint = 'directory_services/list'
    payload = {'filter': '', 'kind': 'directory_service'}
    dirs = http_request(api_endpoint, payload)
    for item in dirs['entities']:
        if item['spec']['resources']['domain_name'] == domain_name:
            return item['metadata']['uuid']

    return None


current_directory_uuid = '@@{DIRECTORY_UUID}@@'
if not current_directory_uuid:
    print('DIRECTORY_UUID={}'.format(get_directory_uuid('@@{DOMAIN_NAME}@@')))

from calm.dsl.cli.bp_commands import create_blueprint_command, create_blueprint_from_dsl, get_api_client


client = get_api_client()
bp_file = 'MCSA-70-240.py'
name = 'MCSA-Blueprint'
description = 'First blueprint'
force = False

res, err = create_blueprint_from_dsl(client, bp_file, name=name, description=description, force_create=force)

print(err)
print(res)

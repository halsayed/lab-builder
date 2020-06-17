
calm_index = int('@@{calm_array_index}@@')
student_list = '''@@{LIST}@@'''
# default_owner = '@@{calm_username}@@'
default_owner = 'husain@lab.demo'

clean_list = [x for x in student_list.splitlines() if x.strip(' ')]
clean_list.insert(0, default_owner)

if calm_index < len(clean_list):
    print('OWNER={}'.format(clean_list[calm_index]))
else:
    print('OWNER={}'.format(default_owner))

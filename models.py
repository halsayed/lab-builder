import inspect
import logging
import os
import sys
import uuid

from jinja2 import Template


def create_provider_spec_from_template(filename, depth=1, **kwargs):

    file_path = os.path.join(os.path.dirname(inspect.getfile(sys._getframe(depth))), filename)
    if not os.path.exists(file_path):
        logging.debug("file {} not found at location {}".format(filename, file_path))
        raise ValueError("file {} not found".format(filename))

    if kwargs.get('gc_file'):
        gc_file_path = os.path.join(os.path.dirname(inspect.getfile(sys._getframe(depth))), kwargs.get('gc_file'))
        if not os.path.exists(file_path):
            logging.debug("file {} not found at location {}".format(kwargs.get('gc_file'), gc_file_path))
            raise ValueError("file {} not found".format(kwargs.get('gc_file')))

        with open(gc_file_path, 'r') as f:
            guest_customization = Template(f.read())
            gc_output = guest_customization.render(kwargs)
    else:
        gc_output = None

    with open(file_path) as f:
        spec_template = Template(f.read())

    temp_file_name = 'tmp/{}'.format(str(uuid.uuid4()))
    with open(temp_file_name, 'w') as f:
        f.write(spec_template.render(guest_customization=gc_output, **kwargs))

    return temp_file_name







    return spec

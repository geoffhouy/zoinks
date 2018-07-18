import json
import logging
import os


logger = logging.getLogger(__name__)


def new_json_file(file_dir: str, file_name: str, init_dict: dict):
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    path = os.path.join(file_dir, file_name)
    if not os.path.isfile(path):
        with open(path, 'w') as file:
            json.dump(init_dict, file, indent=4)

import os.path

import kv_manager
from dotenv import dotenv_values

import const

def manage_kv(path):
    namespace = os.path.basename(path)
    key_values = dotenv_values(path)
    for key, value in key_values.items():
        kv_manager.put_key_value(namespace, key, value)


if __name__ == "__main__":
    manage_kv(f"{const.WORKSPACE_PATH}/secrets.env")
    manage_kv(f"{const.WORKSPACE_PATH}/variables.env")
    manage_kv(f"{const.WORKSPACE_PATH}/ports.env")
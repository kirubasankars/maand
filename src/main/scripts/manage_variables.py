import os.path

import kv_manager
from dotenv import dotenv_values

import const

def manage_kv(path):
    namespace = os.path.basename(path)
    key_values = dotenv_values(path)

    for key, value in key_values.items():
        kv_manager.put_key_value(namespace, key, value)

    all_keys = kv_manager.get_keys(namespace)
    missing_keys = list(set(all_keys) ^ set(key_values.keys()))
    for key in missing_keys:
        kv_manager.delete_key(namespace, key)



if __name__ == "__main__":
    manage_kv(f"{const.WORKSPACE_PATH}/secrets.env")
    manage_kv(f"{const.WORKSPACE_PATH}/variables.env")
    manage_kv(f"{const.WORKSPACE_PATH}/ports.env")
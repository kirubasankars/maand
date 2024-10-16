import os
import shutil

import utils

def test_initialize():
    shutil.rmtree("/workspace/jobs", ignore_errors=True)

    utils.initialize_cluster()

    assert os.path.exists("/workspace/ca.crt")
    assert os.path.exists("/workspace/ca.key")

    assert os.path.exists("/workspace/maand.db")
    assert os.path.exists("/workspace/kv.db")

    assert os.path.exists("/workspace/secrets.env")
    assert os.path.exists("/workspace/variables.env")
    assert os.path.exists("/workspace/command.sh")
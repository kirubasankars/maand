import os
import maand

def test_initialize():

    maand.clean()
    maand.initialize()

    assert os.path.exists("/workspace/ca.crt")
    assert os.path.exists("/workspace/ca.key")
    assert os.path.exists("/workspace/maand.agent.db")
    assert os.path.exists("/workspace/maand.job.db")
    assert os.path.exists("/workspace/kv.db")
    assert os.path.exists("/workspace/secrets.env")
    assert os.path.exists("/workspace/variables.env")
    assert os.path.exists("/workspace/command.sh")
    assert os.path.exists("/workspace/maand.config.env")


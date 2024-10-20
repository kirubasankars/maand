import os

def test_initialize():
    assert os.path.exists("/workspace/ca.crt")
    assert os.path.exists("/workspace/ca.key")

    assert os.path.exists("/workspace/maand.db")
    assert os.path.exists("/workspace/kv.db")

    assert os.path.exists("/workspace/secrets.env")
    assert os.path.exists("/workspace/variables.env")
    assert os.path.exists("/workspace/command.sh")
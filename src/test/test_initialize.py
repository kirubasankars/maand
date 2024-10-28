from utils import *

def test_initialize():
    clean()

    command(get_maand_command("init"))

    assert os.path.exists("/workspace/secrets/ca.crt")
    assert os.path.exists("/workspace/secrets/ca.key")
    assert os.path.exists("/workspace/data/maand.agent.db")
    assert os.path.exists("/workspace/data/kv.db")
    assert os.path.exists("/workspace/secrets/secrets.env")
    assert os.path.exists("/workspace/variables.env")
    assert os.path.exists("/workspace/command.sh")
    assert os.path.exists("/workspace/maand.conf")

def test_initialize_failed():
     r = command(get_maand_command("init"))
     assert r.returncode == 1

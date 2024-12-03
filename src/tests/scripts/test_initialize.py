from utils import *

def test_initialize():
    command("rm -rf /bucket/*")
    command(get_maand_command("init"))

    assert os.path.exists("/bucket/secrets/ca.crt")
    assert os.path.exists("/bucket/secrets/ca.key")
    assert os.path.exists("/bucket/data/maand.db")
    assert os.path.exists("/bucket/data/kv.db")
    assert os.path.exists("/bucket/data/agents.db")
    assert os.path.exists("/bucket/data/jobs.db")
    assert os.path.exists("/bucket/logs")
    assert os.path.exists("/bucket/workspace/secrets.env")
    assert os.path.exists("/bucket/workspace/variables.env")
    assert os.path.exists("/bucket/workspace/command.sh")
    assert os.path.exists("/bucket/maand.conf")

def test_initialize_failed():
     r = command(get_maand_command("init"))
     assert r.returncode == 1

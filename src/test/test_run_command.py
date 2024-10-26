import maand

agents = maand.agents_ip(None)
agents_ip = [item.get("host") for item in agents]

def test_run_command_no_check():
    maand.clean()
    maand.initialize()
    maand.run_command_no_check("ls")

def test_run_command():
    maand.clean()
    maand.initialize()
    maand.build()
    maand.deploy()
    maand.run_command("ls")

def test_run_command_local():
    maand.clean()
    maand.initialize()
    maand.build()
    maand.deploy()
    maand.run_command("ls")


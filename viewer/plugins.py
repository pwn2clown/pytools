class Plugin:
    def __init__(self, name: str, raw_config: dict):
        self.name = name
        self.commands = []

        for raw_cmd in raw_config:
            try:
                self.commands.append(PluginCommand(raw_cmd))
            except Exception as e:
                print(f"failed to load command in plugin {name}")

class PluginCommand:

    def __init__(self, raw_config: dict):
        self.name = raw_config["name"]
        self.cmd_args = raw_config["args"]
        self.cmd_fmt = raw_config["cmd_fmt"]

    def run(self):
        cmd = self.cmd_fmt
        for (arg, value) in self.cmd_args.items():
            cmd = cmd.replace("{{"+arg+"}}", str(value))

        print(cmd)

if __name__ == "__main__":
    raw_config = {
		"name": "start",
		"args": {
			"port": 8080,
			"project_name": "default"
        },
		"cmd_fmt": "mitmdump -s {{PLUGIN_PATH}}/save_request.py -p {{port}} --listen-hort localhost --set project_name={{project_name}}"
    }

    plugin_cmd = PluginCommand(raw_config)
    plugin_cmd.run()

import os,shutil,subprocess
import tempfile

class Plugin:
    first_run = "True"
    
    temp_config = "/dev/null"

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        steam_directory = "/home/deck/.local/share/Steam/"
        config_file = "/config/config.vdf"
        temp = tempfile.NamedTemporaryFile(delete=True)
        shutil.copy2(steam_directory+config_file, temp.name) # for diffing if need be
        if os.path.exists(steam_directory+config_file+".bak"):
            Plugin.first_run = "False"
        # TODO: do not use shutil and use a bash subprocess to copy instead to preserve file info
        if Plugin.first_run:
            shutil.copy(steam_directory+config_file,steam_directory+config_file+".bak") # preserve a backup of our original file jic
        Plugin.temp_config = temp.name
    pass
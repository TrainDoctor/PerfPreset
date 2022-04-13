import os,shutil,subprocess
import tempfile

class Plugin:
    temp_config = "/dev/null"

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        steam_directory = "/home/deck/.local/share/Steam/"
        config_file = "/config/config.vdf"
        temp = tempfile.NamedTemporaryFile(delete=True)
        shutil.copy2(steam_directory+config_file, temp.name) # for diffing if need be
        if not os.path.exists(steam_directory+config_file+".bak"):
            shutil.copy(steam_directory+config_file,steam_directory+config_file+".bak") # preserve a backup of our original file jic
        # TODO: do not use shutil and use a bash subprocess to copy instead to preserve file info
        Plugin.temp_config = temp.name
import collections
import os,shutil,subprocess
import tempfile

subprocess.run(["bash", "install.sh"], cwd="/home/deck/homebrew/plugins/PerfPresets/",capture_output=True)

import vdf

class Plugin:
    temp_config = "/dev/null"
    
    async def get_vdf(self) -> dict:
        return None
    
    def get_perfsettings(self, *args):
        vdf_obj = vdf.parse(open(Plugin.temp_config), mapper=collections.OrderedDict)
        vdf_dict = vdf.VDFDict.get("perf")
        return str(vdf_dict)
    
    # async def python_setup(self):
    #     subprocess.run(["bash", "-c", "install.sh"], capture_output=True)
    #     temp_str = subprocess.CompletedProcess.stdout

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        pass
        # steam_directory = "/home/deck/.local/share/Steam/"
        # config_file = "/config/config.vdf"
        # temp = tempfile.NamedTemporaryFile(delete=True)
        # shutil.copy2(steam_directory+config_file, temp.name) # for diffing if need be
        # if not os.path.exists(steam_directory+config_file+".bak"):
        #     shutil.copy(steam_directory+config_file,steam_directory+config_file+".bak") # preserve a backup of our original file jic
        # # TODO: do not use shutil and use a bash subprocess to copy instead to preserve file info
        # Plugin.temp_config = temp.name
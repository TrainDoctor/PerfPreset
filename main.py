import sys,os,shutil,subprocess,random
import collections,tempfile,pkg_resources

required = {'vdf'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    subprocess.run(["bash", "install.sh"], cwd="/home/deck/homebrew/plugins/PerfPresets/",capture_output=True)
    exit()

import vdf

class Plugin:
    steam_directory = "/home/deck/.local/share/Steam/"
    orig_config = "/home/deck/.local/share/Steam/config/config.vdf"
    temp_config = "/dev/null"
    
    async def get_int(self) -> int:
        out = random.randint(1,10)
        return out
    
    async def get_vdf(self, protected = False) -> dict:
        if protected:
            vdf_obj = vdf.parse(open(Plugin.orig_config, "rt"), mapper=collections.OrderedDict)
        else:
            vdf_obj = vdf.parse(open(Plugin.orig_config, "rt"), mapper=collections.OrderedDict)
        return vdf_obj
    
    def get_perfsettings(self, *args):
        vdf_obj = vdf.parse(open(Plugin.temp_config), mapper=collections.OrderedDict)
        vdf_dict = vdf.VDFDict.get("perf")
        return str(vdf_dict)

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        pass
        # temp = tempfile.NamedTemporaryFile(delete=True)
        # shutil.copy2(steam_directory+config_file, temp.name) # for diffing if need be
        # if not os.path.exists(steam_directory+config_file+".bak"):
        #     shutil.copy(steam_directory+config_file,steam_directory+config_file+".bak") # preserve a backup of our original file jic
        # # TODO: do not use shutil and use a bash subprocess to copy instead to preserve file info
        # Plugin.temp_config = temp.name
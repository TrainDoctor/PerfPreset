import sys,os,shutil,subprocess,random
import collections,tempfile

sys.path.insert(1, "/home/deck/.local/lib/python3.10/site-packages")

try:
    import vdf
except:
    subprocess.run(["bash", "install.sh"], cwd="/home/deck/homebrew/plugins/PerfPresets/",capture_output=True)

class Plugin:
    steam_directory = "/home/deck/.local/share/Steam/"
    orig_config = "/home/deck/.local/share/Steam/config/config.vdf"
    temp_config = "/dev/null"
    
    async def get_vdf(self, protected = False):
        # load vdf file as a python object (dictionary)
        data = None
        with open(Plugin.orig_config, "rt") as file:
            data = file.read()
        if protected:
            vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        else:
            vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        return vdf_obj
    
    # get perf externalized
    async def get_perf_ext(self, obj = vdf.VDFDict):
        # out = obj.get(self, 'perf')
        key = dict.get(obj, "InstallConfigStore")
        key = dict.get(key, "Software")
        key = dict.get(key, "Valve")
        key = dict.get(key, "Steam")
        key = dict.get(key, "perf")
        return str(key)
        # out = []
        # for k,v in 
        #     out += k
        #     if k is 'perf':
        #         return v
        return "NotFound"
    
    # get perf self contained
    async def get_perf_cont(self, protected):
        obj = self.get_vdf(protected)
        out = obj
        return out
        # try:
        #     return vars(obj).get('Software')
        #     for atr,val in vars(obj):
        #         if atr is 'perf':
        #             return val
        #         else:
        #             continue
        #     # out = str(dic)
        #     return "NotFound"
        # except:
        #     return "NotFoundForSure"
    
    # def get_perfsettings(self, *args):
    #     vdf_obj = vdf.parse(open(Plugin.temp_config), mapper=collections.OrderedDict)
    #     vdf_dict = vdf.VDFDict.get("perf")
    #     return str(vdf_dict)

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        pass
        # temp = tempfile.NamedTemporaryFile(delete=True)
        # shutil.copy2(steam_directory+config_file, temp.name) # for diffing if need be
        # if not os.path.exists(steam_directory+config_file+".bak"):
        #     shutil.copy(steam_directory+config_file,steam_directory+config_file+".bak") # preserve a backup of our original file jic
        # # TODO: do not use shutil and use a bash subprocess to copy instead to preserve file info
        # Plugin.temp_config = temp.name
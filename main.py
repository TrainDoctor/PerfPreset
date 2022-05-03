import sys,os,shutil,subprocess,random
import collections,tempfile
import logging

logging.basicConfig(filename="/home/deck/homebrew/perfpresets.log",
					format='%(asctime)s %(levelname)s %(message)s',
					filemode='w',
                    force=True)
logger=logging.getLogger()
logger.setLevel(logging.INFO)

logger.debug("Adding local python libraries to path")
sys.path.insert(1, "/home/deck/.local/lib/python3.10/site-packages")

logger.info("Attempting to import VDF Library")
try:
    import vdf
except:
    logger.error("Could not import vdf library, running install script.\nMake sure to reload the plugin-loader.")
    subprocess.run(["bash", "install.sh"], cwd="/home/deck/homebrew/plugins/PerfPresets/")
    raise ModuleNotFoundError
    # TODO: implement a subprocess that can reload plugin_loader if vdf could not be imported
    # subprocess.run(["sudo", "systemctl", "restart", "plugin_loader.service"])

class Plugin:
    steam_directory = "/home/deck/.local/share/Steam/"
    orig_config = "/home/deck/.local/share/Steam/config/config.vdf"
    game_list = "/home/deck/.local/share/Steam/steamapps/libraryfolders.vdf"
    temp_config = "/dev/null"
    
    def _finditem(self, obj, key):
        if key in obj: 
            logger.debug("Item found, " + str(key) + " " + str(obj[key]))
            return obj[key]
        for k, v in obj.items():
            logger.debug("K: " + str(k))
            if isinstance(v,dict):
                item = self._finditem(self, v, key)
                if item is not None:
                    return item
            elif isinstance(v,list):
                for list_item in v:
                    logger.debug("List Item: " + str(list_item))
                    item = self._finditem(self, list_item, key)
                    if item is not None:
                        return item
    
    async def pretty_perf(self, obj):
        logger.debug("Prettying up: " + str(obj))
        out = ""
        for k,v in obj.items():
            out += str(k) + " " + str(v) + "<br>"
        return out
    
    async def get_vdf(self, isprotected = True):
        # load vdf file as a python object (dictionary)
        data = None
        with open(Plugin.orig_config, "rt") as file:
            data = file.read()
        if isprotected:
            logger.debug("Loading VDF Config. Protecting original file from changes.")
            vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        else:
            logger.warn("Loading VDF Config. Not protecting original file from changes!")
            vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        return vdf_obj
    
    # get perf self contained
    async def get_perf(self, isprotected):
        obj = await self.get_vdf(self,isprotected)
        return self._finditem(self, obj, key="perf")

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        pass
        # temp = tempfile.NamedTemporaryFile(delete=True)
        # shutil.copy2(steam_directory+config_file, temp.name) # for diffing if need be
        # if not os.path.exists(steam_directory+config_file+".bak"):
        #     shutil.copy(steam_directory+config_file,steam_directory+config_file+".bak") # preserve a backup of our original file jic
        # # TODO: do not use shutil and use a bash subprocess to copy instead to preserve file info
        # Plugin.temp_config = temp.name
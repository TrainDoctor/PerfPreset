import sys,os,shutil,subprocess
import collections,tempfile
import logging,traceback

if not os.path.exists("/home/deck/.config/pluginloader/perfpresets"):
    subprocess.run(["mkdir", "-p", "/home/deck/.config/pluginloader/perfpresets/"])

logging.basicConfig(filename="/home/deck/.config/pluginloader/perfpresets/\
                    perfpresets.log",
					format='%(asctime)s %(levelname)s %(message)s',
					filemode='w',
                    force=True)
logger=logging.getLogger()
logger.setLevel(logging.INFO)

def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info()))
    logging.error("Unhandled exception: %s", text)

sys.excepthook = log_except_hook

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

if not os.path.exists("/home/deck/.config/pluginloader/perfpresets"):
    subprocess.run(["mkdir", "-p", "/home/deck/.config/pluginloader/perfpresets/"])
    
class Plugin:
    # steam_directory = "/home/deck/.local/share/Steam/"
    steam_config = "/home/deck/.local/share/Steam/config/config.vdf"
    steam_data = "/home/deck/.steam/registry.vdf"
    preset_location = "/home/deck/.config/perfpresets"
    
    def _finditem(self, obj, key):
        if key in obj: 
            logger.debug("Item found, " + str(key) + " " + str(obj[key]))
            return obj[key]
        for k, v in obj.items():
            logger.debug("K: " + str(k))
            if isinstance(v,dict):
                # logger.debug("Dict Item: " + str(v))
                item = self._finditem(self, v, key)
                if item is not None:
                    return item
            elif isinstance(v,list):
                for list_item in v:
                    # logger.debug("List Item: " + str(list_item))
                    item = self._finditem(self, list_item, key)
                    if item is not None:
                        return item
    
    async def get_vdf(self, vdfile):
        # load vdf file as a python object (dictionary)
        data = None
        with open(vdfile, "rt") as file:
            data = file.read()
        logger.debug("Loading VDF Config. Protecting original file from changes.")
        vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        return vdf_obj
    
    async def get_game(self) -> str:
        obj = await self.get_vdf(self, Plugin.steam_data)
        id = self._finditem(self, obj, key="RunningAppID")
        # TODO: incorporate language detection for smarter name cleanup
        # lang = self._finditem(self, obj, key="language")
        if str(id) == "0":
            return f"Unknown/Unsupported Program<br>ID: {str(id)}"
        else:
            name = self._finditem(self, obj, key=str(id))
            name = str(name.get("name")).encode("ascii", "ignore").decode()
            return f"\"{name}\" ID: {str(id)}"
            
    # get perf self contained
    async def get_perf(self):
        obj = await self.get_vdf(self, Plugin.steam_config)
        return self._finditem(self, obj, key="perf")
    
    async def pretty_perf(self, obj):
        logger.debug("Prettying up: " + str(obj))
        out = ""
        for k,v in obj.items():
            out += str(k) + " " + str(v) + "<br>"
        return out

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        pass
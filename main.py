import json
import re
import sys,os,shutil,subprocess
import collections,tempfile
import logging,traceback
from textwrap import indent

if not os.path.exists("/home/deck/.config/pluginloader/perfpresets"):
    subprocess.run(["mkdir", "-p", "/home/deck/.config/pluginloader/perfpresets/"])

logging.basicConfig(filename="/home/deck/.config/pluginloader/perfpresets/perfpresets.log",
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

# if not os.path.exists("/home/deck/.config/pluginloader/perfpresets"):
#     subprocess.run(["mkdir", "-p", "/home/deck/.config/pluginloader/perfpresets/"])

info_preset =   {   "location":  "/home/deck/.config/pluginloader/perfpresets/",
                    "filename": "presets.json"  }
info_steam =    {   "locationlocal" : "/home/deck/.local/share/Steam",
                    "locationregistry": "/home/deck/.steam",
                    "configpath": "/config/config.vdf",
                    "registryname": "/registry.vdf"  }

class Plugin:

    preset_registry = info_preset.get("location")+info_preset.get("filename")
    steam_config = info_steam.get("locationlocal")+info_steam.get("configpath")
    steam_registry = info_steam.get("locationregistry")+info_steam.get("registryname")
    
    # recursively search through vdf to find a key and it's value
    def _findfirstitem(self, obj, key):
        if key in obj: 
            logger.debug("Item found, " + str(key) + " " + str(obj[key]))
            return obj[key]
        for k, v in obj.items():
            logger.debug("K: " + str(k))
            if isinstance(v,dict):
                # logger.debug("Dict Item: " + str(v))
                item = self._findfirstitem(self, v, key)
                if item is not None:
                    return item
            elif isinstance(v,list):
                for list_item in v:
                    # logger.debug("List Item: " + str(list_item))
                    item = self._findfirstitem(self, list_item, key)
                    if item is not None:
                        return item
    
    # return a VDFDict object of a .vdf file
    async def get_vdf(self, vdfile) -> vdf.VDFDict:
        # load vdf file as a python object (dictionary)
        data = None
        with open(vdfile, "rt") as file:
            data = file.read()
        logger.debug("Loading VDF Config. Protecting original file from changes.")
        vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        return vdf_obj
    
    # get the name and app id of currently running game
    async def get_game(self):
        obj = await self.get_vdf(self, Plugin.steam_registry)
        id = self._findfirstitem(self, obj, key="RunningAppID")
        out = { "name" :  "",
                "id" : ""}
        # TODO: incorporate language detection for smarter name cleanup
        # lang = self._finditem(self, obj, key="language")
        if str(id) == "0":
            out["name"] = "Unknown/Unsupported Program"
            out["id"] = str(id)
        else:
            name = self._findfirstitem(self, obj, key=str(id))
            # TODO: account for UTF-8 characters properly
            # (this is simple enough for now)
            name = str(name.get("name")).encode("ascii", "ignore").decode()
            # TODO: establish a good length to truncate game names
            # ( or just display first and last 'n' characters in modal?)
            out["name"] = name
            out["id"] = str(id)
        return out

    # get perf self contained
    async def get_settings(self):
        obj = await self.get_vdf(self, Plugin.steam_config)
        return self._findfirstitem(self, obj, key="perf")
    
    # format settings for display
    async def pretty_settings(self, obj):
        logger.debug("Prettying up: " + str(obj))
        out = ""
        for k,v in obj.items():
            out += str(k) + " " + str(v) + "<br>"
        return out
 
    async def get_presets(self):
        avaliable_presets = json.load(open(Plugin.preset_registry))
 
    async def save_preset(self):
        logger.debug("Starting to save preset")
        logger.debug("Getting game info")
        data_game = await self.get_game(self)
        logger.debug("Getting settings info")
        data_perf = await self.get_settings(self)
        name = re.sub(r"[^a-zA-Z0-9]","",str(data_game.get("name")))
        filename = f'{name}_{data_game.get("id")}.json'
        file = None
        try:
            logger.debug("Trying to create file")
            if not os.path.exists(info_preset.get("location")+filename):
                open(info_preset.get("location")+filename, 'x')
            with open(info_preset.get("location")+filename, 'w') as file:
                tofile = { "preset": { "game": "", "settings": ""}}
                tofile["preset"]["game"] = data_game
                tofile["preset"]["settings"] = data_perf
                file.write(json.dumps(tofile, indent=4))
                logger.debug(f"Created a preset file for: {filename}")
        # except FileExistsError:
        #     logger.error(f"Attempted to create already existing file, {sys.exc_info()}")
        except OSError:
            logger.error(f"COULD NOT CREATE FILE, {sys.exc_info()}")
        except:
            logger.error(f"AN ERROR OCCURED, {sys.exc_info()}")
        finally:
            logger.info(f"Attempted to create a preset file for: {filename}")    
            # registry = json.load(open(self.preset_registry))
            # presets = self._findfirstitem(registry, "presets")
            # logger.debug(registry)
            # logger.debug(type(registry))
            # with open(self.preset_registry, 'a') as file:
            #     file.write(json.dumps(data_game)+json.dumps(data_perf))
    async def load_preset(self):
        pass
   
    async def _main(self):
        # establish config filepath
        config = self.steam_config
        registry = self.preset_registry
        # check if copy of config doesn't exist
        if not os.path.exists(config+".bak"):
            # if so, make a copy
            shutil.copy2(config, config+".bak")
        # check if plugin registry doesn't exist
        if not os.path.exists(registry):
            # if so, create it
            default_registry = { "presets" : {} }
            with open(registry, 'x') as file:
                file.write(json.dumps(default_registry, indent=4))
        
                    
        
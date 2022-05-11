import sys,os
import logging,traceback,shutil,subprocess
import re,json

if not os.path.exists("/home/deck/.config/pluginloader/perfpresets"):
    subprocess.run(["mkdir", "-p", "/home/deck/.config/pluginloader/perfpresets/"])

logging.basicConfig(filename="/home/deck/.config/pluginloader/perfpresets/perfpresets.log",
					format='%(asctime)s %(levelname)s %(message)s',
					filemode='w',
                    force=True)
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

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

    preset_registry = info_preset["location"]+info_preset["filename"]
    steam_config = info_steam["locationlocal"]+info_steam["configpath"]
    steam_registry = info_steam["locationregistry"]+info_steam["registryname"]
    
    # recursively search through vdf to find a key and it's value
    def _findfirstitem(self, obj, key):
        if key in obj: 
            # logger.debug("Item found, " + str(key) + " " + str(obj[key]))
            return obj[key]
        for k, v in obj.items():
            # logger.debug("K: " + str(k))
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
    
    async def _getfromjs(self, obj):
        return obj
    
    # return a VDFDict object of a .vdf file
    async def get_vdf(self, vdfile) -> vdf.VDFDict:
        # load vdf file as a python object (dictionary)
        data = None
        with open(vdfile, "rt") as file:
            data = file.read()
        # logger.debug("Loading VDF Config. Protecting original file from changes.")
        vdf_obj = vdf.loads(data, mapper=vdf.VDFDict)
        return vdf_obj
    
    async def write_perf(self, obj=vdf.VDFDict):
        logger.debug(f"obj: {str(obj)}")
        config = self.steam_config
        shutil.copy2(config, config+".temp")
        if not os.path.exists(config+".bak"):
            # if so, make a copy
            shutil.copy2(config, config+".bak")
        with open(config+".temp", "wt") as file:
            file.write(obj)
            pass
    
    # get the name and app id of currently running game
    async def get_game(self):
        obj = await self.get_vdf(self, Plugin.steam_registry)
        id = self._findfirstitem(self, obj, key="RunningAppID")
        out = { "name" :  "",
                "id" : ""}
        if str(id) == "0":
            out["name"] = "Unknown/Unsupported Program"
            out["id"] = str(id)
        # TODO: incorporate language detection for smarter name cleanup
        # lang = self._finditem(self, obj, key="language")
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
        # logger.debug("Prettying up: " + str(obj))
        out = ""
        for k,v in obj.items():
            out += str(k) + " " + str(v) + "<br>"
        return out
 
    async def get_presets(self):
        with open(Plugin.preset_registry, "rt") as file:
            presets = json.load(file)
            # logger.debug(json.dumps(presets, indent=4))
            return self._findfirstitem(self, presets, "apps")
 
    async def get_preset(self, filename):
        with open(info_preset["location"]+filename+".json", "rt") as file:
            return json.load(file)
    
    # 
    async def save_preset(self, obj):
        logger.debug("Starting to save preset")
        logger.debug("Getting game info")
        data_game = await self.get_game(self)
        logger.debug("Getting settings info")
        data_perf = await self.get_settings(self)
        name = re.sub(r"[^a-zA-Z0-9]","",str(data_game.get("name")))
        id = data_game.get("id")
        if id == "0": return
        filename = f'{name}_{id}.json'
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
                try:
                    registry = json.load(open(self.preset_registry))
                    registry["presets"]["apps"].append(name+"_"+id)
                    # logger.debug(registry)
                    # logger.debug(type(registry))
                    with open(self.preset_registry, 'w') as file:
                        file.write(json.dumps(registry, indent=4))
                except:
                    logger.error(f"AN ERROR OCCURED, {sys.exc_info()}")
        # except FileExistsError:
        #     logger.error(f"Attempted to create already existing file, {sys.exc_info()}")
        except OSError:
            logger.error(f"COULD NOT CREATE FILE, {sys.exc_info()}")
        except:
            logger.error(f"AN ERROR OCCURED, {sys.exc_info()}")
        # finally:
        #     logger.info(f"Attempted to create a preset file for: {filename}")
    
    async def load_preset(self, filename):
        logger.debug(str(filename))
        filepath = info_preset["location"]+str(filename)+".json"
        logger.debug(f"filepath: {filepath}")
        settings = None
        with open(filepath, 'rt') as file:
            fileobj = json.load(file)
            settings = Plugin._findfirstitem(self, fileobj, "settings")
            logger.debug(f"settings: {settings}")
        # vdfile = VDFDict
        vdfile = await self.get_vdf(self, Plugin.steam_config)
        perf = vdfile["InstallConfigStore"]["Software"]["Valve"]["Steam"]["perf"]
        logger.debug(f"perf from vdfile: {perf}")
        

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
            default_registry = { "presets" : { "apps": [] } }
            with open(registry, 'x') as file:
                file.write(json.dumps(default_registry, indent=4))               
        
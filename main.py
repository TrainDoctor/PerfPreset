import os,shutil,subprocess
import tempfile

class Plugin:
    # The name of the plugin. This string will be displayed in the Plugin menu
    name = "Performance Presets"
    # The name of the plugin author 
    author = "TrainDoctor"

    # If the plugin should be reloaded from a call to /plugins/reload or a file change
    hot_reload = False

    # The HTML file that will be loaded when selecting the plugin in the list
    main_view_html = "main_view.html"

    # The HTML file that will be used to display a widget in the plugin main page
    # Comment this out if you don't plan to use a tile view. This will make a button with your plugin name appear
    tile_view_html = ""
    
    first_run = "True"
    
    temp_config = "/dev/null"

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def __main(self):
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
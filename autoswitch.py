"""
NOTE
- The purpose of making this script is to AutoSwitch OBS Scene via Websocket for osu! game
- The Data collected is from Gosumemory (https://github.com/l3lackShark/gosumemory)
- The script first will collect your current state in osu! (Song Select, Menu Screen, Playing etc)
    and then change the Scene on your OBS Stucdio via Websocket
- Scenes will be collected automatically from OBS Studio via Websocket
- The script will then generate a config.yaml which will be used to save the configuration
"""
#---------------------------------------
# Import Function (if not installed, install it)
#---------------------------------------
def checkImport(package):
    try:
        if(util.find_spec("{}".format(package)) == None):
            raise ModuleNotFoundError
        else:
            pass
    except ModuleNotFoundError:
        install(package)
    finally:
        return True
def install(package):
    get_package = {
        "websocket" :   "websocket-client",
        "obswebsocket" :    "obs-websocket-py"
    }.get(package, package)
    subprocess.run(['pip', 'install','--user','-q', get_package])
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.1)

#---------------------------------------
# Import Libraries
#---------------------------------------
import os,sys
import time
import json
from datetime import datetime, timedelta
from importlib import util
from glob import glob
import itertools
import threading
import subprocess

#---------------------------------------
# Import Not Installed Libraries
#---------------------------------------
os.system('cls')
print('----------------------------')
print('INSTALL NOT INSTALLED MODULE')
print('----------------------------\n')
done = False
t = threading.Thread(target=animate)
t.start()
if checkImport('websocket'):
    import websocket
if checkImport('obswebsocket'):
    from obswebsocket import obsws, requests, exceptions
if checkImport('colorama'):
    from colorama import Fore
if checkImport('ruamel.yaml'):
    import ruamel.yaml
done = True
print('\rimported websocket')
print('imported obswebsocket')
print('imported colorama')
print('imported ruamel.yaml')
print('\n----------------------------')
print('---ALL MODULES INSTALLED----')
print('----------------------------\n')
time.sleep(3)

#---------------------------------------
# Functions
#---------------------------------------
def printHeader(header):
    header_template = {
        "import config.yaml": "----------------------------\n-----IMPORT CONFIG.YAML-----\n----------------------------\n",
        "error": "----------------------------\n-----------ERROR------------\n----------------------------\n",
        "scene selector": "----------------------------\n-------Scene Selector-------\n----------------------------\n",
        "initial process": "----------------------------\n-----Initial Process--------\n--------only once-----------\n----------------------------\n",
        "password": "----------------------------\n----Please Enter Password---\n----------------------------\n",
        "print log": "----------------------------\n---------PRINT LOG----------\n----------------------------\n"
    }
    print(Fore.WHITE)
    os.system('cls')
    print(header_template.get('{0}'.format(header)))
    
def readJSON(data):
    return json.loads(data)

def readYAML(data, typ=None):
    if (typ == None):
        yaml = ruamel.yaml.YAML()
    else:
        yaml = ruamel.yaml.YAML(typ=typ)
    return yaml.load(data)

def writeYAML(data, file_path, typ=None):
    if (typ == None):
        yaml = ruamel.yaml.YAML()
    else:
        yaml = ruamel.yaml.YAML(typ=typ)
    yaml.default_flow_style=False
    with open(file_path, "w") as f:
        yaml.dump(data, f)
        f.close()
  
def CaseSensitivePath(name):
    sep = os.path.sep
    parts = os.path.normpath(name).split(sep)
    dirs = parts[0:-1]
    filename = parts[-1]
    if dirs[0] == os.path.splitdrive(name)[0]:
        test_name = [dirs[0].upper()]
    else:
        test_name = [sep + dirs[0]]
    for d in dirs[1:]:
        test_name += ["%s[%s]" % (d[:-1], d[-1])]
    path = glob(sep.join(test_name))[0]
    res = glob(sep.join((path, filename)))
    if not res:
        #File not found
        return None
    return res[0]
    
#---------------------------------------
# Global Vars
#---------------------------------------

printHeader('import config.yaml')

# Check if config.yaml is exist, otherwise create config.yaml
CONFIG_FILE = ".\\config.yaml"

# Read config.yaml
try:
    
    print(Fore.WHITE + 'Import config.yaml')
    config_file = open(CONFIG_FILE, "r")
    
except IOError:
    
    data = """\
    general:
        song select mode:
            inactive: 20 # in seconds
    gosumemory:
        uri: ws://127.0.0.1:24050/ws
    obs-websocket:
        host: 127.0.0.1
        port: 4444
    """
    
    data = readYAML(data)
    print(Fore.RED + 'config.yaml not found')
    time.sleep(1)
    print(Fore.WHITE +'Creating config.yaml')
    writeYAML(data, CONFIG_FILE)
    
finally:
    
    CONFIG_FILE = CaseSensitivePath(str(os.path.abspath(".\\config.yaml")))
    config_file = open(CONFIG_FILE, "r")
    config_yaml = readYAML(config_file.read())

    print(Fore.YELLOW + '"{}"'.format(CONFIG_FILE))
    time.sleep(3)
    
# Link variable with config.yaml
song_select_inactive_period = config_yaml['general']['song select mode']['inactive']
uri = config_yaml['gosumemory']['uri']
host = config_yaml['obs-websocket']['host']
port = config_yaml['obs-websocket']['port']

# Check if the password is in config.yaml, otherwise enter the password
if ('password' in config_yaml['obs-websocket']):
    
    password = config_yaml['obs-websocket']['password']
    
else:
    
    printHeader('password')
    password = input(Fore.WHITE + 'Enter OBS Websocket password : ')
    
    config_yaml['obs-websocket']['password'] = password
    writeYAML(config_yaml, CONFIG_FILE)
    
    print(Fore.WHITE + 'Password is set as : ', 
          Fore.GREEN +'{}'.format(password),
          Fore.WHITE +'\nYou can change password in',
          Fore.YELLOW + '\n"{}"'.format(CONFIG_FILE),'\n')                # i can't allow no password, keep your obs safe bro
    
    time.sleep(5)

# Get scene list from config.yaml, otherwise Get from obs-websocket
scene_list = {}
if ('scene' in config_yaml['obs-websocket']):
    
    list = config_yaml['obs-websocket']['scene']
    for key,value in list.items():
        scene_list['{}'.format(key)] = value
        
else:
    
    ws = obsws(host, port, password)
    increment = 0
    
    # initial obs-websocket connection (not using Websocket Class and variable will be deleted)
    printHeader('initial process')
    try:
        ws.connect()
    except exceptions.ConnectionFailure:
        
        print(Fore.RED + 'Unable to perform the initial process',
              Fore.WHITE + '\nPlease Enable OBS Websocket\n',
              Fore.WHITE + 'And make sure the password is match\n')
        time.sleep(3)
        exit()
        
    config_yaml['obs-websocket']['scene'] = {}
    writeYAML(config_yaml, CONFIG_FILE)
    
    get_scene_list = ws.call(requests.GetSceneList())
    list = config_yaml['obs-websocket']['scene']
    for scene in get_scene_list.getScenes():
        get_name = '{}'.format(scene.get('name'))
        if get_name.__contains__('[osu]'):
            list[increment] = get_name
            writeYAML(config_yaml, CONFIG_FILE)
            increment += 1
            
    for key,value in list.items():
        scene_list['{}'.format(key)] = value
    
    config_file.close()
    ws.disconnect()
    del increment, ws, get_scene_list, get_name
    print('Done')

# Get default scene mode from config.yaml, otherwise ask user
if ('state' in config_yaml['general']):
    
    scene_mode_default = int(config_yaml['general']['state']['default'])
    scene_mode_song_select = int(config_yaml['general']['state']['song select'])
    
else:
    
    config_yaml['general']['state'] = {}
    
    printHeader('scene selector')
    for key, value in scene_list.items():
        print(key,':', value)
        
    # user input
    try:
        print()
        print(Fore.WHITE +'If it is empty then you have to rename your obs scene with', 
            Fore.YELLOW + '[osu]', 
            Fore.WHITE + 'included\nand run this script again (CTRL-C to terminate)\n')
        scene_mode_default = input(Fore.WHITE + 'Enter number for your default scene : ')
        scene_mode_song_select = input(Fore.WHITE + 'Enter number for your song select scene : ')
    except KeyboardInterrupt:
        exit()

    config_yaml['general']['state']['default'] = scene_mode_default
    config_yaml['general']['state']['song select'] = scene_mode_song_select
    writeYAML(config_yaml, CONFIG_FILE)
    
    time.sleep(1)
    print()
    print(Fore.WHITE + 'I cant ask you to input every scene, but instead')
    time.sleep(1)
    print(Fore.WHITE + 'input them yourself in your', 
          Fore.GREEN + 'config.yaml')
    time.sleep(1)
    print('\n',
          Fore.WHITE + '-=Short Explanation=-',
          '\n',)
    time.sleep(1)
    print(Fore.WHITE + 'general:\n  state:\n    list:\n',
          Fore.BLUE + '     # add osu! state here')
    time.sleep(1)
    print(Fore.YELLOW + '      2 :', 
          Fore.GREEN + '3',
          '\n')
    time.sleep(1)
    print(Fore.WHITE + 'with', 
          Fore.YELLOW + '2', 
          Fore.WHITE + 'is osu state(from link above) and', 
          Fore.GREEN + '3',
          Fore.WHITE + 'is your scene number',
          '\n')
    time.sleep(10)
    print(Fore.GREEN + 'Using default value')
    time.sleep(3)
    
# Get state_list from config.yaml, otherwise create
state_list = {} 
if ('list' in config_yaml['general']['state']):
    
    list = config_yaml['general']['state']['list']
    for key,value in list.items():
        state_list['{}'.format(key)] = value
        
else: 
    
    value = """\
    # add osu!state or change obs scene number here
    5:  0      # Song Select
    7:  0      # Result
    11: 0      # Multi Lobby
    12: 0      # Multi Room
    2:  3      # Playing
    # ^     ^
    # osu!  obs 
    # state scene 
    #       number
    # reference for osu!state (https://github.com/Piotrekol/ProcessMemoryDataFinder/blob/master/OsuMemoryDataProvider/OsuMemoryStatus.cs)
    """
    value = readYAML(value)
    
    config_yaml['general']['state']['list'] = value
    writeYAML(config_yaml, CONFIG_FILE)
    
    list = config_yaml['general']['state']['list']
    for key,value in list.items():
        state_list['{}'.format(key)] = value
        
# close config.yaml
del key, value, list
config_file.close()                 # I'm bad at creating user input and feedback, I'm sorry

#---------------------------------------
# Class
#---------------------------------------
class Websocket:
    
    class Osu:
        
        def __init__(self):
            global uri
            self.uri = uri
            self.ws = websocket.WebSocket()
            
        def connect(self):
            try:
                self.ws.connect(self.uri)
            except ConnectionRefusedError as e:
                printHeader('error')
                print(Fore.RED + 'Error :',e,Fore.WHITE + '\nPlease Run Gosumemory and osu!')
                time.sleep(3)
                exit()
                
        def disconnect(self):
            self.ws.close()
            
        def recv(self):
            return self.ws.recv()
        
    class Obs:
        
        def __init__(self):
            # Using obs-websocket-py library
            global host, port, password
            self.ws = obsws(host,port,password)
            
        def connect(self):
            try:
                self.ws.connect()
            except exceptions.ConnectionFailure as e:
                printHeader('error')
                print(Fore.RED + 'Error :',e,Fore.WHITE + '\nPlease Enable OBS Websocket\n',
                      Fore.WHITE + 'And make sure the password is match\n')
                time.sleep(3)
                exit()
                
        def disconnect(self):
            self.ws.disconnect()
            
        def setScene(self, scene):
            self.ws.call(requests.SetCurrentScene(scene))
            
        def getScene(self):
            get_scene = self.ws.call(requests.GetCurrentScene())
            return get_scene.getName()
        
        
class translateScene:
    
    def __init__(self):
        pass
    
    def ToText(self, scene_number):
        # Get scene_list from config.yaml
        # return scene name from scene_list based on scene number
        # you can add/change in your config.yaml
        global scene_list
        return scene_list.get('{0}'.format(scene_number))
    
    def FromMemoryState(self, memory_state):
        # All osu! state can be read here:
        # https://github.com/Piotrekol/ProcessMemoryDataFinder/blob/master/OsuMemoryDataProvider/OsuMemoryStatus.cs
        # return scene_number from state_list based on memory_state
        # you can add/change in your config.yaml
        global scene_mode_default
        global state_list
        return state_list.get('{0}'.format(memory_state), scene_mode_default)
    
    
class OsuMainVar:
    
    def __init__(self):
        self.__memorystate = None
        self.__bg_path = None
        self.__game_path = None
        self.__map_id = None
        
    def Update(self, data):
        osu_json = readJSON(data)
        # doing self update
        self.__memorystate = osu_json['menu']['state']
        self.__bg_path = osu_json['menu']['bm']['path']['full']
        self.__game_path = osu_json['settings']['folders']['songs']
        self.__map_id = osu_json['menu']['bm']['set']
        otv.new_memory_state = self.__memorystate
        
    # You cannot get variables directly from this class
    # instead, use this function
    def getMemoryState(self):
        return self.__memorystate
    
    def getBgPath(self):
        return self.__bg_path
    
    def getGamePath(self):
        return self.__game_path
    
    def getMapID(self):
        return self.__map_id


class OsuTempVar:
    old_memory_state = None
    new_memory_state = None
    song_select_state = 0
    song_select_is_inactive = 0
    
    
class OsuSongSelectStatus:
    
    def __init__(self):
        self.old_map_id = 0
        self.map_id_list = {}
        self.map_id_list_increment = 0
        self.time_now_1second = 0
        self.time_now = 0
        self.time_period = 0
        
    def doIncrement(self):
        # a true 1 second increments based on real time
        increment = timedelta(seconds=1)    
        if (self.time_now_1second == 0):
            self.time_now_1second = self.time_now + increment
        if (self.time_now == self.time_now_1second):
            self.time_now_1second = self.time_now + increment
            self.map_id_list_increment += 1
            
    def doCheckIsInactive(self):
        # check if all values in map_id_list are true for inactive status
        map_id_list = self.map_id_list.values()
        val = list(map_id_list)[0]
        if (all(value == val for value in map_id_list) == True):
            return 1
        else:
            return 0
        
    def setPeriod(self):
        # set period based on song_select_inactive_period
        global song_select_inactive_period
        increment = timedelta(seconds=int(song_select_inactive_period))     
        self.time_period = self.time_now + increment
        
    def doCalc(self):
        self.time_now = datetime.now().replace(microsecond=0)
        self.doIncrement()
        self.map_id_list["mapID{0}".format(self.map_id_list_increment)] = omv.getMapID()    # expected output is a list of mapID lists in a dictionary format
        
        if (self.time_period == 0):                 # initial run to set period
            self.setPeriod()
        if (self.old_map_id != omv.getMapID()):     # if mapID is changed, reset period
            self.map_id_list.clear()
            self.setPeriod()
        if (self.time_now == self.time_period):     # If period is over, determine the inactive status and reset period
            otv.song_select_is_inactive = self.doCheckIsInactive()
            self.map_id_list.clear()
            self.map_id_list = {}
            self.setPeriod()
            self.map_id_list_increment = 0
    
    # I'm using the get function for readable reasons
    def getOldMapID(self):
        return self.old_map_id
    
    def getMapIDList(self):
        return self.map_id_list


class OsuStatus:
    
    def __init__(self):
        pass
    
    def doCheck(self):
        if (otv.old_memory_state != otv.new_memory_state):
            ws_obs.setScene(ts.ToText(ts.FromMemoryState(omv.getMemoryState())))      # I'm gonna write TODO to change this. but it still readable just read back to front
            self.printMiniLog()
            otv.old_memory_state = otv.new_memory_state
        self.doCheckSongSelectStatus()
        
    def doCheckSongSelectStatus(self):
        global scene_mode_default
        global scene_mode_song_select
        if (otv.new_memory_state == 5):     # only check song select status at song select state
            osss.doCalc()
            if (osss.getOldMapID() != omv.getMapID() and \
                    otv.song_select_state == 0 and \
                    otv.song_select_is_inactive == 0):
                otv.song_select_state = 1
                ws_obs.setScene(ts.ToText(scene_mode_song_select))
                print('   Entering Song Select Mode')
                self.printMiniLog()
            if (otv.song_select_state == 1 and \
                    otv.song_select_is_inactive == 1):
                otv.song_select_state = 0
                otv.song_select_is_inactive = 0
                ws_obs.setScene(ts.ToText(scene_mode_default))
                print('   Exiting Song Select Mode Because Inactive')
                self.printMiniLog()
        else:                               # reset all song select status when you are not in song select state
            if (otv.song_select_state == 1 or \
                    otv.song_select_is_inactive == 1):
                otv.song_select_state = 0
                otv.song_select_is_inactive = 0
                print('   Exiting Song Select Mode')
                self.printMiniLog()
        osss.old_map_id = omv.getMapID()
        
    def printMiniLog(self):
        print(Fore.WHITE + 'State', Fore.GREEN + '{}'.format(omv.getMemoryState()), 
              Fore.WHITE + '| Scene', Fore.CYAN + '{}'.format(ws_obs.getScene()),
              Fore.WHITE)
        
    def printLongLog(self):
        print('song select state', otv.song_select_state,'inactive',otv.song_select_is_inactive)
        print(osss.getMapIDList())
        print('memory state',omv.getMemoryState())
        print(ws_obs.getScene())
#---------------------------------------
# Start
#---------------------------------------
time.sleep(2)
if __name__ == "__main__":
    omv = OsuMainVar()
    otv = OsuTempVar()
    osss = OsuSongSelectStatus()
    ostat = OsuStatus()
    ws_obs = Websocket.Obs()
    ws_osu = Websocket.Osu()
    ts = translateScene()
    ws_osu.connect()
    ws_obs.connect()
    printHeader('print log')
    while True:
        try:
            omv.Update(ws_osu.recv())
            ostat.doCheck()
            #ostat.printLog()
        except KeyboardInterrupt:
            break
    ws_osu.disconnect()
    ws_obs.disconnect()

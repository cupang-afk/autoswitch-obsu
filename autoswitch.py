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
# Import Libraries
#---------------------------------------
from glob import glob
from datetime import datetime, timedelta
import os
import time

#---------------------------------------
# Import Not Installed Libraries
#---------------------------------------
import utils.install_package

os.system('cls')
print('----------------------------')
print('INSTALL NOT INSTALLED MODULE')
print('----------------------------\n')
done = False

utils.install_package.install_all()

import websocket
from obswebsocket import obsws, requests, exceptions
from colorama import Fore

done = True
print('\n----------------------------')
print('---ALL MODULES INSTALLED----')
print('----------------------------\n')
time.sleep(3)

#---------------------------------------
# Import Utils
#---------------------------------------
from utils import print_header
import utils.config_parser

#---------------------------------------
# Global Vars
#---------------------------------------

print_header.printHeader('import config.yaml')
Config = utils.config_parser.Config()
    
# Link variable with config.yaml
song_select_inactive_period = Config.Read()['general']['song select mode']['inactive']
uri = Config.Read()['gosumemory']['uri']
host = Config.Read()['obs-websocket']['host']
port = Config.Read()['obs-websocket']['port']
password = Config.Password()
scene_list = Config.SceneList()
scene_mode_default = Config.DefaultState()[0]
scene_mode_song_select = Config.DefaultState()[1]
state_list = Config.StateList()
        
# close config.yaml
Config.Close()                 # I'm bad at creating user input and feedback, I'm sorry

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
                print_header.printHeader('error')
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
                print_header.printHeader('error')
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
        osu_json = utils.config_parser.readJSON(data)
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
    print_header.printHeader('print log')
    while True:
        try:
            omv.Update(ws_osu.recv())
            ostat.doCheck()
            #ostat.printLog()
        except KeyboardInterrupt:
            break
    ws_osu.disconnect()
    ws_obs.disconnect()

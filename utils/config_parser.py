from glob import glob
from colorama import Fore
from . import print_header
from obswebsocket import obsws, requests, exceptions
import os
import json
import time
import ruamel.yaml

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
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.encoding = 'utf-8'
    with open(file_path, "w", encoding='utf-8') as f:
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

class Config:
    def __init__(self):
        self.CONFIG_FILE = ".\\config.yaml"
    
        # Check if config.yaml is exist, otherwise create config.yaml
        
        try:
            
            print(Fore.WHITE + 'Import config.yaml')
            self.OPEN_CONFIG_FILE = open(self.CONFIG_FILE, "r")
            self.OPEN_CONFIG_FILE.close()
            
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
            writeYAML(data, self.CONFIG_FILE)
            
        finally:
            self.OPEN_CONFIG_FILE = open(self.CONFIG_FILE, "r")
            self.PATH_CONFIG_FILE = CaseSensitivePath(str(os.path.abspath(self.CONFIG_FILE)))
            self.config_yaml = readYAML(self.OPEN_CONFIG_FILE.read())
            print(Fore.YELLOW + '"{}"'.format(self.PATH_CONFIG_FILE))
            
            time.sleep(3)
            
    def Read(self):
        return self.config_yaml
    
    def Close(self):
        return self.OPEN_CONFIG_FILE.close()
    
    def Password(self):
        
        # Check if the password is in config.yaml, otherwise enter the password
        
        if ('password' in self.Read()['obs-websocket']):
            password = self.Read()['obs-websocket']['password']
            
            return password
        
        else:
            print_header.printHeader('password')
            password = input(Fore.WHITE + 'Enter OBS Websocket password : ')
            
            self.Read()['obs-websocket']['password'] = password
            writeYAML(self.Read(), self.CONFIG_FILE)
            
            print(Fore.WHITE + 'Password is set as : ', 
                Fore.GREEN +'{}'.format(password),
                Fore.WHITE +'\nYou can change password in',
                Fore.YELLOW + '\n"{}"'.format(self.PATH_CONFIG_FILE),'\n')                # i can't allow no password, keep your obs safe bro
            
            time.sleep(5)
            return password
        
    def SceneList(self):
        
        # Get scene list from config.yaml, otherwise Get from obs-websocket
        
        scene_list = {}
        
        if ('scene' in self.Read()['obs-websocket']):               #TODO add if scene_list is not blank
            list = self.Read()['obs-websocket']['scene']
            
            for key,value in list.items():
                scene_list['{}'.format(key)] = value
                
            return scene_list
        
        else:
            
            # initial obs-websocket connection
            host = self.Read()['obs-websocket']['host']
            port = self.Read()['obs-websocket']['port']
            password = self.Password()
            
            ws = obsws(host, port, password)
            increment = 0
            
            print_header.printHeader('initial process')
            
            try:
                
                ws.connect()
                
            except exceptions.ConnectionFailure:
                
                print(Fore.RED + 'Unable to perform the initial process',
                    Fore.WHITE + '\nPlease Enable OBS Websocket\n',
                    Fore.WHITE + 'And make sure the password is match\n')
                time.sleep(3)
                exit()
                
            self.Read()['obs-websocket']['scene'] = {}
            writeYAML(self.Read(), self.PATH_CONFIG_FILE)
            
            get_scene_list = ws.call(requests.GetSceneList())
            
            list = self.Read()['obs-websocket']['scene']
            
            for scene in get_scene_list.getScenes():
                get_name = '{}'.format(scene.get('name'))
                
                if get_name.__contains__('[osu]'):
                    list[increment] = get_name
                    writeYAML(self.Read(), self.PATH_CONFIG_FILE)
                    increment += 1
                    
            for key,value in list.items():
                scene_list['{}'.format(key)] = value
                
            ws.disconnect()
            print('Done')
            return scene_list
        
    def StateList(self):
        
        # Get state_list from config.yaml, otherwise create
        
        state_list = {} 
        
        if ('list' in self.Read()['general']['state']):
            list = self.Read()['general']['state']['list']
            
            for key,value in list.items():
                state_list['{}'.format(key)] = value
                
            return state_list
                
        else: 
            
            value = """\
    # add [Osu!State] or change [OBS Scene Number] here
    #
    # First value is [Osu!State]
    # Second value is [OBS Scene Number]
    #
            5:  0   # Song Select
            7:  0   # Result
            11: 0   # Multi Lobby
            12: 0   # Multi Room
            2:  3   # Playing
    # ↑     ↑
    # osu!  obs 
    # state scene 
    #       number
    #
    # add [Osu!State] acording to this link
    # reference for [Osu!State] (https://github.com/Piotrekol/ProcessMemoryDataFinder/blob/master/OsuMemoryDataProvider/OsuMemoryStatus.cs)
    """
            value = readYAML(value)
            
            self.Read()['general']['state']['list'] = value
            writeYAML(self.Read(), self.PATH_CONFIG_FILE)
            
            list = self.Read()['general']['state']['list']
            
            for key,value in list.items():
                state_list['{}'.format(key)] = value
                
            return state_list
        
    def DefaultState(self):
        
        # Get default scene mode from config.yaml, otherwise ask user
        
        scene_list = self.SceneList()
        
        if ('state' in self.Read()['general']):
            scene_mode_default = int(self.Read()['general']['state']['default'])
            scene_mode_song_select = int(self.Read()['general']['state']['song select'])
            
            return scene_mode_default, scene_mode_song_select
        
        else:
            self.Read()['general']['state'] = {}
            
            print_header.printHeader('scene selector')
            
            for key, value in scene_list.items():
                print(key,':', value)
                
            # user input
            try:
                print()
                print(Fore.WHITE +'If it is empty then you have to rename your obs scene with', 
                    Fore.YELLOW + '[osu]', 
                    Fore.WHITE + 'included\nand run this script again (type exit or ctrl-c to terminate)\n\n')

                while True:
                    try:
                        os.sys.stdout.write("\033[F")
                        scene_mode_default = input(Fore.WHITE + 'Enter number for your default scene : ')
                        if (scene_mode_default == "exit"):
                            raise KeyboardInterrupt
                        else:
                            scene_mode_song_select = input(Fore.WHITE + 'Enter number for your song select scene : ')
                            if (scene_mode_song_select == "exit"):
                                raise KeyboardInterrupt

                        if scene_mode_default.isdigit() or scene_mode_song_select.isdigit():
                            pass
                        else:
                            raise ValueError
                        
                    except ValueError:
                        os.sys.stdout.write('\033[F')
                        os.sys.stdout.write('\033[F')
                        print('\rPlease enter a NUMBER', ' ' * 30, '\n', ' ' * 70, '\033[F')
                        time.sleep(2)
                        continue
                    break
                
                if (scene_mode_default == "exit"):
                    raise KeyboardInterrupt
                
            except KeyboardInterrupt:
                exit()

            self.Read()['general']['state']['default'] = scene_mode_default
            self.Read()['general']['state']['song select'] = scene_mode_song_select
            writeYAML(self.Read(), self.PATH_CONFIG_FILE)
            
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
                Fore.BLUE + '     # add [Osu!State] or change [OBS Scene Number] here')
            time.sleep(1)
            print(Fore.YELLOW + '      2 :', 
                Fore.GREEN + '3',
                '\n')
            time.sleep(1)
            print(Fore.WHITE + 'with', 
                Fore.YELLOW + '2', 
                Fore.WHITE + 'is [Osu!State] and', 
                Fore.GREEN + '3',
                Fore.WHITE + 'is your [OBS Scene Number]',
                '\n')
            time.sleep(10)
            print(Fore.GREEN + 'Using default value')
            time.sleep(3)
            
            return scene_mode_default, scene_mode_song_select
        

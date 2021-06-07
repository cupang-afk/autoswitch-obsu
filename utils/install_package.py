from os import sys
from importlib import util
import subprocess
import itertools
import threading
import time

#---------------------------------------
# Global Vars
#---------------------------------------
done = False

#---------------------------------------
# Function
#---------------------------------------
def animate():
    
    global done
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rInstalling ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    
def install_all():
    
    global done
    
    p = Package()
    t = threading.Thread(target=animate)
    t.start()
    if p.doCheckInstall('websocket'):
        pass
        
    if p.doCheckInstall('obswebsocket'):
        pass
        
    if p.doCheckInstall('colorama'):
        pass

    if p.doCheckInstall('ruamel.yaml'):
        pass
    
    done = True
    
#---------------------------------------
# Class
#---------------------------------------
class Package:
    
    def __init__(self):
        pass
    
    def listPackage(self, package):
        # list of packages
        # because sometimes packages don't always have the same name when imported
        return {
            "websocket" :   "websocket-client",
            "obswebsocket" :    "obs-websocket-py"
        }.get(package, package)
    
    def doCheckInstall(self, package):
        
        try:
            if(util.find_spec("{}".format(package)) == None):
                raise ModuleNotFoundError
            
            else:
                pass
            
        except ModuleNotFoundError:
            self.install(package)
            
        finally:
            get_package = self.listPackage(package)
            print('\rInstalled : ', get_package)
            return True
        
    def install(self, package):

        get_package = self.listPackage(package)
        subprocess.run(['pip', 'install','--user','-q', get_package])

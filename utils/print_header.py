from colorama import Fore
import os

def printHeader(header, cls=True):
    header_template = {
        "import config.yaml": "----------------------------\n-----IMPORT CONFIG.YAML-----\n----------------------------\n",
        "error": "----------------------------\n-----------ERROR------------\n----------------------------\n",
        "scene selector": "----------------------------\n-------Scene Selector-------\n----------------------------\n",
        "initial process": "----------------------------\n-----Initial Process--------\n--------only once-----------\n----------------------------\n",
        "password": "----------------------------\n----Please Enter Password---\n----------------------------\n",
        "print log": "----------------------------\n---------PRINT LOG----------\n----------------------------\n"
    }
    print(Fore.WHITE)
    if cls:
        os.system('cls')
    print(header_template.get('{0}'.format(header)))
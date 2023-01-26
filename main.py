import pygame as pg
import sys
from menu import Menu
from configs import *

class Stderr:
    def write(self, s, error=""):
        with open("debug.log", "a") as f:
            f.write(error + s)

if __name__ == "__main__":
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass
    
    pg.init()
    pg.display.set_mode((WIDTH, HEIGHT))
    sys.stderr = Stderr()
    Menu()

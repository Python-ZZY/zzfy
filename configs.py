from functools import lru_cache
import pygame as pg
import os
import random
import sys

pg.mixer.pre_init()
pg.mixer.init()

def path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.normpath(os.path.join(base_path, relative_path))

def load_anm(name):
    anms = []
    num = 1
    base_path = path("assets/"+name)

    if "{}" not in base_path:
        return [base_path]
    
    while True:
        pth = base_path.format(num)
        
        if not os.path.exists(pth):
            break

        anms.append(pth)  
        num += 1

    return anms

@lru_cache(300)
def load_image(name, scale=None, flip=None):
    if "\\" not in name:
        surf = pg.image.load(path("assets/"+name))
    else:
        surf = pg.image.load(name)

    if scale:
        surf = pg.transform.scale(surf, scale)
    if flip:
        surf = pg.transform.flip(surf, *flip)
        
    return surf

def load_images(name, **kw):
    return [load_image(anm, **kw) for anm in load_anm(name)]

@lru_cache(1)
def load_font(size, name="fnt"):
    return pg.font.Font(path("assets/"+name+".ttc"), size)

@lru_cache()
def render(text, color=(255, 255, 255), size=19):
    return load_font(size).render(text, True, color)

def renders(texts, pady=5, bg=(0, 0, 0, 0)):
    wsizes = [load_font(size).size(text)[0] for text, _, size in texts]
    hsizes = [load_font(size).size("")[1]+pady for _, _, size in texts]
    
    surf = pg.Surface((max(wsizes), sum(hsizes))).convert_alpha()
    surf.fill(bg)
    
    for i, (text, color, size) in enumerate(texts):
        surf.blit(render(text, color, size), ((surf.get_size()[0]-wsizes[i])//2, sum(hsizes[:i])))

    return surf

@lru_cache()
def load_sound(name):
    return pg.mixer.Sound(path(name))

def play_sound(name, filetype="ogg"):
    load_sound("assets/"+name+"."+filetype).play()

def set_threshold(num, min, max):
    if num < min:
        return min
    elif num > max:
        return max
    return num

class MusicManager:
    def __init__(self, music=path("assets/bgm{}.ogg"), music_formats=["1", "2"]):
        self.music = music
        self.music_formats = music_formats
        self.idx = 0
        self.running = True
        random.shuffle(self.music_formats)

    def update(self):
        if not pg.mixer.music.get_busy() and self.running:
            pg.mixer.music.load(self.music.format(self.music_formats[self.idx]))
            pg.mixer.music.play()

            self.idx += 1
            if self.idx == len(self.music_formats):
                self.idx = 0

    def stop(self):
        self.running = False
        pg.mixer.music.fadeout(500)

vec = pg.Vector2

WIDTH = 1200
HEIGHT = 650

APPNAME = "战争风云"
VERSION = "Alpha 1.2"
CREDITS = f"""
战争风云  VERSION: {VERSION}

游戏作者: Python-ZZY (pythonzzy@foxmail.com)
Created by Python-ZZY

CSDN: https://blog.csdn.net/qq_48979387

itch: https://python-zzy-china.itch.io/

github: https://github.com/Python-ZZY/

贡献者: WuxiaScrub (素材/游戏设计)
Contributor: WuxiaScrub (Game Assets/Game Design)
itch: https://wuxia-scrub.itch.io/

此游戏的卡组设计仿照SUPERCELL的《皇室战争》游戏
The game's character design is modeled after SUPERCELL's Clash Royale game

主要素材来源如下网站，感谢游戏素材的提供者
Most assets comes from the following websites. Thank you to the creators of the assets.
https://opengameart.org/
https://game-icons.net/
https://www.aigei.com/
https://sanderfrenken.github.io/Universal-LPC-Spritesheet-Character-Generator/

更多版权信息如下:
More credits:
Stephen "Redshrike" Challener, William.Thompsonj
[LPC] Siege Weapons by bluecarrot16 (https://opengameart.org/content/lpc-siege-weapons)
https://www.aigei.com/view/70413.html

BGM:
orcs-victorious (opengamearg.org)
battle-music (soundcloud.com/alexandr-zhelanov)
spooky-enchantment (soundimage.org)

素材源于网络
如有侵权行为请联系作者
Game assets come from the Internet.
If your credit is required, please contact the creator!!

此游戏使用Python + Pygame制作
Made with Python + Pygame

感谢游玩！
Thanks for playing!
""".replace("\n\n", "\n"*8)

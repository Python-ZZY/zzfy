import pygame as pg
import sys
import os
import pickle
import units, battle_fun
from base import *
from battle import *
from configs import *

def load_user():
    try:
        file = open("user.p", "rb")
    except FileNotFoundError:
        user = {"score":0,
                "all_units":["bow_infantry", "soldier", "shielded_sword_infantry", "elite_spear_infantry",
                             "light_cavalry", "king", "fire", "wind"]}
        user["wear_units"] = user["all_units"].copy()
        write_user(user)
        return user
    else:
        data = pickle.load(file)
        return pickle.loads(data[::-1])

def write_user(user):
    data = pickle.dumps(user)[::-1]
    with open("user.p", "wb") as f:
        pickle.dump(data, f)

def cut_str(string, length):
    return [string[i:i+length] for i in range(0, len(string), length)]

class SceneWithButtons(Scene):
    def init(self):
        self.click = False
        self.tooltip = None
        
        self.tip = None
        self.effect_sprites = pg.sprite.Group()
        self.buttons = pg.sprite.Group()
        self.cup_rect = load_image("cup.png").get_rect(x=5, y=5)
        self.mm = MusicManager()

    def do(self, func, *args):
        def f():
            self.click = False
            self.tip = None
            func(*args)
        return f
    
    def show_tip(self, text):
        self.tip = FadeOutText(text, size=20, last=0)
        self.tip.rect.y = 40

    def show_tooltip(self, pos, text, anchor="bottomright"):
        if text:
            tip = renders([(text[0], (255, 255, 255), 18),
                           (text[1], (255, 255, 255), 13)], bg=(0, 0, 0, 150))
            rect = eval(f"tip.get_rect({anchor}=pos)")
            self.tooltip = Static(rect.x, rect.y, tip, pgim=True)

    def onexit(self):
        self.click = False
        self.quit_scene()
        
    def events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                play_sound("button_click")
                self.click = True
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.click = False
            
    def update(self):
        self.mm.update()
        pos = pg.mouse.get_pos()
        
        for sprite in self.effect_sprites:
            sprite.animate()
            
        if self.tip:
            self.tip.update()
            if not self.tip.alive:
                self.tip = None

    def draw(self):
        self.tooltip = None
        
        pos = pg.mouse.get_pos()
        for button in self.buttons:
            if button.update(self.screen, self.click, pos):
                self.show_tooltip(pos, button.tooltip, anchor=button.anchor)

        if self.cup_rect.collidepoint(pos):
            self.show_tooltip(pos, ("奖杯", "战斗胜利会获得一定奖杯，失败会扣除一定奖杯（派对模式除外）"),
                              anchor="topleft")

        self.screen.blit(load_image("cup.png"), self.cup_rect)
        self.screen.blit(render(str(int(self.user["score"]))), (self.cup_rect.right + 3, 5))

        self.effect_sprites.draw(self.screen)
        
        if self.tooltip:
            self.tooltip.draw(self.screen)
        if self.tip:
            self.screen.blit(self.tip.image, self.tip.rect)
        
class Credits(SceneWithButtons):
    def __init__(self, user):
        self.user = user
        super().__init__()
        
    def init(self):
        super().init()
        
        self.background = load_image("mainmenu.jpg")
        self.group = []
        self.speed = 2

        i = 0
        for text in CREDITS.split("\n"):
            if text == "\n":
                i += 2
                continue
            
            sprite = render(text)
            self.group.append([sprite, sprite.get_rect(centerx=WIDTH//2,
                                                       y=HEIGHT+i*50)])
            i += 1

        Button(self.buttons, (WIDTH - 42, HEIGHT - 42), "button_return.png",
               ("返回", "点击回到主菜单"), self.do(self.quit_scene))
        
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for i, (sprite, rect) in enumerate(self.group):
            if rect.y < HEIGHT:
                self.screen.blit(sprite, rect)
                
            rect.y -= self.speed
            if rect.bottom < 0:
                self.group.pop(i)

        super().draw()

    def update(self):
        super().update()
        if len(self.group) == 0:
            self.onexit()

class Party(SceneWithButtons):
    def __init__(self, user, start_battle):
        self.all_battle = []
        for cls in dir(battle_fun):
            if cls.startswith("b_"):
                self.all_battle.append(eval("battle_fun." + cls))
                
        self.user = user
        self.start_battle = start_battle
        super().__init__()

    def _left(self):
        self.click = False
        self.active_choice -= 1
        if self.active_choice < 0:
            self.active_choice = len(self.all_battle) - 1

    def _right(self):
        self.click = False
        self.active_choice += 1
        self.active_choice = self.active_choice % len(self.all_battle)

    def events(self, event):
        super().events(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                self._left()
            elif event.key == pg.K_RIGHT:
                self._right()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                self._left()
            elif event.button == 5:
                self._right()
                
    def init(self):
        super().init()

        self.background = load_image("mainmenu.jpg").copy()
        self.active_choice = 0
        
        pad = 30
        boardw = WIDTH - 2 * pad
        boardh = HEIGHT - 2 * pad
        board = pg.Surface((boardw, boardh)).convert_alpha()
        board.fill((0, 0, 0, 150))
        pg.draw.rect(board, (255, 255, 0), (0, 0, boardw, boardh), width=1)
        self.background.blit(board, (pad, pad))

        self.battle_icons = []
        self.battle_tips = []
        for cls in self.all_battle:
            icon = load_image(cls.__name__[2:] + "_icon.png")
            icon_rect = icon.get_rect(centerx=WIDTH//2, centery=HEIGHT//3)
            self.battle_icons.append((icon, icon_rect))

            text = cls.__doc__.split(";")
            r = renders([(text[0], (255, 255, 255), 22), (text[1], (255, 255, 255), 14)],
                        pady=15, bg=(0, 0, 0, 0))
            self.battle_tips.append((r, r.get_rect(centerx=WIDTH//2, centery=HEIGHT*2//3)))

        self.click_surf = pg.Surface(icon_rect.size).convert_alpha()
        self.click_surf.fill((0, 0, 0, 0))
        pg.draw.circle(self.click_surf, (0, 0, 0, 50), (icon_rect.width//2, icon_rect.height//2), icon_rect.width//2)
        self.click_rect = icon_rect
        
        Button(self.buttons, (WIDTH - 42, HEIGHT - 42), "button_return.png",
               ("返回", "点击回到主菜单"), self.do(self.quit_scene))
        Button(self.buttons, (150, HEIGHT//2), "button_left.png",
               None, self._left)
        Button(self.buttons, (WIDTH - 150, HEIGHT//2), "button_right.png",
               None, self._right)        
            
    def draw(self):
        pos = pg.mouse.get_pos()
        
        self.screen.blit(self.background, (0, 0))

        self.screen.blit(self.battle_icons[self.active_choice][0],
                         self.battle_icons[self.active_choice][1])
        self.screen.blit(self.battle_tips[self.active_choice][0],
                         self.battle_tips[self.active_choice][1])

        if self.click_rect.collidepoint(pos):
            self.screen.blit(self.click_surf, self.click_rect)
            if self.click:
                self.click = False
                self.start_battle(self.all_battle[self.active_choice], False)
                self.quit_scene()
        
        super().draw()
        
class UnitManager(SceneWithButtons):
    def __init__(self, user):
        self.user = user
        super().__init__()

    def init(self):
        super().init()
        
        self.background = load_image("mainmenu.jpg").copy()
        self.active_unit = None

        self.pad = pad = 30
        tipboardw = 280
        boardw = WIDTH - 3 * pad - tipboardw
        boardh = HEIGHT - 2 * pad
        board = pg.Surface((boardw, boardh)).convert_alpha()
        board.fill((0, 0, 0, 150))
        pg.draw.rect(board, (255, 255, 0), (0, 0, boardw, boardh), width=1)
        self.background.blit(board, (pad, pad))

        tipboard = pg.Surface((tipboardw, boardh)).convert_alpha()
        tipboard.fill((0, 0, 0, 150))
        pg.draw.rect(tipboard, (255, 255, 0), (0, 0, tipboardw, boardh), width=1)
        self.background.blit(tipboard, (boardw + 2 * pad, pad))

        self.tipboard_tip_pos = (boardw + 2 * pad, pad)

        self.column_c = 9
        for i, (en_name, value) in enumerate(sys.stdout.all_units.items()):
            if en_name not in self.user["all_units"] and self.user["score"] >= value[0]:
                self.user["all_units"].append(en_name)
                row = i // self.column_c
                column = i % self.column_c
                icon_rect = pg.Rect((column*85+pad+40, row*85+pad+40, 65, 65))
                self.play_effect(icon_rect.center, "unlock{}.png")  
        sys.stdout.all_units = dict(sorted(sys.stdout.all_units.items(),
                                           key=lambda x: 1 if x[0] in self.user["all_units"] else 0,
                                           reverse=True))
    
        self.all_units = sys.stdout.all_units
        self.unit_tipboard_tips = []
        self.unit_rects = []
        for i, (en_name, value) in enumerate(self.all_units.items()):
            row = i // self.column_c
            column = i % self.column_c

            icon = load_image(en_name + "_icon.png")
            icon_rect = pg.Rect((column*85+pad+40, row*85+pad+40, 65, 65))
                
            if en_name not in self.user["all_units"]:
                icon = set_grey(icon)
                icon.blit(load_image("lock.png"), (0, 0))                
            
            self.unit_tipboard_tips.append(self.get_unit_tipboard_tip(tipboardw, boardh, en_name, icon,
                                                                      en_name in self.user["all_units"]))
            self.unit_rects.append(icon_rect)
            self.background.blit(icon, icon_rect)

            self.background.blit(render(str(value[2]), size=11),
                                 (column*85+pad+100, row*85+pad+90))

        self.update_wear_units()
        write_user(self.user)

        Button(self.buttons, (WIDTH - 42, HEIGHT - 42), "button_return.png",
               ("返回", "点击回到主菜单"), self.onexit)
        Button(self.buttons, (42, HEIGHT - 42), "button_random_units.png",
               ("随机卡组", "点击随机生成士兵卡组"), self.random_units,
               anchor="bottomleft")

    def get_unit_tip(self, cn_name, doc):
        tip = renders([(cn_name, (255, 255, 255), 18),
                       (doc, (255, 255, 255), 13)], bg=(0, 0, 0, 150))
        return tip

    def get_unit_tipboard_tip(self, w, h, en_name, icon, locked):
        tip = pg.Surface((w, h)).convert_alpha()
        tip.fill((0, 0, 0, 0))
        value = self.all_units[en_name]

        name_r = render(value[1], size=20)

        pad = 30
        tip.blit(icon, (pad, pad))
        tip.blit(name_r, name_r.get_rect(x=64 + 2 * pad, centery=32 + pad))

        if not locked:
            r = renders([("未解锁", (200, 200, 200), 20),
                         ("奖杯数达到%d后解锁"%value[0], (255, 255, 255), 14)], pady=20, bg=(0, 0, 0, 0))
            tip.blit(r, r.get_rect(centerx=w//2, y=200))
        else:
            dictionary = {"类型":("战斗单位" if value[4] == "soldier" else "法术"),
                          "花费":value[2],
                          "冷却时间":value[5]}
            if value[4] == "soldier":
                dictionary.update({"速度":value[6],
                                   "血量":value[8],
                                   "破阵伤害":value[7]})
            else:
                dictionary.update({"范围":"%dx%d"%value[6]})

            for i, (k, v) in enumerate(dictionary.items()):
                tip.blit(render(str(k), color=(210, 210, 210), size=16), (pad, i * 24 + 124))
                tip.blit(render(str(v), size=14), (pad + 100, i * 24 + 124))

            for i, s in enumerate(cut_str(value[3], 15), start=i):
                tip.blit(render(s, size=15), (pad, i * 24 + 200))
        
        return tip

    def update_wear_units(self):
        self.wear_unit_rects = []
        for i, (en_name, value) in enumerate(self.all_units.items()):
            row = i // self.column_c
            column = i % self.column_c
            if en_name in self.user["wear_units"]:
                icon_rect = pg.Rect((column*85+self.pad+40, row*85+self.pad+40, 65, 65))
                self.wear_unit_rects.append(icon_rect)
                
    def random_units(self):
        self.user["wear_units"] = random.sample(self.user["all_units"], 8)
        self.update_wear_units()
        write_user(self.user)

    def onexit(self):
        if len(self.user["wear_units"]) != 8:
            self.show_tip("军队数量不足")
        else:
            super().onexit()
            
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(load_image("cup.png"), (5, 5))
        self.screen.blit(render(str(int(self.user["score"]))), (33, 5))
        pos = pg.mouse.get_pos()

        for rect in self.wear_unit_rects:
            self.screen.blit(load_image("wore.png"), rect)
            
        for i, rect in enumerate(self.unit_rects):
            if rect.collidepoint(pos):
                self.active_unit = i
                if self.click:
                    self.click = False
                    en_name = tuple(self.all_units.keys())[i]
                    if rect in self.wear_unit_rects:
                        self.user["wear_units"].remove(en_name)
                        self.wear_unit_rects.remove(rect)
                        write_user(self.user)
                    else:
                        if en_name in self.user["all_units"]:
                            if len(self.user["wear_units"]) < 8:
                                self.user["wear_units"].append(en_name)
                                self.wear_unit_rects.append(rect)
                                write_user(self.user)
                            else:
                                self.show_tip("军队数量已达上限")
                        else:
                            self.show_tip("未解锁")
                            
                break
            
        if self.active_unit != None:
            self.screen.blit(self.unit_tipboard_tips[self.active_unit], self.tipboard_tip_pos)

        super().draw()

class Menu(SceneWithButtons):
    def __init__(self):
        setattr(sys.stdout, "all_units", {})
        for cls in dir(units):
            if cls.startswith("c_"):
                try:
                    eval(cls)(None, {})
                except TypeError:
                    try:
                        eval(cls)(None)
                    except AttributeError:
                        pass
                except AttributeError:
                    pass
                
        super().__init__(caption=APPNAME, icon=load_image("icon.ico"))
        
    def init(self):
        super().init()
        
        pg.mouse.set_cursor(pg.cursors.Cursor((0, 0), load_image("cursor.png")))
        self.background = load_image("mainmenu.jpg")

        self.all_sprites = pg.sprite.Group()
        self.user = load_user()
        
        Button(self.buttons, (WIDTH*0.25, HEIGHT//2), "button_battle.png",
               ("战地", "点击匹配对手"), self.do(self.start_battle))
        Button(self.buttons, (WIDTH*0.5, HEIGHT//2), "button_party.png",
               ("派对 !", "点击参加更多玩法"), self.do(Party, self.user, self.start_battle))
        Button(self.buttons, (WIDTH*0.75, HEIGHT//2), "button_manager.png",
               ("军营", "点击管理军队卡牌"), self.do(UnitManager, self.user))
        Button(self.buttons, (42, HEIGHT - 42), "button_log.png",
               ("日志", "点击查看游戏日志信息，请及时向创作者反馈遇到的bug"),
               self.load_log, anchor="bottomleft")
        Button(self.buttons, (WIDTH - 116, HEIGHT - 42), "button_info.png",
               ("信息", "点击查看游戏创作者及素材来源"), self.do(Credits, self.user))
        Button(self.buttons, (WIDTH - 42, HEIGHT - 42), "button_exit.png",
               ("退出", "点击离开游戏"), sys.exit)

    def _command_win(self, battle):
        score_before = self.user["score"]
        
        self.user["score"] += random.randint(6, 11) * battle.difficulty * 1000
        write_user(self.user)
        
        return "奖杯 %d -> %d"%(score_before, self.user["score"])

    def _command_lose(self, battle):
        score_before = self.user["score"]
        self.user["score"] -= random.randint(6, 11) * (0.01 - battle.difficulty) * 1000

        if self.user["score"] >= 0:
            write_user(self.user)
            
            return "奖杯 %d -> %d"%(score_before, self.user["score"])
        else:
            self.user["score"] = 0
            write_user(self.user)
            
            return "奖杯 %d -> 0"%score_before

    def _command_same(self, battle):
        return "奖杯 %d -> %d"%(self.user["score"], self.user["score"])
    
    def load_log(self):
        try:
            os.startfile(os.getcwd()+"/debug.log")
        except OSError:
            self.show_tip("无日志记录")
    
    def start_battle(self, battle=Battle, score=True):
        if len(self.user["wear_units"]) != 8:
            self.show_tip("军队数量不足")
            return

        a = (self.user["wear_units"],
             random.sample(list(sys.stdout.all_units), 8),
             random.uniform(0.003, 0.008))
        if score:
            battle(*a, self._command_win, self._command_lose, self._command_same)
        else:
            battle(*a)
            
    def update(self):
        super().update()
        for sprite in self.all_sprites:
            sprite.animate()
    
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)

        super().draw()
    
if __name__ == "__main__":
    pg.init()
    pg.display.set_mode((WIDTH, HEIGHT))
    Menu()

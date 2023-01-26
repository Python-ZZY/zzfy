import pygame as pg
import random
from configs import *
from battle import *

all_battle_list = {}

class fallingSpellBattle(Battle):
    def init(self):
        super().init()
        self.last_falling = 0
        self.count = 10

    def getdelta(self):
        return 8000 - set_threshold(self.period, 0, 2) * 2000
    
    def update(self):
        super().update()
        now = self.timer
        
        if now - self.last_falling > self.getdelta():
            self.last_falling = now
            
            for i in range(self.count):
                spell = random.choice(self.all_spells)
                self.add_spell(spell, "l", (random.randint(0, self.background_width),
                                             random.randint(self.action_bar_height, HEIGHT)))
                self.add_spell(spell, "r", (random.randint(0, self.background_width),
                                             random.randint(self.action_bar_height, HEIGHT)))

class fallingSoldierBattle(Battle):
    def init(self):
        super().init()
        self.last_falling = 0

    def getdelta(self):
        return 9000 - set_threshold(self.period, 0, 2) * 2000
        
    def update(self):
        super().update()
        now = self.timer
        
        if now - self.last_falling > self.getdelta():
            self.last_falling = now
            soldier = random.choice(self.all_soldiers)
            
            for i in range(self.maxroad+1):
                self.add_soldier(soldier, "l", i)
                self.add_soldier(soldier, "r", i)

class b_barricade_battle(Battle):
    '''层层设防模式;战场上栅栏数量增加'''
    def init(self):
        super().init()
        for i in range(self.maxroad//2+1):
            unit = self.add_soldier("barricade", "l", road=i*2+1, startswith="cs_")
            unit.health = unit.maxhealth = 220
            self.barricades.add(unit)
            self.soldiers[i*2].add(unit)
            unit.moveto("centerx", 500)
            
            unit = self.add_soldier("barricade", "r", road=i*2+1, startswith="cs_")
            unit.health = unit.maxhealth = 220
            self.barricades.add(unit)
            self.soldiers[i*2].add(unit)
            unit.moveto("centerx", self.background_width-500)

            camp = "l" if i % 2 == 0 else "r"
            unit = self.add_soldier("barricade", camp, road=i*2+1, startswith="cs_")
            unit.health = unit.maxhealth = 220
            self.barricades.add(unit)
            self.soldiers[i*2].add(unit)
            unit.moveto("centerx", 1100 if camp == "l" else self.background_width-1100)

class b_classic(fallingSoldierBattle):
    '''经典模式;融合多种玩法的战斗模式'''
    def init(self):
        super().init()
        self.all_soldiers = ["soldier", "bow_infantry"]
        self.all_spells = ["fire", "treatment"]

    def getdelta(self):
        return 8000
    
    def update(self):
        if "golem" not in self.all_soldiers and self.period > 1:
            self.all_soldiers += ["cannon", "light_cavalry", "golem"]
            
        now = self.timer
        
        if now - self.last_falling > 8000:
            for i in range(5):
                spell = random.choice(self.all_spells)
                self.add_spell(spell, "l", (random.randint(0, self.background_width),
                                             random.randint(self.action_bar_height, HEIGHT)))
                self.add_spell(spell, "r", (random.randint(0, self.background_width),
                                             random.randint(self.action_bar_height, HEIGHT)))
        super().update()
        
    def add_soldier(self, name, camp, road, startswith="c_", money=0):
        sprite = super().add_soldier(name, camp, road, startswith, money)

        if self.period > 1 and "master" not in name:
            inf = float("inf")
            sprite.do_increase("speed", 0.5, inf)
            sprite.do_increase("attack_delta", -0.3, inf)
            sprite.do_increase("frame_delta", -0.3, inf)
            if name != "barricade":
                sprite.cover_color((255, 0, 255, 80), inf)

        return sprite
    
class b_double_energy(Battle):
    '''双倍能量对战;获得能量的速度翻倍'''
    def init(self):
        super().init()
        self.money_got[1] *= 2

class b_energy_party(fallingSoldierBattle):
    '''能量狂欢;获得能量的速度翻倍，每经过10秒双方各自派出一排能量精灵'''
    def init(self):
        super().init()
        self.difficulty += 0.001
        self.money_got[1] *= 2
        self.all_soldiers = ["energy_sprite"]

    def getdelta(self):
        return 10000
    
class b_falling_barbarian(fallingSoldierBattle):
    '''蛮兵入侵;每过一段时间，双方各自派出一排野蛮人士兵，蛮兵具有比普通士兵更强的战斗力'''
    def init(self):
        super().init()     
        self.period_events[2][1] = "倒计时180秒  野蛮象兵加入战场"
        self.all_soldiers = ["cs_barbarian_soldier", "cs_barbarian_bow_infantry",
                             "cs_barbarian_light_dagger_infantry"]

    def update(self):
        if "elephant_rider" not in self.all_soldiers and self.period > 1:
            self.all_soldiers.append("elephant_rider")
            
        super().update()
            
class b_falling_bomb(fallingSpellBattle):
    '''随机轰炸模式;每过一段时间，战场上就会落下20颗霹雳弹'''
    def init(self):
        super().init()
        self.all_spells = ["bomb"]

    def getdelta(self):
        return 8000 - set_threshold(self.period, 0, 3) * 1000
        
class b_falling_catapult(fallingSoldierBattle):
    '''战斗机器世界;每经过25秒，双方各自派出一排攻城弩、投石车、加农炮或黄金加农炮'''
    def init(self):
        super().init()
        self.all_soldiers = ["ballista", "catapult", "cannon", "gold_cannon"]

    def getdelta(self):
        return 25000

class b_falling_clone(fallingSpellBattle):
    '''克隆战场;每过一段时间，随机克隆20个区域'''
    def init(self):
        super().init()
        self.all_spells = ["clone"]
        
class b_falling_freeze_fire(fallingSpellBattle):
    '''冰火二重天;每过一段时间，随机冰冻或燃烧10个区域'''
    def init(self):
        super().init()

        self.all_spells = ["freeze", "fire"]
        self.count = 5
    
class b_falling_soldiers(fallingSoldierBattle):
    '''战斗乐园;每过一段时间，双方各自派出一排战兵、弓箭手、盾兵、矛兵或超级士兵'''
    def init(self):
        super().init()

        self.all_soldiers = ["soldier", "bow_infantry", "shielded_sword_infantry",
                             "elite_spear_infantry", "dragon_infantry"]

class b_falling_masters(fallingSoldierBattle):
    '''法师派对;每过一段时间，双方各自派出一排雷电法师、寒冰法师或飓风法师'''
    def init(self):
        super().init()

        self.all_soldiers = ["lightning_master", "ice_master", "wind_master"]

    def getdelta(self):
        return 14000 - set_threshold(self.period, 0, 2) * 2000

class b_fog_battle(fallingSpellBattle):
    '''迷雾之地;远程攻击类兵种精准度变差，且会定时落下闪电'''
    def init(self):
        super().init()
        self.all_spells = ["thunder"]

        self.mm.stop()
        self.mm = MusicManager(music_formats=["_spooky"])
        pg.mixer.music.set_volume(0.6)

        self.battle_projectile_offset = "uniform(0.75, 1.01)"
        
        surf = pg.Surface((self.background_width, HEIGHT)).convert_alpha()
        surf.fill((128, 0, 128, 100))
        self.background.blit(surf, (0, 0))

        self.fog_image = load_image("bg_dec_fog.png").convert_alpha()
        
    def draw(self):
        super().draw()
        self.screen.blit(self.fog_image, self.pos(0, self.action_bar_height))

class b_mirror_battle(Battle):
    '''镜像对战;在战场上派出士兵时，会在对称的一路派出相同的士兵'''
    def add_soldier(self, name, camp, road, startswith="c_", money=0):
        if startswith == "c_":
            super().add_soldier(name, camp, self.maxroad - road)
        return super().add_soldier(name, camp, road, startswith, money)
    
class b_rage_battle(Battle):
    '''狂暴对战;所有士兵（除法师）将持续处于狂暴状态'''
    def init(self):
        super().init()

        surf = pg.Surface((self.background_width, HEIGHT)).convert_alpha()
        surf.fill((255, 0, 255, 30))
        self.background.blit(surf, (0, 0))
        
    def add_soldier(self, name, camp, road, startswith="c_", money=0):
        sprite = super().add_soldier(name, camp, road, startswith, money)

        if "master" not in name:
            inf = float("inf")
            sprite.do_increase("speed", 0.5, inf)
            sprite.do_increase("attack_delta", -0.3, inf)
            sprite.do_increase("frame_delta", -0.3, inf)
            if name != "barricade":
                sprite.cover_color((255, 0, 255, 80), inf)

        return sprite            

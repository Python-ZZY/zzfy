from base import *
from configs import *

class cs_barbarian_bow_infantry(soldierUnit):
    def __init__(self, camp, imgkw):
        super().__init__(None, "_b_falling_barbarian1", 0, 0, 1.3, 2, 70, camp, imgkw)
        self.be_col = -15

    @remote("arrow.png", 9, 1000, wait=True)
    def attack(self, sprite):
        play_sound("projectile_move")
        return True

class cs_barbarian_light_dagger_infantry(soldierUnit):
    def __init__(self, camp, imgkw):
        super().__init__(None, "_b_falling_barbarian2", 0, 0, 2.5, 4, 80, camp, imgkw, frame_delta=50)
        
        self.rushing = False

    def call(self):
        if self.state != "attack":
            for sprite in self.sprites:
                if sprite.camp != self.camp and 180 < abs(sprite.rect.x - self.rect.x) < 220:
                    self.do_increase("speed", 2, 1000)
                    self.rushing = True
                    break

    @melee(5, 330, wait=True)
    def attack(self, sprite):
        if self.rushing:
            play_sound("rushing")
            sprite.do_stun(self.rand("randint(1000, 1300)"))
            sprite.take_damage(25, self)
            self.rushing = False
            self.clear_increase("speed")
        return True
    
class cs_barbarian_soldier(soldierUnit):
    def __init__(self, camp, imgkw):
        super().__init__(None, "_b_falling_barbarian3", 0, 0, 1.7, 3, 90, camp, imgkw)

    @melee(9, 900)
    def attack(self, sprite):
        play_sound("melee_att")
        return True
    
class cs_barricade(soldierUnit):
    def __init__(self, camp, imgkw):
        super().__init__(None, "_barricade", 0, 0, 0, 0, 400, camp, imgkw)

    def call(self):
        self.sprites = self.battle.soldiers[self.road-1].sprites() + \
                       self.battle.soldiers[self.road].sprites()

    @melee(10, 1000, wait=True, maxtarget=20)
    def attack(self, sprite):
        return True

    def mutiny(self):
        self.kill()

class c_ballista(soldierUnit):
    '''攻城弩只能攻击较远的目标'''
    def __init__(self, camp, imgkw):
        super().__init__(800, "攻城弩", 46, 11000, 1, 9, 130, camp, imgkw)

    @remote("ballista_bolt.png", 10, 400, wait=True, dist=1000)
    def attack(self, sprite):
        if abs(sprite.rect.x - self.rect.x) > 200:
            play_sound("projectile_move")
            return True
    
class c_bow_infantry(soldierUnit):
    '''弓箭手可以远程攻击目标'''
    def __init__(self, camp, imgkw):
        super().__init__(0, "弓箭手", 8, 3500, 1, 1, 60, camp, imgkw)
        self.be_col = -15

    @remote("arrow.png", 8, 1000, wait=True)
    def attack(self, sprite):
        play_sound("projectile_move")
        return True

class cs_bomb_cannon(spellUnit):
    def __init__(self, camp):
        super().__init__(550, "_cannon", 12, 20000, "single", (130, 130), (100, 0, 0), camp)

        self.call_delta = 0
        self.allow_barricade = True
        self.playing_effect = False

    def attack(self):
        self.battle.play_effect(self.add_pos, "bomb{}.png", sound=True)
        for sprite in self.enemy_sprites:
            sprite.take_damage(self.rand("randint(20, 27)"), self)
            
class c_cannon(soldierUnit):
    '''加农炮可以发射炮弹，炸到多路的目标'''
    def __init__(self, camp, imgkw):
        super().__init__(250, "加农炮", 32, 11000, 1, 9, 120, camp, imgkw, whole_delta=1200)

    def kill_effect(self, projectile):
        self.battle.add_spell("bomb_cannon", self.camp, projectile.rect.center, startswith="cs_")
        
    @remote("cannon_ball.png", 0, 2000, wait=True, dist=600)
    def attack(self, sprite):
        play_sound("projectile_move")
        return True

class c_gold_cannon(soldierUnit):
    '''黄金加农炮是加农炮的升级版，攻速更快，但不能攻击较近目标'''
    def __init__(self, camp, imgkw):
        super().__init__(900, "黄金加农炮", 50, 11000, 1.1, 9, 130, camp, imgkw, whole_delta=400)

    def kill_effect(self, projectile):
        self.battle.add_spell("bomb_cannon", self.camp, projectile.rect.center, startswith="cs_")
        
    @remote("gold_cannon_ball.png", 0, 1000, wait=True, dist=600)
    def attack(self, sprite):
        if abs(sprite.rect.x - self.rect.x) > 100:
            play_sound("projectile_move")
            return True
        
class c_catapult(soldierUnit):
    '''投石车只能攻击较远的目标，但投出的石块可以伤害多个目标'''
    def __init__(self, camp, imgkw):
        super().__init__(50, "投石车", 50, 11000, 1, 9, 130, camp, imgkw, whole_delta=1200)
            
    @remote("catapult_rock.png", 50, 2000, wait=True, dist=1400, maxtarget=6)
    def attack(self, sprite):
        if abs(sprite.rect.x - self.rect.x) > 200:
            play_sound("projectile_move")
            return True

class c_crossbow_infantry(soldierUnit):
    '''弩兵攻速极快'''
    def __init__(self, camp, imgkw):
        super().__init__(500, "弩兵", 24, 13000, 2, 2, 70, camp, imgkw, frame_delta=50)

    @remote("arrow.png", 9, 400, dist=250)
    def attack(self, sprite):
        play_sound("projectile_move")
        return True

class c_demon(soldierUnit):
    '''火焰魔龙可以灼伤多个目标，死后会掉落燃烧法术'''
    def __init__(self, camp, imgkw):
        super().__init__(150, "火焰魔龙", 16, 8000, 2.2, 3, 80, camp, imgkw, frame_delta=80)
        self.be_col = -20
        
    @melee(8, 500, wait=True, dist=50, maxtarget=5)
    def attack(self, sprite):
        self.play_effect("fire_attack{}.png", offset=10, sound=True)
        return True

    def die(self):
        self.battle.add_spell("fire", self.camp, self.rect.center)
        return True
    
class c_dragon_infantry(soldierUnit):
    '''对目标造成伤害后，伤害会进行累加'''
    def __init__(self, camp, imgkw):
        super().__init__(500, "超级士兵", 16, 10000, 2, 3, 80, camp, imgkw, frame_delta=80)

        self.damage_increase = 0

    @melee(4, 500, wait=True)
    def attack(self, sprite):
        play_sound("melee_att")
        if self.damage_increase < 50:
            self.damage_increase += 1
        sprite.take_damage(self.damage_increase, self)
        return True
    
class c_elephant_rider(soldierUnit):
    '''象兵血量极厚，并且可以反弹一部分伤害'''
    def __init__(self, camp, imgkw):
        super().__init__(300, "野蛮象兵", 44, 12000, 1.4, 7, 230, camp, imgkw)
        self.first = True

    def call(self):
        if self.first:
            self.first = False
            play_sound("elephant_rider_arrive")
        
    @melee(30, 750, wait=True)
    def attack(self, sprite):
        play_sound("melee_att")
        return True

    def take_damage(self, damage, actor):
        self.health -= damage
        damage = damage*0.3*(self.health/self.maxhealth)
        if damage != 0:
            actor.take_damage(damage, self)
        self.update_health_bar(actor)

class c_elite_spear_infantry(soldierUnit):
    '''长矛战兵可以同时攻击2个敌人'''
    def __init__(self, camp, imgkw):
        super().__init__(0, "长矛战兵", 10, 6500, 1.1, 3, 80, camp, imgkw, frame_delta=150)
        self.be_col = -55
    
    @melee(12, 1000, dist=-5, maxtarget=2)
    def attack(self, sprite):
        play_sound("melee_att")
        return True

class c_energy_sprite(soldierUnit):
    '''能量精灵攻击时有概率会产生1点能量'''
    def __init__(self, camp, imgkw):
        super().__init__(800, "能量精灵", 15, 10000, 1.2, 1, 60, camp, imgkw)
        self.be_col = -15

    @remote("arrow.png", 9, 1000, wait=True)
    def attack(self, sprite):
        if self.rand("random()") > 0.7:
            play_sound("get_energy")
            self.play_effect("get_energy{}.png", offset=-32, frame_delta=100)
            self.battle.add_money(self.camp, 1)
        play_sound("projectile_move")
        return True
    
class c_ice_master(soldierUnit):
    '''寒冰法师可以冻结敌人'''
    def __init__(self, camp, imgkw):
        super().__init__(700, "寒冰法师", 20, 13000, 1.4, 2, 60, camp, imgkw)

    def bullet_effect(self, projectile, sprite):
        stun = self.rand("randint(200, 500)")
        sprite.cover_color((0, 255, 255, 100), stun)
        sprite.do_stun(stun)
        
    @remote("snowball.png", 6, 700, dist=350)
    def attack(self, sprite):
        play_sound("projectile_move")
        return True

class c_golem(soldierUnit):
    '''傀儡石怪死后会变成一个较小石怪，伤害和血量为原来的一半'''
    def __init__(self, camp, imgkw):
        super().__init__(750, "傀儡石怪", 29, 9000, 1.5, 5, 120, camp, imgkw)
        
    @melee(12, 700, wait=True, maxtarget=5)
    def attack(self, sprite):
        if self.others.get("no_split"):
            sound = load_sound("assets/earthquake.ogg")
            sound.set_volume(0.5)
            sound.play()
        else:
            sprite.take_damage(12, self)
            play_sound("earthquake")
        return True

    def _split_self_scale(self, img):
        return pg.transform.scale(img, (img.get_width()*2//3, img.get_height()*2//3))

    def die(self):
        if not self.others.get("no_split"):
            rect_b = self.rect.copy()
            self.enum_images(self._split_self_scale)
            self.rect = self.now_image.get_rect()
            self.moveto("midbottom", (rect_b.centerx-10, rect_b.bottom))
            self.damage = 1
            self.health = self.maxhealth = 60
            self.others["no_split"] = True
            self.update_health_bar(None)
            return False
        return True
    
class c_good_light_cavalry(soldierUnit):
    '''轻骑兵中的精锐'''
    def __init__(self, camp, imgkw):
        super().__init__(900, "轻骑兵精锐", 44, 12000, 1.8, 6, 150, camp, imgkw)
        
        self.last_attack = self.battle.timer

    def call(self):
        if self.now - self.last_attack > 3500: #冲锋
            self.speed = 3.7
        else:
            self.speed = 1.8

    def clear(self):
        self.last_attack = self.now
        self.speed = 1.8
        
    @melee(40, 800)
    def attack(self, sprite):
        play_sound("melee_att")
        if self.speed == 3.7:
            play_sound("rushing")
            sprite.take_damage(100, self)
            self.clear()
            return False
        return True

class c_light_cavalry(soldierUnit):
    '''轻骑兵冲击敌人时造成大量伤害'''
    def __init__(self, camp, imgkw):
        super().__init__(0, "轻骑兵", 27, 9000, 1.8, 5, 120, camp, imgkw)
        
        self.last_attack = self.battle.timer

    def call(self):
        if self.now - self.last_attack > 5000: #冲锋
            self.speed = 3.5
        else:
            self.speed = 1.8

    def clear(self):
        self.last_attack = self.now
        self.speed = 1.8
        
    @melee(30, 1000)
    def attack(self, sprite):
        play_sound("melee_att")
        if self.speed == 3.5:
            play_sound("rushing")
            sprite.take_damage(80, self)
            self.clear()
            return False
        return True

class c_light_dagger_infantry(soldierUnit):
    '''刺客行动速度极快，冲撞敌人时产生眩晕效果'''
    def __init__(self, camp, imgkw):
        super().__init__(150, "刺客", 12, 6000, 2.5, 3, 70, camp, imgkw, frame_delta=50)
        
        self.rushing = False

    def call(self):
        if self.state != "attack":
            for sprite in self.sprites:
                if sprite.camp != self.camp and 150 < abs(sprite.rect.x - self.rect.x) < 180:
                    self.do_increase("speed", 2, 1000)
                    self.rushing = True
                    break

    @melee(4, 350, wait=True)
    def attack(self, sprite):
        if self.rushing:
            play_sound("rushing")
            sprite.do_stun(self.rand("randint(900, 1000)"))
            sprite.take_damage(20, self)
            self.rushing = False
            self.clear_increase("speed")
        return True

class c_lightning_master(soldierUnit):
    '''雷电法师会对敌人造成穿透伤害，并且可以造成眩晕效果'''
    def __init__(self, camp, imgkw):
        super().__init__(800, "雷电法师", 14, 12000, 1.6, 2, 60, camp, imgkw)

        self.effect_sprites = pg.sprite.Group()

    def draw(self):
        for sprite in self.effect_sprites:
            exec(f"sprite.rect.{'midleft' if self.camp=='l' else 'midright'} = self.rect.center")
            
        soldierUnit.draw(self)
        
    @melee(9, 700, dist=200, maxtarget=20)
    def attack(self, sprite):
        play_sound("lightning_master_att")
        
        sprite.do_stun(self.rand("randint(140, 160)"))
        eff = self.play_effect("lightning{}.png")
        self.effect_sprites.add(eff)
        
        return True

class c_meteor_hammer_infantry(soldierUnit):
    '''流星锤武士攻击时有概率击晕敌人'''
    def __init__(self, camp, imgkw):
        super().__init__(50, "流星锤武士", 14, 8000, 2, 3, 80, camp, imgkw)
        self.be_col = -15

    @melee(9, 750, wait=True, maxtarget=3)
    def attack(self, sprite):
        play_sound("melee_att")
        sprite.do_stun(self.rand("choice([10, 100, 500, 2000])"))
        
        return True
    
class c_minotaur(soldierUnit):
    '''牛头怪力量强大，每次攻击有概率暴击，伤害翻倍'''
    def __init__(self, camp, imgkw):
        super().__init__(100, "牛头怪", 13, 5000, 1.5, 3, 90, camp, imgkw)

    @melee(11, 1000)
    def attack(self, sprite):
        play_sound("melee_att")
        if self.rand("random()") > 0.6:
            sprite.take_damage(9, self)
            
        return True
    
class cs_skeleton(soldierUnit): #可以被king召唤出来
    def __init__(self, camp, imgkw):
        super().__init__(None, "_king", 0, 0, 1.7, 1, 65, camp, imgkw, frame_delta=150)

    @melee(9, 1000, wait=True)
    def attack(self, sprite):
        return True
    
class c_king(soldierUnit):
    '''国王在攻击时会定期召唤一批士兵'''
    def __init__(self, camp, imgkw):
        super().__init__(0, "国王", 18, 11000, 0.9, 7, 80, camp, imgkw)

    @melee(0, 3000, dist=500)
    def attack(self, sprite):
        unit = self.battle.add_soldier("skeleton", self.camp, self.road, startswith="cs_")
        unit.moveto("centerx", self.rect.centerx)
        
        return True

class c_shielded_sword_infantry(soldierUnit):
    '''盾兵有概率免疫伤害'''
    def __init__(self, camp, imgkw):
        super().__init__(200, "盾兵", 10, 3000, 1.5, 3, 90, camp, imgkw)

    @melee(10, 850, wait=True)
    def attack(self, sprite):
        play_sound("melee_att")
        return True

    def take_damage(self, damage, actor):
        if actor.unittype == "soldier" and self.rand("random()") > 0.7:
            return
        
        soldierUnit.take_damage(self, damage, actor)
        
class c_super_infantry(soldierUnit):
    '''狂暴主宰伤害较高，死后会掉落狂暴法术'''
    def __init__(self, camp, imgkw):
        super().__init__(700, "狂暴主宰", 24, 10000, 2, 8, 100, camp, imgkw, frame_delta=80)

    def die(self):
        self.battle.add_spell("rage", self.camp, self.rect.center)
        return True
    
    @melee(13, 500, wait=True, maxtarget=2)
    def attack(self, sprite):
        play_sound("melee_att")
        return True

class c_soldier(soldierUnit):
    '''普普通通的士兵'''
    def __init__(self, camp, imgkw):
        super().__init__(0, "战兵", 5, 2000, 2, 2, 75, camp, imgkw)

class c_wind_master(soldierUnit):
    '''飓风法师召唤的飓风对敌兵造成一定伤害，同时可以治疗己方的士兵'''
    def __init__(self, camp, imgkw):
        super().__init__(900, "飓风法师", 17, 12000, 1.3, 2, 70, camp, imgkw)

    def bullet_effect(self, projectile, sprite):
        rect = pg.Rect(sprite.rect.centerx - 65, sprite.rect.centery - 65, 130, 130)
        for sprite in self.sprites:
            if sprite.camp == self.camp and sprite.rect.colliderect(rect):
                sprite.restore_health(self.rand("randint(1, 7)"))
        
    @remote("wind_master_att{}.png", 6, 800, dist=250, maxtarget=3, nogravity=3, anchor=("bottom", "bottom"))
    def attack(self, sprite):
        play_sound("projectile_move")
        return True
        
class c_zombie(soldierUnit):
    '''杀死的目标会成为亡魂，供己方作战'''
    def __init__(self, camp, imgkw):
        super().__init__(600, "僵尸", 16, 11000, 2, 3, 90, camp, imgkw)

    @melee(10, 500, wait=True)
    def attack(self, sprite):
        if sprite.health - 10 <= 0:
            sprite.health = 1
            sprite.health_bar = None
            sprite.mutiny()
        else:
            play_sound("melee_att")
            return True
            
class c_bomb(spellUnit):
    '''造成较高的伤害，同时产生眩晕'''
    def __init__(self, camp):
        super().__init__(550, "霹雳弹", 13, 20000, "single", (130, 130), (100, 0, 0), camp)

        self.call_delta = 200

    def attack(self):
        for sprite in self.enemy_sprites:
            sprite.take_damage(self.rand("randint(40, 60)"), self)
            sprite.do_stun(self.rand("randint(0, 3000)"))

class c_clone(spellUnit):
    '''克隆范围内的士兵，但是克隆后的士兵血量较低'''
    def __init__(self, camp):
        super().__init__(900, "克隆法术", 10, 17000, "single", (180, 180), (0, 0, 200), camp)
        self.playing_effect = False

    def attack(self):
        play_sound("clone")
        for sprite in self.player_sprites:
            if not sprite.others.get("clone"):
                soldier = sprite.unit_copy()
                soldier.moveto("centerx", self.add_pos[0] * 2 - sprite.rect.centerx)
                soldier.maxhealth = soldier.health = 1
                soldier.cover_color((0, 0, 255, 100), float("inf"))
                soldier.damage = 1
                soldier.others["clone"] = True

class c_fire(spellUnit):
    '''对范围内敌人造成持续伤害'''
    def __init__(self, camp):
        super().__init__(0, "燃烧法术", 8, 9500, "repeated", (150, 150), (255, 0, 0), camp)
        self.frame_delta = 250
        self.attack_time = 3750

    def call(self):
        play_sound("fire")
        
    def attack(self):
        for sprite in self.enemy_sprites:
            sprite.take_damage(2, self)
            sprite.do_increase("speed", -1)
            
class c_freeze(spellUnit):
    '''使范围内敌人被冻住，无法移动或攻击'''
    def __init__(self, camp):
        super().__init__(800, "冰冻法术", 9, 20000, "repeated", (200, 200), (0, 255, 255), camp)
        
        self.attack_delta = 50
        self.attack_time = 5000
        self.update_sprites_single = True

    def attack(self):
        for sprite in self.enemy_sprites:
            sprite.do_stun(150)

class c_thunder(spellUnit):
    '''打断敌人的行动并造成较小伤害'''
    def __init__(self, camp):
        super().__init__(100, "闪电法术", 4, 3000, "single", (55, 115), (160, 160, 210), camp)

        self.call_delta = 100

    def call(self):
        play_sound("thunder")
        
    def attack(self):
        for sprite in self.enemy_sprites:
            sprite.take_damage(self.rand("randint(0, 5)"), self)
            sprite.do_stun(self.rand("randint(200, 800)"))
        
class c_wind(spellUnit):
    '''使范围内敌人被飓风卷到中心'''
    def __init__(self, camp):
        super().__init__(0, "飓风法术", 8, 7500, "repeated", (400, 200), (255, 255, 255), camp)
        
        self.attack_delta = 12
        self.attack_time = 2000
        self.playing_effect = False

    def call(self):
        play_sound("wind")
        
    def attack(self):
        for sprite in self.enemy_sprites:
            sprite.do_increase("speed", -sprite.speed)
            sprite.do_stun()
            sprite.take_damage(0.05, self)
            if sprite.rect.centerx > self.add_pos[0]:
                sprite.move("x", -1.5)
            elif sprite.rect.centerx < self.add_pos[0]:
                sprite.move("x", 1.5)
            
class c_rage(spellUnit):
    '''使己方士兵移动和攻击速度加快'''
    def __init__(self, camp):
        super().__init__(550, "狂暴法术", 8, 12000, "repeated", (300, 200), (255, 0, 255), camp)

        self.attack_delta = 20
        self.attack_time = 4000
        self.playing_effect = False

    def attack(self):
        for sprite in self.player_sprites:
            sprite.do_increase("speed", 0.5, 1000)
            sprite.do_increase("attack_delta", -0.3, 1000)
            sprite.do_increase("frame_delta", -0.3, 1000)
            sprite.cover_color((255, 0, 255, 100), 1000)

class c_treatment(spellUnit):
    '''对己方士兵产生治疗效果'''
    def __init__(self, camp):
        super().__init__(20, "治疗法术", 10, 9000, "single", (200, 190), (0, 255, 0), camp)

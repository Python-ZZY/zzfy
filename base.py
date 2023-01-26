import pygame as pg
import math
import sys
from configs import *

class Scene:
    def __init__(self, screen=None, caption=None, icon=None, bg=(0, 0, 0),
                 fps=60, loop=True):
        self.screen = screen if screen else pg.display.get_surface()
        self.bg = bg
        self.fps = fps

        self.clock = pg.time.Clock()
        self.scene_running = False
        
        if caption:
            pg.display.set_caption(caption)
        if icon:
            pg.display.set_icon(icon)

        self.init()
        if loop:
            self.loop()

    def init(self):
        pass

    def loop(self):
        self.scene_running = True
        
        while self.scene_running:
            self.screen.fill(self.bg)
            self.update()
            self.draw()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.onexit()
                self.events(event)
            self.draw2()
            
            self.clock.tick(self.fps)

            pg.display.update()

    def onexit(self):
        self.quit_scene()
        
    def quit_scene(self):
        self.scene_running = False

    def draw(self):
        pass

    def draw2(self):
        pass
    
    def update(self):
        pass

    def events(self, event):
        pass
                
    def wait_event(self, update=None, key=True, mouse=True):
        if not update:
            update = self.draw
            
        running = True
        while running:
            self.screen.fill(self.bg)
            update()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    self.quitscene()
                elif event.type == pg.KEYUP and key:
                    running = False
                    return event.key
                elif event.type == pg.MOUSEBUTTONUP and mouse:
                    running = False
                    return event.pos
                
            self.clock.tick(self.fps)
            pg.display.update()

    def play_effect(self, pos, name, sound=False, frame_delta=100, kill_after_play=1,
                    anchor="center", sprites=None, **kw):
        sprite = Dynamic(0, 0, {"":name}, frame_delta=frame_delta,
                         kill_after_play=kill_after_play, **kw)
        exec(f"sprite.rect.{anchor} = pos")
        
        if sprites != None:
            sprites.add(sprite)
        else:
            self.effect_sprites.add(sprite)

        if sound:
            play_sound(name.split("{")[0])

        return sprite

    def fade_out(self, decrease=15, background=None, draw=None, alpha=0):
        if not draw:
            draw = self.draw
            
        alpha = alpha
        
        screenrect = self.screen.get_rect()
        if not background:
            background = pg.Surface((screenrect.width, screenrect.height)).convert_alpha()
            background.fill(self.bg)
        
        while True:
            draw()
            self.screen.blit(background, (0, 0))
            background.set_alpha(alpha)
            alpha += decrease
            if alpha >= 500:
                break

            pg.event.get()
            self.clock.tick(self.fps)
            pg.display.update()
            
class Dynamic(pg.sprite.Sprite):
    def __init__(self, x, y, imgs, state=None, frame_delta=100, whole_delta=0, kill_after_play=False,
                 mark=None, call_after_kill=None, imgkw={}):
        super().__init__()

        self.imgs = {k:load_images(v, **imgkw.get(k, {})) for k, v in imgs.items()}
        self.frame_delta = frame_delta
        self.whole_delta = whole_delta
        self.lasttime = whole_delta
        self.played = 0
        self.state = None
        self.kill_after_play = kill_after_play
        self.call_after_kill = call_after_kill
        self.mark = mark
        self.init_special_image()

        if self.mark:
            setattr(*self.mark, 1)
            
        if state is None:
            self.cstate(tuple(self.imgs.keys())[0], x, y)
        else:
            self.cstate(state, x, y)

    def init_special_image(self):
        self.HIDE = pg.Surface((0, 0))

    @property
    def now_image(self):
        return self.imgs[self.state][self.anmidx]
        
    def animate(self, flip=None):
        if self.state == "HIDE":
            self.image = self.HIDE
            return
        
        now = pg.time.get_ticks()
        if now - self.lasttime > self.frame_delta:
            self.lasttime = now

            self.image = self.now_image
            if flip:
                self.image = pg.transform.flip(self.image, *flip)

            if self.mark and (not hasattr(*self.mark)):
                self.kill()
                
            self.anmidx += 1
            if self.anmidx == len(self.imgs[self.state]):
                self.anmidx = 0

                if self.whole_delta:
                    self.lasttime += self.whole_delta
                    self.image = self.imgs[self.state][self.anmidx]
                    if flip:
                        self.image = pg.transform.flip(self.image, *flip)

                if self.kill_after_play:
                    self.played += 1
                    if self.played == self.kill_after_play:
                        if self.mark:
                            delattr(*self.mark)
                        if self.call_after_kill:
                            self.call_after_kill(self)
                        self.kill()
            
    def cstate(self, state, x=None, y=None):
        if state != self.state:
            self.state = state
            self.anmidx = 0
            self.lasttime = 0
    
            if x != None and y != None:
                self.image = self.imgs[self.state][self.anmidx]
                self.rect = self.image.get_rect(x=x, y=y)

    def enum_images(self, func):
        for state, imgs in self.imgs.items():
            for i, img in enumerate(imgs):
                self.imgs[state][i] = func(img)
                
    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Static(pg.sprite.Sprite):
    def __init__(self, x, y, img, flip=None, pgim=False):
        super().__init__()

        if pgim:
            self.image = img
        else:
            self.image = load_image(img)

        if flip:
            self.image = pg.transform.flip(self.image, *flip)

        self.state = ""
        self.rect = self.image.get_rect(x=x, y=y)

    def draw(self, surf):
        if self.state != "HIDE":
            surf.blit(self.image, self.rect)

class FadeOutText(pg.sprite.Sprite):
    def __init__(self, text, color=(255, 255, 255), size=34, last=6000):
        super().__init__()

        self.image = render(text, color, size).convert_alpha()
        self.image.set_alpha(0)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.alpha = 0
        self.last = last
        self.last_to = None
        self.alive = True

    def update(self):
        if self.last_to:
            now = pg.time.get_ticks()
            if now > self.last_to:
                self.alive = False
                self.kill()
        else:
            self.alpha += 5
            self.image.set_alpha(self.alpha)
            if self.alpha >= 990:
                self.last_to = pg.time.get_ticks()

class Button(pg.sprite.Sprite):
    def __init__(self, group, center, image, tooltip, command, anchor="bottomright"):
        super().__init__(group)
        self.tooltip = tooltip
        self.anchor = anchor
        self.image = load_image(image)
        self.selected_image = pg.mask.from_surface(self.image.convert_alpha()).to_surface(
            setcolor=(0, 0, 0, 50),
            unsetcolor=(0, 0, 0, 0))
        self.rect = self.image.get_rect(center=center)
        self.command = command

    def update(self, screen, click, pos):
        screen.blit(self.image, self.rect)
        if self.rect.collidepoint(pos):
            screen.blit(self.selected_image, self.rect)
            if click:
                self.command()
            return True

def melee(damage, delta, wait=False, dist=-20, maxtarget=1, getdelta=None): #伤害 攻击间隔 首次攻击延迟
    if not getdelta:
        getdelta = lambda self: delta
        
    def decorator(attack):
        def func(self):
            target = 0
            saw_target = False
            for sprite in self.sprites:
                if sprite.unittype == "shell":
                    continue
                if self.col(sprite, dist) and sprite.camp != self.camp:
                    saw_target = True
                    if (self.now - self.last_wait) > (getdelta(self) * (1+self.increase["attack_delta"][0])):
                        if attack(self, sprite):
                            sprite.take_damage(damage, self)
                        
                        target += 1
                        if target >= maxtarget:
                            break

            if saw_target:
                if target:
                    self.last_attack = self.now
                    self.last_wait = self.now
                return True
            
            if wait:
                self.last_wait = self.now
            else:
                self.last_wait = self.last_attack
        
        return func
    return decorator

def remote(bullet, damage, delta, wait=False, dist=400, getdelta=None, **kw):
    if not getdelta:
        getdelta = lambda self: delta
        
    def decorator(attack):
        def func(self):
            for sprite in self.sprites:
                if sprite.unittype == "shell":
                    continue
                if self.col(sprite, dist) and \
                   sprite.camp != self.camp:
                    if (self.now - self.last_wait) > (getdelta(self) * (1+self.increase["attack_delta"][0])):
                        if attack(self, sprite):
                            self.last_attack = self.now
                            self.last_wait = self.now
                            eval(f"self.battle.{self.camp}_projectile_group.add(Projectile({repr(bullet)}, {repr(damage)}, "+\
                                 f"self, sprite, attack=(self.bullet_effect, self.kill_effect), **{kw}))")
                    return True
            if wait:
                self.last_wait = self.now
            else:
                self.last_wait = self.last_attack

        return func
    return decorator

class Projectile(Dynamic):
    def __init__(self, image, damage, shooter, target, maxtarget=1, nogravity=False,
                 anchor=("centery", "centery"), attack=(lambda *args: None, lambda *args: None),
                 road=None, **kw):
        self.battle = sys.stdout.battle
        self.en_name = self.unittype = "projectile"
        self.attack = attack

        self.damage = damage
        self.road = [shooter.road + i for i in road] if road else [shooter.road]
        self.background_width = shooter.battle.background_width
        self.maxtarget = maxtarget
        
        super().__init__(0, 0, {"":image}, **kw)
        self.original_image = self.image.copy()
        self.camp = shooter.camp
        if self.camp == "l":
            self.rect.x = shooter.rect.right + shooter.be_col
        else:
            self.rect.right = shooter.rect.x - shooter.be_col
        exec("self.rect.%s = shooter.rect.%s"%anchor)
        self.target_y = shooter.rect.centery

        self.nogravity = nogravity
        if self.nogravity:
            self.target_x = target.rect.centerx
            if self.camp == "r":
                self.nogravity = -nogravity
        else:
            self.gravity = 0.5

            x_dist = abs(shooter.rect.x - target.rect.x - target.be_col)
            y_dist = abs(self.rect.y - target.rect.y)
            if self.camp == "r":
                x_dist = -x_dist
                y_dist = -y_dist
            
            dist = (x_dist ** 2 + y_dist ** 2) ** 0.5 ** self.battle.rand(self.battle.battle_projectile_offset, self.camp) + 1
            self.x_vel = x_dist / dist * 20
            self.y_vel = -0.25 * abs(x_dist/20)

            self.set_orientation()

    def col(self, sprite):
        if self.camp == "l":
            colarea = pg.Rect((self.rect.x, self.rect.y, self.rect.width+sprite.be_col, self.rect.height))
        else:
            colarea = pg.Rect((self.rect.right-self.rect.width-sprite.be_col, self.rect.y,
                               self.rect.width+sprite.be_col, self.rect.height))

        if sprite.rect.colliderect(colarea):
            return True
        return False
    
    def take_damage(*args):
        pass
    
    def set_orientation(self):
        if self.x_vel == 0:
            self.x_vel = self.y_vel + 1
        angle = math.atan(-self.y_vel / self.x_vel) * 180 / math.pi
        if self.x_vel < 0:
            self.image = pg.transform.rotate(pg.transform.flip(self.original_image, True, False), angle)
        else:
            self.image = pg.transform.rotate(self.original_image, angle)

    def kill(self):
        self.attack[1](self)
        super().kill()
        
    def update(self):
        self.animate()

        if self.nogravity:
            self.rect.x += self.nogravity
        else:
            self.y_vel += self.gravity
            self.set_orientation()
            self.rect.x += self.x_vel
            self.rect.y += self.y_vel

        if (not 0 <= self.rect.centerx <= self.background_width) or (self.rect.y > self.target_y):
            self.kill()
        elif self.nogravity:
            if self.camp == "l" and self.rect.x > self.target_x:
                self.kill()
            elif self.camp == "r" and self.rect.right < self.target_x:
                self.kill()

def set_grey(image):
    image = image.convert_alpha()
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            c = image.get_at((x, y))
            color = sum(c[:3]) // 3
            image.set_at((x, y), (color, color, color, c[3]))
    return image
                
class UnitIcon(Dynamic):
    def __init__(self, unit, icon_rect):
        self.battle = sys.stdout.battle
        
        super().__init__(icon_rect.x, icon_rect.y, {"":unit.en_name+"_icon.png"})
        self.imgs[""][0] = set_grey(self.imgs[""][0])
        self.unittype = unit.unittype
        self.cost = unit.cost
        self.icon_rect = icon_rect
        self.maxfrozen = unit.maxfrozen
        #self.frozen_h = 0
        self.freeze()
        
    def can_buy(self, money):
        if money >= self.cost and self.now > self.frozen_to:
            return True
        
        return False

    def freeze(self):
        self.image_frozen = pg.Surface((65, 65)).convert_alpha()
        self.image_frozen.fill((0, 0, 0, 100))
        self.frozen_to = self.battle.timer + self.maxfrozen
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.now <= self.frozen_to:
            screen.blit(self.image_frozen, (self.icon_rect.x, self.icon_rect.y + 65 - self.frozen_h))
                    
    def update(self, money):
        self.now = self.battle.timer

        self.frozen_h = 64
        if self.now <= self.frozen_to:
            if self.maxfrozen:
                self.frozen_h = (self.frozen_to - self.now) * 65 // self.maxfrozen
            self.image_frozen = pg.transform.scale(self.image_frozen, (65, self.frozen_h))
        
        if self.can_buy(money):
            self.cstate("HIDE")
            self.animate()
        else:
            self.cstate("")
            self.animate()

class BaseUnit:
    def rand(self, expr):
        return self.battle.rand(expr, self.camp)

class soldierUnit(Dynamic, BaseUnit): #战斗人物卡牌
    def __init__(self, unlock_need, cn_name, cost, maxfrozen, speed, damage, maxhealth, camp, imgkw,
                 **kw):
        self.startswith = self.__class__.__name__.split("_")[0]
        self.en_name = "_".join(self.__class__.__name__.split("_")[1:])
        self.others = {}
        if not camp:
            sys.stdout.all_units[self.en_name] = (unlock_need, cn_name, cost, self.__doc__, "soldier",
                                                  maxfrozen, speed, damage, maxhealth)
            return

        self.unittype = "soldier"
        self.battle = sys.stdout.battle
        self.now = self.battle.timer
        
        self.camp = camp
        self.cn_name = cn_name
        
        self.health_bar = None # Hide at first
        self.health_bar_rect = None
        self.damage_list = pg.sprite.Group() #避免坠落物重复伤害士兵

        self.be_col = -5 #用于准确碰撞
        self.stun = 0 #眩晕
        self.color_cover = {}
        self.increase = {"speed":[0, 0], "attack_delta":[0, 0], "frame_delta":[0, 0]}
        self.last_attack = 0
        self.last_wait = 0

        self.cost = cost
        self.maxfrozen = maxfrozen #冷却时间
        self.speed = speed
        self.damage = damage #冲过敌阵造成的伤害
        self.maxhealth = self.health = maxhealth

        super().__init__(0, 0, {"walk":self.en_name+"_w{}.png",
                                "attack":self.en_name+"_a{}.png"}, imgkw=imgkw, **kw)

        self.position = pg.Vector2(0, 0)
        self.default_whole_delta = self.whole_delta
        self.lasttime = 0

    def animate(self, flip=None):
        if self.state == "HIDE":
            self.image = self.HIDE
            return
        
        now = pg.time.get_ticks()
        if now - self.lasttime > self.frame_delta * (1+self.increase["frame_delta"][0]):
            self.lasttime = now

            self.image = self.imgs[self.state][self.anmidx]
            if flip:
                self.image = pg.transform.flip(self.image, *flip)
            self.update_color_cover()

            if self.mark and (not hasattr(*self.mark)):
                self.kill()
                
            self.anmidx += 1
            if self.anmidx == len(self.imgs[self.state]):
                self.anmidx = 0

                if self.whole_delta:
                    self.lasttime += self.whole_delta * (1+self.increase["frame_delta"][0])
                    self.image = self.imgs[self.state][self.anmidx]
                    if flip:
                        self.image = pg.transform.flip(self.image, *flip)

                if self.kill_after_play:
                    self.played += 1
                    if self.played == self.kill_after_play:
                        if self.mark:
                            delattr(*self.mark)
                        if self.call_after_kill:
                            self.call_after_kill(self)
                        self.kill()
                        
    @property
    def direction(self):
        return 1 if self.camp == "l" else -1
        
    def move(self, direction, px):
        exec(f"self.position.{direction} += px")
        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def moveto(self, direction, pos):
        exec(f"self.rect.{direction} = pos")
        self.position.x = self.rect.x
        self.position.y = self.rect.y
        
    def col(self, sprite, dist=0):
        if self.camp == "l":
            colarea = pg.Rect((self.rect.x, self.rect.y, self.rect.width+dist+sprite.be_col, self.rect.height))
        else:
            colarea = pg.Rect((self.rect.right-self.rect.width-dist-sprite.be_col, self.rect.y,
                               self.rect.width+dist+sprite.be_col, self.rect.height))

        if sprite.rect.colliderect(colarea):
            return True
        return False

    def cover_color(self, color, last=50):
        self.color_cover[color] = self.now + last

    def update_color_cover(self):
        for color in self.color_cover:
            self.image = self.image.copy()
            self.image.blit(pg.mask.from_surface(self.image).to_surface(setcolor=color,
                                                                        unsetcolor=(0, 0, 0, 0)), (0, 0))
            
    def update_road(self, road, x=None):
        roadheight = self.battle.roadheight

        if x:
            self.rect.x = x
        else:
            if self.camp == "l":
                self.rect.x = 0
            else:
                self.rect.right = self.battle.background_width
        self.road = road
        self.rect.bottom = roadheight * (road+1) + self.battle.action_bar_height
        self.position.x = self.rect.x
        self.position.y = self.rect.y
        
        self.sprites = self.battle.soldiers[road]

    def update_health_bar(self, actor):
        if self.health == self.maxhealth:
            self.health_bar = None
            return
        
        if not self.health_bar:
            self.health_bar = pg.Surface((20, 2))
        self.health_bar.fill((255, 0, 0))
        pg.draw.rect(self.health_bar, (0, 255, 0), (0, 0, self.health/self.maxhealth*20, 2))

        if actor and actor.en_name == "projectile":
            self.damage_list.add(actor)
            
    def draw(self):
        self.battle.screen.blit(self.image, self.battle.pos(*self.rect.topleft))
        if self.health_bar:
            self.health_bar_rect = self.health_bar.get_rect(centerx=self.rect.centerx, bottom=self.rect.top-1)
            self.battle.screen.blit(self.health_bar, self.battle.pos(*self.health_bar_rect.topleft))

    def update(self):
        self.now = self.battle.timer
        self.call()

        if self.stun != 0 and self.now > self.stun:
            self.clear()
            self.stun = 0

        for key, (value, last_to) in self.increase.items():
            if self.now > last_to:
                self.increase[key] = [0, 0]

        for color, last_to in tuple(self.color_cover.items()):
            if self.now > last_to:
                del self.color_cover[color]
                
        if self.stun:
            self.cstate("walk")
        else:
            self.animate()
            att = self.attack()
            if att:
                self.whole_delta = self.default_whole_delta
                self.cstate("attack")
            elif self.walk():
                self.whole_delta = 0
                self.cstate("walk")

        if self.health <= 0:
            if self.die():
                self.kill()
                return

        if self.camp == "l":
            if self.rect.x > self.battle.background_width:
                self.battle.take_damage("r", self.damage)
                self.kill()
        else:
            if self.rect.right < 0:
                self.battle.take_damage("l", self.damage)
                self.kill()

    def call(self):
        pass

    def clear(self):
        '''Restore default state'''
        pass

    def bullet_effect(self, projectile, sprite):
        '''Only remote: what will happen when hitting target'''

    def kill_effect(self, projectile):
        '''Only remote: what will happen when killing'''
        
    @melee(6, 900)
    def attack(self, sprite):
        '''Check attacking. return True if attack'''
        play_sound("melee_att")
        return True

    def walk(self):
        '''Call when moving. return True if move'''
        self.move("x", (self.speed + self.increase["speed"][0]) * self.direction)

        return True

    def play_effect(self, name, offset=0, frame_delta=2, **kw):
        d = -1 if self.camp == "r" else 1
        return self.battle.play_effect(vec(self.rect.center)+vec(d*offset, 0), name,
                                       anchor="midleft" if self.camp=="l" else "midright",
                                       frame_delta=frame_delta, sprites=self.battle.low_effect_sprites,
                                       imgkw={} if self.camp == "l" else {"":{"flip":(True, False)}},
                                       **kw)

    def restore_health(self, point):
        self.health += point
        if self.health > self.maxhealth:
            self.health = self.maxhealth
        self.update_health_bar(None)
            
    def take_damage(self, damage, actor):
        '''Call when be damaged.'''
        self.health -= damage
        self.update_health_bar(actor)

    def unit_copy(self):
        return self.battle.add_soldier(self.en_name, self.camp, self.road,
                                       startswith=self.startswith+"_")
        
    def mutiny(self):
        self.camp = "r" if self.camp == "l" else "l"
        self.clear()

        for state in self.imgs:
            for i, image in enumerate(self.imgs[state]):
                self.imgs[state][i] = pg.transform.flip(image, True, False)

        self.anmidx = 0
        self.image = self.imgs[self.state][self.anmidx]

    def do_increase(self, key, value, last=250, postive=True):
        self.increase[key] = [value, self.now + last]
        if key == "speed" and postive and self.speed - value < 0:
            self.increase[key][0] = self.speed

    def clear_increase(self, key):
        self.increase[key] = [0, 0]
        
    def do_stun(self, last=1):
        self.update_color_cover()
        self.stun = self.now + last
        self.anmidx = 0
                
    def die(self):
        '''Call to check if die. return True if kill'''
        return True

class spellUnit(Static, BaseUnit): #法术卡牌
    def __init__(self, unlock_need, cn_name, cost, maxfrozen, spelltype, area, areacolor, camp):
        self.startswith = self.__class__.__name__.split("_")[0]
        self.en_name = "_".join(self.__class__.__name__.split("_")[1:])
        if not camp:
            sys.stdout.all_units[self.en_name] = (unlock_need, cn_name, cost, self.__doc__, "spell",
                                                  maxfrozen, area)
            return
        
        self.unittype = "spell"
        self.battle = sys.stdout.battle

        self.camp = camp
        self.cn_name = cn_name
        
        self.cost = cost
        self.maxfrozen = maxfrozen
        self.areacolor = areacolor
        self.spelltype = spelltype
        self.area = area

        self.update_sprites_single = False #只刷新一次碰撞精灵组
        self.call_delta = 600
        self.time_start_call = 0
        self.going = False
        self.playing_effect = True
        self.play_effect_delta = 600
        self.frame_delta = 30
        self.allow_barricade = False
        if spelltype == "repeated":
            self.call_to = 0
            self.last_attack = 0
            self.attack_delta = 250
            self.attack_time = 5000
            self.image_repeat_area = pg.Surface(self.area).convert_alpha()
            self.image_repeat_area.fill((*self.areacolor, 50))
            
        image = pg.Surface(self.area).convert_alpha()
        image.fill((*self.areacolor, 100))
        super().__init__(0, 0, image, pgim=True)

    def take_damage(*args):
        pass

    def go(self):
        self.going = True
        self.time_start_call = self.battle.timer + self.call_delta
        self.rect_collide = pg.Rect((self.rect.x, self.rect.y,
                                     self.rect.width, self.rect.height))
        pos = pg.mouse.get_pos()
        self.add_pos = self.rect.center
            
        if self.spelltype == "repeated":
            self.call_to = self.time_start_call + self.attack_time
            self.battle.repeated_spell.add(self)
            self.update_sprites()
        self.call()

    def update_sprites(self):
        self.player_sprites = pg.sprite.Group()
        self.enemy_sprites = pg.sprite.Group()
        for road in self.battle.soldiers:
            for unit in road:
                if unit.unittype == "soldier" and (self.allow_barricade or unit.en_name != "barricade"):
                    if self.rect_collide.colliderect(unit.rect):
                        if unit.camp == self.camp:
                            self.player_sprites.add(unit)
                        else:
                            self.enemy_sprites.add(unit)
        
    def update(self):
        now = self.battle.timer
        
        if self.going:
            if now > self.time_start_call:
                if self.playing_effect:
                    self.battle.play_effect(self.add_pos, self.en_name + "{}.png", frame_delta=self.frame_delta,
                                            whole_delta=self.play_effect_delta, sound=True)
                    self.playing_effect = False
                if self.spelltype == "single":
                    self.update_sprites()
                    self.attack()
                    self.kill()
                else:
                    if self.call_to > now:
                        if now - self.last_attack > self.attack_delta:
                            self.last_attack = now
                            if not self.update_sprites_single:
                                self.update_sprites()
                            self.attack()
                    else:
                        self.kill()
        else:
            pos = pg.mouse.get_pos()
            self.rect.center = pos

    def call(self):
        '''Call before going'''
        
    def attack(self):
        for sprite in self.player_sprites:
            sprite.restore_health(sprite.maxhealth * 0.1 + 50)

class GetItemEffect:
    def __init__(self, sprite, group, startpos, speed=5, command=lambda:...):
        group.add(sprite)
        sprite.center = startpos
        self.sprite = sprite
